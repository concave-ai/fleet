from typing import List

from openai import OpenAI
from pydantic import Field, BaseModel

from fleet.agents.base.base import OpenAIAgent

SYSTEM_PROMPT = """You are an smart autonomous AI assistant.
Your task is to locate the code relevant to an issue.
Let's start with the first step. Generate some search keywords for finding relevant code in preparation for the next phase.

# Instructions:

1. Understand The Issue:
Read the <issue> tag to understand the issue. just this repo caused the bug.

2. Review codebase tokens:
Examine the <tokens> tag to see the project's tokens, generated from function and class names.

3. Consider the Necessary Keywords:
Determine if specific file types, directories, function or class names, or code patterns are mentioned in the issue.
If possible, you should accurately select keywords from <tokens>.
You can return up to ten keywords.
"""


class KeywordExtractRes(BaseModel):
    keywords: List[str] = Field(description="List of keywords to search for.")


# keyword_extract
class KeywordExtract(OpenAIAgent):
    name = "KeywordExtract"
    responseType = KeywordExtractRes

    def __init__(self, ctx, tokens):
        super().__init__(ctx=ctx)
        self.tokens = tokens

    def create_messages(self):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"<issue>{self.ctx.issue}</issue>\n<tokens>\n{self.tokens}</tokens>"},
        ]

    def run(self):
        messages = self.create_messages()
        self._call_openai(messages)
