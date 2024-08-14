from concave.internal.datasets.config import get_config_from_swe_bench
from concave.internal.workspace.manager import WorkspaceManager
from datasets import load_dataset

from fleet.agents.searcher.file_evaluate import FileEvaluate
from fleet.agents.searcher.files_filter import FilesFilter
from fleet.agents.searcher.files_keyword_search import FilesKeywordSearch
from fleet.agents.searcher.keyword_extract import KeywordExtract
from fleet.context import Context
from fleet.fst.fst import FST


def prepare_fst():
    fst = FST()
    fst.add(KeywordExtract.state.END, FilesKeywordSearch.state.START)
    print(fst.status_map)


def get_test_rule_from_dataset(swe_bench_id):
    ds = load_dataset("princeton-nlp/SWE-bench_Verified")
    rows = ds.get("test")
    filter_rows = [row for row in rows if swe_bench_id in row["instance_id"]]
    if len(filter_rows) == 0:
        raise ValueError(f"Could not find {swe_bench_id} in SWE-bench_Verified")
    return filter_rows[0]


def prepare_ctx(swe_bench_id: str):
    rule = get_test_rule_from_dataset(swe_bench_id)
    config = get_config_from_swe_bench(
        name=rule["instance_id"],
        repo=rule["repo"],
        version=rule["version"],
        base_commit=rule["base_commit"]
    )

    manager = WorkspaceManager()

    ctx = Context(
        task_id=swe_bench_id,
        model="gpt-4o-mini",
        # model="gpt-4o-2024-08-06",
    )
    ctx.workspace = manager.create(config)

    issue = f"<description>:{rule['problem_statement']}"
    if "hints_text" in rule and rule['hints_text']:
        issue += f"\n<hints>:{rule['hints_text']}</hints>"
    issue += f"</description>"
    ctx.issue = issue
    ctx.trace = True
    return ctx


def start(ctx):
    # TODO: write a tool in concave to get tokens
    with open("/Users/justwph/labs/hackathons/2024/concave/tests/code_search/tokens.txt") as f:
        repo_tokens = f.read()

    key_extract = KeywordExtract(ctx, repo_tokens)
    key_extract.run()
    # key_extract.load("logs/pytest-dev__pytest-5262/KeywordExtract/2024-08-14T11:43:26.559643.json")

    key_search = FilesKeywordSearch(ctx, key_extract.response.keywords)
    key_search.run()

    files_filter = FilesFilter(ctx, key_search.response.results)
    files_filter.run()

    files = files_filter.response.files[:2]
    for file in files:
        file_evaluate = FileEvaluate(ctx, file)
        file_evaluate.run()


def start_from_filters(ctx):
    files_filter = FilesFilter(ctx, [])
    files_filter.load("logs/pytest-dev__pytest-5631/FilesFilter/2024-08-14T13:31:24.024871.json")
    print(files_filter.response.files)
    files = files_filter.response.files[:4]
    for file in files:
        file_evaluate = FileEvaluate(ctx, file)
        file_evaluate.run()


def run_swe_bench(swe_bench_id):
    ctx = prepare_ctx(swe_bench_id)
    start(ctx)

def get_all_pytest_ids():
    ds = load_dataset("princeton-nlp/SWE-bench_Verified")
    rows = ds.get("test")
    return [row["instance_id"] for row in rows if "pytest" in row["instance_id"]]


def full_test():
    ids = get_all_pytest_ids()
    for swe_bench_id in ids:
        run_swe_bench(swe_bench_id)

def round_2():
    ids = ["pytest-dev__pytest-7490", "pytest-dev__pytest-7982"]
    for swe_bench_id in ids:
        run_swe_bench(swe_bench_id)

# full_test()
round_2()