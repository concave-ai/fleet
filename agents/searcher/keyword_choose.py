from typing import List, Optional

from openai import OpenAI
from openai.types.chat import ParsedChatCompletion
from pydantic import Field, BaseModel

from agents.base.base import Agent, OpenAIAgent

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


class KeywordChooseResponse(BaseModel):
    keywords: List[str] = Field(description="List of keywords to search for.")


class KeywordChoose(OpenAIAgent):
    def __init__(self, ctx, tokens):
        super().__init__(
            name="KeywordChoose",
            ctx=ctx,
            responseType=KeywordChooseResponse
        )
        self.tokens = tokens

    def create_messages(self):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"<issue>{self.ctx.issue}</issue>\n<tokens>\n{self.tokens}</tokens>"},
        ]

    def run(self):
        client = OpenAI()
        self.messages = self.create_messages()
        completion = client.beta.chat.completions.parse(
            model=self.ctx.model,
            messages=self.messages,
            response_format=KeywordChooseResponse,
        )
        self.set_response(completion)
        if self.ctx.trace:
            self.save_log()
