import json

from datasets import load_dataset

from agents.searcher.keyword_choose import KeywordChoose
from agents.searcher.keyword_search import KeywordSearch
from agents.searcher.relative_file import RelativeFile
from fleet.context import Context

ds = load_dataset("princeton-nlp/SWE-bench_Verified")


def load_context(id: str) -> Context:
    context = Context(
        task_id=id,
        # model="gpt-4o-mini",
        model="gpt-4o-2024-08-06",
    )

    tests = ds.get("test")
    issue = None
    for test in tests:
        if test['instance_id'] == id:
            issue = test
            break
    context.issue = f"<description>:{issue['problem_statement']}</description>"
    if "hints_text" in issue and issue['hints_text']:
        context.issue += f"\n<hints>:{issue['hints_text']}</hints>"
    context.trace = True
    return context


ctx = load_context("pytest-dev__pytest-7432")

print("START")


# print("============ PROBLEM ====================")
# print(ctx.issue)
# print("=========================================")


def run_to_openai():
    with open("/Users/justwph/labs/hackathons/2024/concave/tests/code_search/tokens.txt") as f:
        repo_tokens = f.read()

    choose = KeywordChoose(ctx, repo_tokens)
    choose.run()
    key_search = KeywordSearch(ctx, choose.response.keywords)
    print(key_search.get_cmd())


def run_with_logs():
    # choose = KeywordChoose(ctx, "").load("logs/KeywordChoose/pytest-dev__pytest-7432/2024-08-13T21:07:21.528149.json")
    key_search = KeywordSearch(ctx, [])
    key_search.run_from_jsonl("logs/KeywordSearch/pytest-dev__pytest-7432/rg_results.jsonl")


def relative_openai():
    key_search = KeywordSearch(ctx, [])
    key_search.load("logs/KeywordSearch/pytest-dev__pytest-7432/2024-08-13T21:44:38.920207.json")
    relative = RelativeFile(ctx, key_search.response.results)
    relative.run()


# run_to_openai()
# run_with_logs()
relative_openai()
