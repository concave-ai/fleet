from concave.internal.codebase.search.symbol.searcher import SymbolSearcher, match_keys
from pydantic import BaseModel

from fleet.agents.base.base import Agent
from fleet.utils import unique_list


class FileSymbolSearchReq(BaseModel):
    file_path: str
    relevant_symbol_keys: list[str]
    root_cause_symbol_keys: list[str]


class FilesSymbolSearchReq(BaseModel):
    files: list[FileSymbolSearchReq]
    with_content: bool = True


class FileSymbol(BaseModel):
    name: str
    file_path: str
    file_content: str | None


class FileSymbolSearchRes(BaseModel):
    related_symbols: list[FileSymbol]
    root_caused_symbols: list[FileSymbol]


class CodeReader:
    def __init__(self, workspace):
        self._files = {}
        self.workspace = workspace

    def read(self, file_path):
        if file_path not in self._files:
            self._files[file_path] = self.workspace.open(file_path).read()
        return self._files[file_path]

    def get_content(self, file_path, start_line, end_line):
        content = self.read(file_path)
        lines = content.split("\n")
        return "\n".join(lines[start_line:end_line])


class FileSymbolSearch(Agent):
    name = "FileSymbolSearch"
    request = FilesSymbolSearchReq
    response = FileSymbolSearchRes

    def __init__(self, ctx, req: FilesSymbolSearchReq):
        super().__init__(ctx)
        self.request = req

    def _file_search(self, req: FileSymbolSearchReq):

        reader = CodeReader(self.ctx.workspace)
        keys = list(set(req.relevant_symbol_keys + req.root_cause_symbol_keys))
        index_file = self.ctx.workspace.open("/workspace/index/scip/index.scip")
        searcher = SymbolSearcher(index_file.read(binary=True))
        results = searcher.search_symbols(keys, filter_path=req.file_path, filter_types=["CLASS", "METHOD"])
        response = FileSymbolSearchRes(related_symbols=[], root_caused_symbols=[])
        for r in results:
            symbol = FileSymbol(name=r.name, file_path=req.file_path, file_content=None)
            if self.request.with_content:
                symbol.file_content = reader.get_content(req.file_path, r.enclosing_start_line,
                                                         r.enclosing_end_line)

            if match_keys(r.name, req.root_cause_symbol_keys):
                response.root_caused_symbols.append(symbol)
            else:
                response.related_symbols.append(symbol)
        return response

    def run(self):
        response = FileSymbolSearchRes(related_symbols=[], root_caused_symbols=[])
        for f in self.request.files:
            result = self._file_search(f)
            response.related_symbols.extend(result.related_symbols)
            response.root_caused_symbols.extend(result.root_caused_symbols)

        response.related_symbols = response.related_symbols
        response.root_caused_symbols = response.root_caused_symbols
        self.response = response
        self.after_run()
        return response
