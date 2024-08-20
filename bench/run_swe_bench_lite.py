import sys
import tempfile
import time
import traceback

from concave.internal.datasets.config import get_config_from_swe_bench
from concave.internal.workspace.manager import WorkspaceManager
from datasets import load_dataset

from fleet.agents.code_gen.symbol_evaluate import SymbolsEvaluate
from fleet.agents.searcher.file_evaluate import FileEvaluate, FileEvaluateReq
from fleet.agents.searcher.file_symbol_search import FileSymbolSearch, FilesSymbolSearchReq
from fleet.agents.searcher.files_filter import FilesFilter, FilesFilterReq
from fleet.agents.searcher.files_keyword_search import FilesKeywordSearch, FilesKeywordSearchReq
from fleet.agents.searcher.keyword_extract import KeywordExtract, KeywordExtractReq
from fleet.agents.searcher.symbol_summary import SymbolSummary, SymbolSummaryReq
from fleet.context import Context
from fleet.task.task import Task
from fleet.utils import unique_list

from multiprocessing.pool import ThreadPool

from loguru import logger

from fleet.utils.searcher.searcher import SymbolSearcher

logger.remove()
logger.add(sys.stdout, level="DEBUG")


class SweBenchTask:
    def __init__(self, task_id):
        # task_id == instance_id , e.g. pytest-dev__pytest-5262
        self.task_id = task_id

    def get_test_rule_from_dataset(self):
        ds = load_dataset("princeton-nlp/SWE-bench_Lite")
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

        ctx.issue = f"<description>:{rule['problem_statement']}</description>"
        ctx.trace = True
        return ctx

    def start_issue_identify(self):
        ctx = self.prepare_ctx()

        logger.debug(f"task_id: {self.task_id}")
        logger.debug(f"model: {ctx.model}")
        logger.debug(f'Workspace created: {ctx.workspace.id()}')

        with Task(ctx) as task:
            tmp = tempfile.mkdtemp()
            index_file = ctx.workspace.open("/workspace/index/symbol_index.parquet").read(binary=True)
            with open(f"{tmp}/symbol_index.parquet", "wb") as f:
                f.write(index_file)
            searcher = SymbolSearcher(f"{tmp}/symbol_index.parquet")
            src_tokens = searcher.tokens()
            ctx.searcher = searcher

            key_extract_res = task.run(KeywordExtract, req=KeywordExtractReq(repo_tokens=src_tokens))
            key_search_res = task.run(FilesKeywordSearch, req=FilesKeywordSearchReq(tokens=key_extract_res.keywords))
            files_filter_res = task.run(FilesFilter, req=FilesFilterReq(keyword_search_results=key_search_res.results))

            file_paths = unique_list(files_filter_res.file_paths)
            files = []
            file_evaluate_res = []

            for file_path in file_paths:
                res = task.run(FileEvaluate, req=FileEvaluateReq(file_path=file_path))
                files.append({
                    "file_path": file_path,
                    "relevant_symbol_keys": res.relevant_symbols,
                    "root_cause_symbol_keys": res.root_cause_symbols
                })
                file_evaluate_res.append(res)
            symbols = task.run(FileSymbolSearch, req=FilesSymbolSearchReq(files=files))
            symbols_evaluate = task.run(SymbolsEvaluate, req=symbols)

            summary = task.run(SymbolSummary, req=SymbolSummaryReq(
                symbols=symbols,
                symbols_evaluate=symbols_evaluate
            ))


def get_all_pytest_ids():
    ds = load_dataset("princeton-nlp/SWE-bench_Lite")
    rows = ds.get("test")
    return [row["instance_id"] for row in rows if "pytest" in row["instance_id"]]


def get_all_ids():
    ds = load_dataset("princeton-nlp/SWE-bench_Verified")
    rows = ds.get("test")
    return [row["instance_id"] for row in rows]


def run_swe_bench_task(task_id):
    start = time.time()
    logger.info("Running task: {}".format(task_id))
    try:
        task = SweBenchTask(task_id)
        task.start_issue_identify()
        used = int(1000 * (time.time() - start)) / 1000
        logger.info("Task completed: {}, used: {}".format(task_id, used))
    except Exception as e:
        logger.error("Failed to run task: {}".format(task_id))
        logger.error(e)
        print(traceback.format_exc())


def run_all_task():
    pool = ThreadPool(8)
    pool.map(run_swe_bench_task, get_all_pytest_ids())
    pool.close()
    pool.join()




if __name__ == "__main__":
    run_swe_bench_task("pytest-dev__pytest-11148")