import tempfile

from concave.internal.workspace.config import Config
from concave.internal.workspace.manager import WorkspaceManager
from loguru import logger

from fleet.agents.code_gen.code_gen import CodeGen
from fleet.agents.code_gen.code_plan_v3 import CodePlanV3, CodePlanV3Req
from fleet.agents.code_gen.issue_analysis import IssueAnalysis, IssueAnalysisReq
from fleet.agents.searcher.keyword_extract import KeywordExtract, KeywordExtractReq
from fleet.context import Context
from fleet.task.task import Task
from fleet.utils import unique_list
from fleet.utils.searcher.searcher import SymbolSearcher
from fleet.agents.code_gen.symbol_evaluate import SymbolsEvaluate
from fleet.agents.searcher.file_evaluate import FileEvaluate, FileEvaluateReq
from fleet.agents.searcher.file_symbol_search import FileSymbolSearch, FilesSymbolSearchReq
from fleet.agents.searcher.files_filter import FilesFilter, FilesFilterReq
from fleet.agents.searcher.files_keyword_search import FilesKeywordSearch, FilesKeywordSearchReq
from fleet.agents.searcher.keyword_extract import KeywordExtract, KeywordExtractReq
from fleet.agents.searcher.symbol_summary import SymbolSummary, SymbolSummaryReq

ISSUE = """

    
Exception ignored in: <function TiDBVectorClient.__del__ at 0x1693e63e0>
Traceback (most recent call last):
  File "/Users/justwph/Library/Caches/pypoetry/virtualenvs/concave-KQBUMHDg-py3.11/lib/python3.11/site-packages/tidb_vector/integrations/vector_client.py", line 177, in __del__
AttributeError: 'NoneType' object has no attribute 'Connection'


isinstance(self._bind, sqlalchemy.engine.base.Connection)
self._bind is None is false, works fine
sqlalchemy.engine is None very strange, it should be a sqlalchemy.engine.base.Connection object, but it is None.
__del__ in high version python have some changes?



"""


def run():
    task_id = "tidb_vector_python_58"
    manager = WorkspaceManager()

    ctx = Context(
        task_id=task_id,
        model="gpt-4o-2024-08-06",
    )
    ctx.workspace = manager.create(Config(
        name=task_id,
        language='python',
        version='3.11',
        codebase='github.com/pingcap/tidb-vector-python/commit/42b2659e61d2ed5c6ee87d7d8f131799f61e0c4b',
        project_setup=[
            "pip install poetry",
            "poetry install --no-root"
        ],
    ))

    ctx.issue = f"<description>:{ISSUE}</description>"
    ctx.trace = True

    logger.debug(f"task_id: {task_id}")
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

        issue_analysis = task.run(IssueAnalysis, req=IssueAnalysisReq(
            file_path="./tidb_vector/integrations/vector_client.py"
        ))
        code_plan = task.run(CodePlanV3, req=CodePlanV3Req(
            issue_analysis=issue_analysis.explain,
            file_path="./tidb_vector/integrations/vector_client.py"
        ))
        code_gen = task.run(CodeGen, req=code_plan)


if __name__ == '__main__':
    run()