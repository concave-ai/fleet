from typing import List

from pydantic import BaseModel, Field

from fleet.agents.base.base import OpenAIAgent
from fleet.agents.searcher.file_symbol_search import FileSymbolSearchRes

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing 
codebase based on a reported issue. 
Your task is base on the symbol code to identify how many symbols need to be change to resolve the issue. 
#Input Structure:

* <issue>: Contains the reported issue.
* <symbol>: the code might to be relevant to the issue.

# Your Task:

1. Analyze User Instructions:
Carefully read the reported issue within the <issue> tag.
think step by step and write out your thoughts in the scratch_pad field.
1.1 What issue is the user describing?
1.2 How was this issue caused?
1.3 If the user described the expected result, what should it be fixed to?
1.4 If the user did not provide an expected result, what should the expectation be?
1.5 How should the issue be fixed to meet the expectation?

2. Make the evaluate:
2.1. Thoroughly analyze each lines in the <symbol> and <symbol> tags.
2.2. Match the symbol/code/pattern with the key elements, functions, variables, or patterns identified in the reported issue.
2.3. Evaluate the relevance of each symbol based on how well it aligns with the reported issue and current file context.
2.4. make the decision how many symbols need to be change to resolve the issue.
2.5. if you need more file content or symbol information, you can ask the user for more information.
2.6. relative symbol means, He might be the root cause of the problem, or he could be a part of the process that reproduces the issue.

Think step by step and write out your thoughts in the scratch_pad field.  
"""


class ChangedSymbol(BaseModel):
    name: str = Field(description="The name of the symbol.")
    file_path: str = Field(description="The file path of the symbol.")
    reason: str = Field(description="The reason why the symbol needs to be changed.")


class MoreInfo(BaseModel):
    type: str = Field(description="The info type, file or symbol.")
    path: str = Field(description="The path of the file.")
    name: str = Field(description="The name of the symbol.")
    reason: str = Field(description="The reason why you need more information.")


class SymbolEvaluateRes(BaseModel):
    scratch_pad: str = Field(description="Your thoughts the problem and how to solve it.")
    symbols: List[ChangedSymbol] = Field(description="List of symbols that relative the issue.")
    more_info: List[MoreInfo] = Field(description="The type of information you need more.")
    is_done: bool = Field(description="You have enough information to solve the issue.")
    symbols_scratch_pad: list[str] = Field(description="Your thoughts the each symbol i give to you")


class SymbolsEvaluate(OpenAIAgent):
    name = "SymbolsEvaluate"
    response = SymbolEvaluateRes
    responseType = SymbolEvaluateRes
    request = FileSymbolSearchRes

    def __init__(self, ctx, req: FileSymbolSearchRes):
        super().__init__(ctx)
        self.request = req

    def create_messages(self):
        base = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": self.content_template(
                 issue=self.ctx.issue,
             )}
        ]
        for symbol in self.request.root_caused_symbols:
            s = f"<name>{symbol.name}</name><path>{symbol.file_path}</path><content>{symbol.file_content}</content>"
            base.append({"role": "user", "content": f"<symbol>{s}</symbol>"})

        for symbol in self.request.related_symbols:
            s = f"<name>{symbol.name}</name><path>{symbol.file_path}</path><content>{symbol.file_content}</content>"
            base.append({"role": "user", "content": f"<symbol>{s}</symbol>"})

        return base

    def run(self):
        self.messages = self.create_messages()
        return self._call_openai(self.messages)
