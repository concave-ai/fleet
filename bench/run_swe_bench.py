import sys

from concave.internal.datasets.config import get_config_from_swe_bench
from concave.internal.workspace.manager import WorkspaceManager
from datasets import load_dataset
from loguru import logger

from fleet.agents.code_gen.code_gen import SymbolsEvaluate
from fleet.agents.searcher.file_evaluate import FileEvaluate, FileEvaluateReq
from fleet.agents.searcher.file_symbol_search import FileSymbolSearch, FilesSymbolSearchReq
from fleet.agents.searcher.files_filter import FilesFilter, FilesFilterReq
from fleet.agents.searcher.files_keyword_search import FilesKeywordSearch, FilesKeywordSearchReq
from fleet.agents.searcher.keyword_extract import KeywordExtract, KeywordExtractReq
from fleet.context import Context
from fleet.fst.fst import FST
from fleet.task.task import Task
from fleet.utils import unique_list


from loguru import logger
logger.remove()
logger.add(sys.stdout, level="INFO")




class SweBenchTask:
    def __init__(self, task_id):
        # task_id == instance_id , e.g. pytest-dev__pytest-5262
        self.task_id = task_id

    def get_test_rule_from_dataset(self):
        ds = load_dataset("princeton-nlp/SWE-bench_Verified")
        rows = ds.get("test")
        filter_rows = [row for row in rows if self.task_id in row["instance_id"]]
        if len(filter_rows) == 0:
            raise ValueError(f"Could not find {self.task_id} in SWE-bench_Verified")
        return filter_rows[0]

    def prepare_ctx(self):
        rule = self.get_test_rule_from_dataset()
        config = get_config_from_swe_bench(
            name=rule["instance_id"],
            repo=rule["repo"],
            version=rule["version"],
            base_commit=rule["base_commit"]
        )

        manager = WorkspaceManager()

        ctx = Context(
            task_id=self.task_id,
            model="gpt-4o-mini",
            # model="gpt-4o-2024-08-06",
        )
        ctx.workspace = manager.create(config)

        ctx.issue = f"<description>:{rule['problem_statement']}</description>"
        ctx.trace = True
        return ctx

    def start(self):
        ctx = self.prepare_ctx()

        logger.info(f"task_id: {self.task_id}")
        logger.info(f"model: {ctx.model}")
        logger.info(f'Workspace created: {ctx.workspace.id()}')

        with Task(ctx) as task:
            # TODO: write a tool in concave to get tokens
            with open("/Users/justwph/labs/hackathons/2024/concave/tests/code_search/tokens.txt") as f:
                repo_tokens = f.read()

            key_extract_res = task.run(KeywordExtract, req=KeywordExtractReq(repo_tokens=repo_tokens.split("\n")))
            key_search_res = task.run(FilesKeywordSearch, req=FilesKeywordSearchReq(tokens=key_extract_res.keywords))
            files_filter_res = task.run(FilesFilter, req=FilesFilterReq(keyword_search_results=key_search_res.results))

            file_paths = unique_list(files_filter_res.file_paths)[:4]
            files = []

            for file_path in file_paths:
                res = task.run(FileEvaluate, req=FileEvaluateReq(file_path=file_path))
                files.append({
                    "file_path": file_path,
                    "relevant_symbol_keys": res.relevant_symbols,
                    "root_cause_symbol_keys": res.root_cause_symbols
                })
            symbols = task.run(FileSymbolSearch, req=FilesSymbolSearchReq(files=files))

            res = task.run(SymbolsEvaluate, req=symbols)


def get_all_pytest_ids():
    ds = load_dataset("princeton-nlp/SWE-bench_Verified")
    rows = ds.get("test")
    return [row["instance_id"] for row in rows if "pytest" in row["instance_id"]]


if __name__ == "__main__":
    for swe_bench_id in get_all_pytest_ids():
        task = SweBenchTask(swe_bench_id)
        task.start()

    # task = SweBenchTask("pytest-dev__pytest-5262")
    # task.start()
