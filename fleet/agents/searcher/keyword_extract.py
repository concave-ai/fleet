from typing import List

from pydantic import Field, BaseModel

from fleet.agents.base.base import OpenAIAgent

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing codebase based on a reported issue.
your task is find some relevant keywords to search for in the codebase.

# Instructions:

1. Understand The Issue:
Read the <issue> tag to understand the issue. just this repo caused the bug.

2. Review codebase/repo tokens:
Examine the <repo_tokens> tag to see the repo's tokens, generated from function and class names.

3. Consider the Necessary Keywords:
Determine if specific file types, directories, function or class names, or code patterns are mentioned in the issue.
If possible, you should accurately select keywords from <repo_tokens>.
You can return not more than ten keywords.
"""


class KeywordExtractReq(BaseModel):
    repo_tokens: List[str] = Field(description="List of tokens generated from function and class names.")


class KeywordExtractRes(BaseModel):
    keywords: List[str] = Field(description="List of keywords to search for. max 10 keywords.")


# keyword_extract
class KeywordExtract(OpenAIAgent):
    name = "KeywordExtract"
    responseType = KeywordExtractRes
    requestType = KeywordExtractReq

    def __init__(self, ctx, req=KeywordExtractReq):
        super().__init__(ctx=ctx)
        self.request = req

    def create_messages(self):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": self.content_template(
                 issue=self.ctx.issue,
                 repo_tokens=self.request.repo_tokens
             )}
        ]

    def run(self) -> KeywordExtractRes:
        messages = self.create_messages()
        return self._call_openai(messages)
