import json
from typing import List

from openai import OpenAI
from pydantic import BaseModel, Field

from agents.base.base import Agent, OpenAIAgent

SYSTEM_PROMPT = """You are an AI helper with the job of finding important code in a big program based on a problem report. Your task is to find the right pieces of code in the search results and decide if the search is done.

# What You Get:

* <issue>: Has the problem report.
* <keysearch_results>: Has search results for keywords and their matching files.

# What You Do:

1. Read the Problem:
Look carefully at the problem report in the <issue> tag.

2. Look at Keyword Search Results:
2.1. Think about each keyword and its matching files in the <keysearch_results> tag.
2.2. Consider if these files are related to the reported problem.
2.3. Be aware that some unrelated files and keywords may also be in the keysearch_results. Carefully check each one.

3. Answer Using the Function:
Use the Identify function to give your answer.

Think step by step and write down your thoughts in the scratch_pad field.
"""


class RelativeFileResponse(BaseModel):
    scratch_pad: str = Field(description="Your thoughts on how to identify the relevant code and why.")
    files: List[str] = Field(description="List of files to relate to the issue. sorted by relevance.")


class RelativeFile(OpenAIAgent):
    def __init__(self, ctx, search_results):
        super().__init__(
            name="RelativeFile",
            ctx=ctx,
            responseType=RelativeFileResponse
        )
        self.search_results = search_results

    def create_messages(self):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"<issue>{self.ctx.issue}</issue>\n<keysearch_results>\n{json.dumps(self.search_results)}</keysearch_results>"},
        ]

    def run(self):
        client = OpenAI()
        self.messages = self.create_messages()
        completion = client.beta.chat.completions.parse(
            model=self.ctx.model,
            messages=self.messages,
            response_format=RelativeFileResponse,
        )
        self.set_response(completion)

        if self.ctx.trace:
            self.save_log()
