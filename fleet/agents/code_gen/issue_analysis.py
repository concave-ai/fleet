from typing import List

from pydantic import Field, BaseModel

from fleet.agents.base.base import OpenAIAgent
from fleet.agents.code_gen.symbol_evaluate import ChangedSymbol, SymbolEvaluateRes
from fleet.agents.searcher.file_symbol_search import FileSymbolSearchRes

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing 
codebase based on a reported issue. 
you task is base on the files and symbols to identify which code part need to be changed to resolve the issue.
you will make a code edit plan
#Input Structure:

* <issue>: Contains the reported issue.
* <file>: the source_code. 


# Your Task:

1. Analyze User Instructions:
Carefully read the reported issue within the <issue> tag.
think step by step and write out your thoughts in the scratch_pad field.
1.1 What issue is the user describing?
1.2 User give a reproduce steps?, if yes, think why this steps cause the issue.
1.3 How was this issue caused?
1.4 Summary the user expectation and why cause the issue.


2. Analyze the code:
Carefully read the code in the <file> tag.
2.1 What is the code doing?
2.2 if issue include stacktrace, check the stacktrace and find the code part.
2.3. read code carefully to understand why error happens.



The description of the issue may only be the surface problem; please consider all possibilities carefully. 
Your goal is to address the root cause, not just provide a simple fix for the issue.





"""





class IssueAnalysisRes(BaseModel):
    scratch_pad: str = Field(description="Your thoughts the problem and how to solve it.")
    explain: str = Field(description="The explanation of the issue.")

class IssueAnalysisReq(BaseModel):
    file_path: str = Field(description="The file caused the issue.")

class IssueAnalysis(OpenAIAgent):
    name = "IssueAnalysis"
    responseType = IssueAnalysisRes

    def __init__(self, ctx, req: IssueAnalysisReq):
        super().__init__(ctx)
        self.request = req

    def create_messages(self):
        file = self.ctx.workspace.open(self.request.file_path).read()

        base = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": self.content_template(
                 issue=self.ctx.issue,
                 file=file,
             )}
        ]
        return base

    def run(self):
        self.messages = self.create_messages()
        return self._call_openai(self.messages)
