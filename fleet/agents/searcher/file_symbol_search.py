from concave.internal.codebase.search.symbol.searcher import SymbolSearcher, match_keys
from concave.internal.workspace.file import File
from pydantic import BaseModel, Field

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
    start_line: int
    start_column: int = 0
    end_line: int = 0
    end_column: int = 0
    start_byte: int
    end_byte: int = 0


class FileSymbolSearchRes(BaseModel):
    related_symbols: list[FileSymbol]
    root_caused_symbols: list[FileSymbol]


class CodeReader:
    def __init__(self, workspace):
        self._files = {}
        self.workspace = workspace

    def read(self, file_path):
        if file_path not in self._files:
            f: File = self.workspace.open(file_path)
            self._files[file_path] = f.read(binary=True)
        return self._files[file_path]

    def get_content(self, file_path, byte_start, byte_end):
        content = self.read(file_path)
        return str(content[byte_start:byte_end], encoding='utf-8')


class FileSymbolSearch(Agent):
    name = "FileSymbolSearch"
    request = FilesSymbolSearchReq
    response = FileSymbolSearchRes

    def __init__(self, ctx, req: FilesSymbolSearchReq):
        super().__init__(ctx)
        self.request = req

    def _file_search(self, req: FileSymbolSearchReq):
        response = FileSymbolSearchRes(related_symbols=[], root_caused_symbols=[])

        reader = CodeReader(self.ctx.workspace)
        keys = list(set(req.relevant_symbol_keys + req.root_cause_symbol_keys))

        results = self.ctx.searcher.search(keys)
        for r in results:
            symbol = FileSymbol(name=r.id,
                                start_line=r.range[0],
                                start_column=r.byte_range[0],
                                end_line=r.range[1],
                                end_column=r.byte_range[1],
                                start_byte=r.byte_range[0],
                                end_byte=r.range[1],
                                file_path=req.file_path,
                                file_content=None)
            if self.request.with_content:
                symbol.file_content = reader.get_content(req.file_path, r.byte_range[0],
                                                         r.byte_range[1])

            if match_keys(r.id, req.root_cause_symbol_keys):
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
