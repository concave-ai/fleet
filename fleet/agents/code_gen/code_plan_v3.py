from typing import List

from pydantic import Field, BaseModel

from fleet.agents.base.base import OpenAIAgent
from fleet.agents.code_gen.code_plan import Plan, CodePlanRes

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing 
codebase based on a reported issue. 
you task is base on the source code and the issue_analysis, make a code fix plan
#Input Structure:

* <issue>: Contains the reported issue.
* <issue_analysis>: the file content.
* <file>: the code change plan. 


# Your Task:
1. Analyze User Instructions:
Carefully read the reported issue within the <issue> tag.
2. Think about the issue_analysis:
Think about the issue_analysis in the <issue_analysis> tag.
3. Analyze the code:
Carefully read the code in the <file> tag.
4. Base on code andd issue_analysis to make a callflow:

Generate callflow only use the code in <file> tag to reproduce the issue. 
format:
callflow = ($callflow_row + \n)*
callflow_row = $symbol $action_description
$symbol = ($module)*+$function
$function = $function_name+"()."
$class = $class_name+"#"
$moudle = $func | $class



5. Make the plan:
based on the issue_analysis and the code, make a code fix plan. 
you can add, replace, delete some code.
Your plan needs to be very detailed.
You have clearly analyzed which code needs to be modified.
You have a clear understanding of the current functionality of the code segments that need to be changed.
You have a clear understanding of which functions call the segments that need to be modified, and these functions will not be affected. The callers of these functions are also unaffected.
You have a clear understanding of which functions are called by the segments that need to be modified, and these functions are not the cause of the issue, nor are the functions called by these functions.
What impact will the changes to the code have?
Please ensure that the modified code does not break the existing logic.
Please ensure that the modified code fully and thoroughly addresses the issue, not just the user-reported problem, as the user-reported issue may only be a part of the problem.




Think step by step and write out your thoughts in the scratch_pad field.  
"""


class CodePlanV3Req(BaseModel):
    issue_analysis: str = Field(description="The issue analysis.")
    file_path: str = Field(description="The file need to change")


class CodePlanV3Res(BaseModel):
    scratch_pad: str = Field(description="Your thoughts the problem and how to solve it.")
    call_flowchart: str = Field(description="The code call flowchart to explain how the issue occurs.")
    is_fault: bool = Field(description="The code change is fault. you need to change the analysis.")
    plans: List[Plan] = Field(description="List of plans to change the code.")


class CodePlanV3(OpenAIAgent):
    name = "CodePlanV3"
    responseType = CodePlanV3Res

    def __init__(self, ctx, req: CodePlanV3Req):
        super().__init__(ctx)
        self.request = req

    def create_messages(self):
        file = self.ctx.workspace.open(self.request.file_path).read()
        base = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": self.content_template(
                 issue=self.ctx.issue,
                 issue_analysis=self.request.issue_analysis,
                 file=file
             )}
        ]

        return base

    def run(self):
        self.messages = self.create_messages()
        return self._call_openai(self.messages)
