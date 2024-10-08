from typing import Optional

from pydantic import BaseModel, Field

from fleet.agents.base.base import OpenAIAgent

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing 
codebase based on a reported issue. Your task is to identify the relevant symbols in the provided source code
and decide whether this code relates to the reported issue. 
symbols: functions, classes, variables that are relevant to the issue.
 
# Input Structure:

* <issue>: Contains the reported issue.
* <file_path>: Contains the path of the file to evaluate.
* <file_content>: Contains the content of the file to evaluate.

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


2. Make file evaluation:
2.1. Thoroughly analyze each lines in the <file_content> tag.
2.2. Match the symbol with the key elements, functions, variables, or patterns identified in the reported issue.
2.3. Evaluate the relevance of each symbol based on how well it aligns with the reported issue and current file context.
2.4. Review entire sections of code, not just isolated symbol, to ensure you have a complete understanding before making a decision. It's crucial to see all code in a section to accurately determine relevance and completeness.
2.5. Verify if there are references to other parts of the codebase that might be relevant but not found in the search results. 
2.6. Determine if the file is the root cause of the issue or if it's related to the root cause.

3. Output Your Decision:
symbol: symbol can be a function name or class name.

class: python class, end with a hash "#"
method: python method, end with three char "()."

e.g. 
# 1. bark() method of Dog class
symbol: Dog.bark
# 2. Dog class
symbol: Dog
# 3. def fly(item)
symbol: fly
# 4. method eat(item, quantity):
symbol: eat
# 5. method eat(item, quantity) in Cat class
symbol: Cat.eat
# 6. method eat_fish(item, quantity) in method eat(item, quantity) in Cat class
symbol: Cat.eat.eat_fish
# 6. method eat_fish(item, quantity) in method eat(item, quantity) in method action()
symbol: action.eat.eat_fish




Think step by step and write out your thoughts in the scratch_pad field. 
"""


class FileEvaluateRes(BaseModel):
    scratch_pad: str = Field(
        description="Your thoughts on if the file where relevant or not"
    )

    relevant: bool = Field(
        description="Set to true if the relevant code have been identified.",
    )

    root_cause: bool = Field(
        description="Set to true if you think the file i give is the  root cause of the issue.",
    )

    relevant_files: list[str] = Field(
        description="if you think the file is not root cause, but it's relative, suggest some file to evaluate. max: "
                    "3 files."
    )
    relevant_symbols: list[str] = Field(
        description="If the file is relevant, suggest some symbol that caused the issue. "
                    "symbol can be a function name or class name. "
                    "limit 10 symbols."
    )

    root_cause_symbols: list[str] = Field(
        description="If the file is root cause, suggest some symbol that caused the issue. "
                    "symbol can be a function name or class name. "
                    "this str list no size limit."
    )


class FileEvaluateReq(BaseModel):
    file_path: str = Field(description="The path of the file to evaluate.")


class FileEvaluate(OpenAIAgent):
    name = "FileEvaluate"

    response: Optional[FileEvaluateRes]
    requestType = FileEvaluateReq
    responseType = FileEvaluateRes

    def __init__(self, ctx, req: FileEvaluateReq):
        self.request = req
        super().__init__(ctx=ctx)

    def create_messages(self, content):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": self.content_template(
                 issue=self.ctx.issue,
                 file_path=self.request.file_path,
                 file_content=content
             )},

        ]

    def run(self):
        f = self.ctx.workspace.open(self.request.file_path)
        content = f.read()
        self.messages = self.create_messages(content)
        return self._call_openai(self.messages)
