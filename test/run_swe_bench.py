import sys

from concave.internal.datasets.config import get_config_from_swe_bench
from concave.internal.workspace.manager import WorkspaceManager
from datasets import load_dataset
from loguru import logger

from fleet.agents.searcher.file_evaluate import FileEvaluate, FileEvaluateReq
from fleet.agents.searcher.files_filter import FilesFilter, FilesFilterReq
from fleet.agents.searcher.files_keyword_search import FilesKeywordSearch, FilesKeywordSearchReq
from fleet.agents.searcher.keyword_extract import KeywordExtract, KeywordExtractReq
from fleet.context import Context
from fleet.fst.fst import FST
# from loguru import logger
# logger.remove()
# logger.add(sys.stdout, level="DEBUG")



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
            # model="gpt-4o-mini",
            model="gpt-4o-2024-08-06",
        )
        ctx.workspace = manager.create(config)

        issue = f"<description>:{rule['problem_statement']}"
        if "hints_text" in rule and rule['hints_text']:
            issue += f"\n<hints>:{rule['hints_text']}</hints>"
        issue += f"</description>"
        ctx.issue = issue
        ctx.trace = True
        return ctx

    def start(self):
        ctx = self.prepare_ctx()

        logger.info(f"task_id: {self.task_id}")
        logger.info(f"model: {ctx.model}")
        logger.info(f'Workspace created: {ctx.workspace.id()}')

        # TODO: write a tool in concave to get tokens
        with open("/Users/justwph/labs/hackathons/2024/concave/tests/code_search/tokens.txt") as f:
            repo_tokens = f.read()

        key_extract = KeywordExtract(ctx, KeywordExtractReq(repo_tokens=repo_tokens.split("\n")))
        key_extract_res = key_extract.run()

        key_search = FilesKeywordSearch(ctx, FilesKeywordSearchReq(tokens=key_extract_res.keywords))
        key_search_res = key_search.run()

        files_filter = FilesFilter(ctx, FilesFilterReq(keyword_search_results=key_search_res.results))
        files_filter.run()

        file_paths = files_filter.response.file_paths[:4]
        for file_path in file_paths:
            file_evaluate = FileEvaluate(ctx, FileEvaluateReq(file_path=file_path))
            file_evaluate.run()



def get_all_pytest_ids():
    ds = load_dataset("princeton-nlp/SWE-bench_Verified")
    rows = ds.get("test")
    return [row["instance_id"] for row in rows if "pytest" in row["instance_id"]]



if __name__ == "__main__":
    # swe_bench_id = "pytest-dev__pytest-5262"
    for swe_bench_id in get_all_pytest_ids():
        task = SweBenchTask(swe_bench_id)
        task.start()