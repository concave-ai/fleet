from typing import List

from pydantic import Field, BaseModel

from fleet.agents.base.base import OpenAIAgent
from fleet.agents.code_gen.code_plan import Plan, CodePlanRes
from fleet.agents.code_gen.symbol_evaluate import ChangedSymbol, SymbolEvaluateRes
from fleet.agents.searcher.file_symbol_search import FileSymbolSearchRes

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing 
codebase based on a reported issue. 
you task is base on the source code and the plan, change the code to resolve the issue. 
#Input Structure:

* <issue>: Contains the reported issue.
* <file>: the file content.
* <plan>: the code change plan. 


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
2.1. Thoroughly analyze each lines in the <file> and <plan> tags.
2.2. Match the symbol/code/pattern with the key elements, functions, variables, or patterns identified in the reported issue.
2.3. Only modify the parts related to the plan. If you think the plan cannot solve the problem, return a failure instead of trying to modify it.


The description of the issue may only be the surface problem; please consider all possibilities carefully. Your goal is to address the root cause, not just provide a simple fix for the issue.
Think step by step and write out your thoughts in the scratch_pad field.  
"""



class CodeGenRes(BaseModel):
    scratch_pad: str = Field(description="Your thoughts the problem and how to solve it.")
    changed_code: str = Field(description="The changed code.")
    explain_code: str = Field(description="The explain of the changed code.")
    is_fault: bool = Field(description="The code change is fault. you need to change the plan.")



class CodeGen(OpenAIAgent):
    name = "CodeGen"
    responseType = CodeGenRes
    request = CodePlanRes

    def __init__(self, ctx, req: CodePlanRes):
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
        plans = []
        files = set()
        for plan in self.request.plans:
            plans.append(f"<plan>{plan.plan_detail}</plan>")
            if plan.file_path not in files:
                file_content = self.ctx.workspace.open(plan.file_path).read()
                base.append({"role": "user", "content": f"<file>{file_content}</file>"})
                files.add(plan.file_path)

        return base

    def run(self):
        self.messages = self.create_messages()
        return self._call_openai(self.messages)
