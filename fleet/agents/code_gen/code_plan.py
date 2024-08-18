from typing import List

from pydantic import Field, BaseModel

from fleet.agents.base.base import OpenAIAgent
from fleet.agents.code_gen.symbol_evaluate import ChangedSymbol, SymbolEvaluateRes

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing 
codebase based on a reported issue. 
you task is base on the files and symbols to identify which code part need to be changed to resolve the issue.
you will make a code edit plan
The description of the issue may only be the surface problem; please consider all possibilities carefully. Your goal is to address the root cause, not just provide a simple fix for the issue.

#Input Structure:

* <issue>: Contains the reported issue.
* <file>: the file content.
* <symbol>: the symbol


# Your Task:

1. Analyze User Instructions:
Carefully read the reported issue within the <issue> tag.
think step by step and write out your thoughts in the scratch_pad field.
1.1 What issue is the user describing?
1.2 How was this issue caused?
1.3 If the user described the expected result, what should it be fixed to?
1.4 If the user did not provide an expected result, what should the expectation be?
1.5 How should the issue be fixed to meet the expectation?
1.6 Remember, you should think from the perspective of a core library developer. This means you need to consider how to make the solution simple, safe, and minimize code changes.

2. Make the evaluate:
2.1. Thoroughly analyze each lines in the <file> and <symbol> tags.
2.2. Match the symbol/code/pattern with the key elements, functions, variables, or patterns identified in the reported issue.
2.3. Evaluate the relevance of each symbol based on how well it aligns with the reported issue and current file context.
2.5. make the plans how to change the code to resolve the issue.

Think step by step and write out your thoughts in the scratch_pad field.  
"""


class CodePlanReq(BaseModel):
    symbols: List[ChangedSymbol] = Field(description="List of symbols that need to be changed.")


class Plan(BaseModel):
    file_path: str = Field(description="The file need to change")
    type: str = Field(description="The type of the plan. add, replace, delete")
    plan_detail: str = Field(description="The plan detail")


class CodePlanRes(BaseModel):
    scratch_pad: str = Field(description="Your thoughts the problem and how to solve it.")
    plans: List[Plan] = Field(description="List of plans to change the code.")


class CodePlan(OpenAIAgent):
    name = "CodePlan"
    responseType = CodePlanRes
    request = SymbolEvaluateRes

    def __init__(self, ctx, req: SymbolEvaluateRes):
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
        files = set()

        for symbol in self.request.symbols:
            base.append({"role": "user", "content": f"<symbol><name>{symbol.name}</name><path>{symbol.file_path}</path></symbol>"})
            if symbol.file_path not in files:
                file_content = self.ctx.workspace.open(symbol.file_path).read()
                base.append({"role": "user", "content": f"<file>{file_content}</file>"})
                files.add(symbol.file_path)
        return base

    def run(self):
        self.messages = self.create_messages()
        return self._call_openai(self.messages)
