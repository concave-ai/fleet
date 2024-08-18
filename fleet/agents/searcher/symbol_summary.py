import os.path

from pydantic import BaseModel

from fleet.agents.base.base import Agent
from fleet.agents.code_gen.symbol_evaluate import SymbolEvaluateRes
from fleet.agents.searcher.file_symbol_search import FileSymbol, FileSymbolSearchRes
from fleet.utils import unique_list


class SymbolSummaryReq(BaseModel):
    symbols: FileSymbolSearchRes
    symbols_evaluate: SymbolEvaluateRes


class SymbolSummaryRes(BaseModel):
    file_paths: list[str]
    symbols: list[str]
    code_spans: dict[str, FileSymbol]


class SymbolSummary(Agent):
    name = "SymbolSummary"
    requestType = SymbolSummaryReq

    def __init__(self, ctx, req: SymbolSummaryReq):
        super().__init__(ctx)
        self.request = req

    def run(self):
        self.response = SymbolSummaryRes(
            file_paths=unique_list([s.file_path for s in self.request.symbols_evaluate.symbols]),
            symbols=unique_list([s.name for s in self.request.symbols_evaluate.symbols]),
            code_spans={s.name: s for s in self.request.symbols.related_symbols}
        )
        for s in self.request.symbols.root_caused_symbols:
            self.response.code_spans[s.name] = s

        self.after_run()
        self.dump_response()

    def dump_response(self):
        path = os.path.dirname(os.path.dirname(self.get_output_dir()))
        with open(f"{path}/issue_identify.json", "w") as f:
            f.write(self.response.model_dump_json(indent=4))
