from concave.internal.codebase.search.symbol.searcher import SymbolSearcher

from bench.run_swe_bench import SweBenchTask
from fleet.agents.searcher.file_symbol_search import FileSymbolSearch, FileSymbolSearchReq, FilesSymbolSearchReq


def test():
    task = SweBenchTask("pytest-dev__pytest-5262")
    ctx = task.prepare_ctx()
    req = FilesSymbolSearchReq(
        files=[
            FileSymbolSearchReq(
                file_path="src/_pytest/capture.py",
                relevant_symbol_keys=[
                    "EncodedFile#write().",
                    "EncodedFile#"
                ],
                root_cause_symbol_keys=[
                    "EncodedFile#write().",
                    "EncodedFile#"
                ]
            )
        ],
        with_content=True
    )
    agent = FileSymbolSearch(ctx, req=req)
    agent.run()

    print(agent.response)


if __name__ == "__main__":
    test()
