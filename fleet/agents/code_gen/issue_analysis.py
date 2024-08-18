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


# Your Task:

1. Analyze User Instructions:
Carefully read the reported issue within the <issue> tag.
think step by step and write out your thoughts in the scratch_pad field.
1.1 What issue is the user describing?
1.2 User give a reproduce steps?, if yes, think why this steps cause the issue.
1.3 How was this issue caused?
1.4 Summary the user expectation and why cause the issue.
1.6 Some possible solutions to the issue.


The description of the issue may only be the surface problem; please consider all possibilities carefully. Your goal is to address the root cause, not just provide a simple fix for the issue.





"""


class Plan(BaseModel):
    file_path: str = Field(description="The file need to change")
    type: str = Field(description="The type of the plan. add, replace, delete")
    plan_detail: str = Field(description="The plan detail")


class IssueAnalysisRes(BaseModel):
    scratch_pad: str = Field(description="Your thoughts the problem and how to solve it.")
    plans: List[Plan] = Field(description="List of plans to change the code.")


class IssueAnalysis(OpenAIAgent):
    name = "IssueAnalysis"
    responseType = IssueAnalysisRes

    def __init__(self, ctx, req: None):
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
        return base

    def run(self):
        self.messages = self.create_messages()
        return self._call_openai(self.messages)
