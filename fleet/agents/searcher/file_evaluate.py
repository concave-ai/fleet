from typing import Optional

from pydantic import BaseModel, Field

from fleet.agents.base.base import OpenAIAgent

SYSTEM_PROMPT = """
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
    relavant_symbols: list[str] = Field(
        description="If the file is relevant, suggest some symbol that caused the issue. "
                    "symbol can be a function name or class name. "
                    "limit 10 symbols."
    )

    root_cause_symbol: list[str] = Field(
        description="If the file is root cause, suggest some symbol that caused the issue. "
                    "symbol can be a function name or class name. "
                    "this str list no size limit."
    )


class FileEvaluate(OpenAIAgent):
    name = "FileEvaluate"
    response: Optional[FileEvaluateRes]
    responseType = FileEvaluateRes

    def __init__(self, ctx, file_path):
        self.file_path = file_path
        super().__init__(ctx=ctx)

    def create_messages(self, content):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"""<issue>{self.ctx.issue}</issue>
             <file>source: {self.file_path}
             {content}
             </file>
             """},

        ]

    def run(self):
        f = self.ctx.workspace.open(self.file_path)
        content = f.read()
        self.messages = self.create_messages(content)
        self._call_openai(self.messages)
