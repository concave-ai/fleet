import json
from typing import List, Optional

from pydantic import BaseModel, Field

from fleet.agents.base.base import Agent, OpenAIAgent

SYSTEM_PROMPT = """You are an AI helper with the job of finding important code in a big program based on a problem report. 
Your task is to find the right pieces of files name in the search results.

# What You Get:

* <issue>: Has the problem report.
* <keysearch_results>: Has search results for keywords and their matching files.

# What You Do:

1. Read the Problem:
Look carefully at the problem report in the <issue> tag.

2. Look at Keyword Search Results:
2.1. Think about each keyword and its matching files in the <keyword_search_results> tag.
2.2. Consider if these files are related to the reported problem.
2.3. Be aware that some unrelated files and keywords may also be in the keyword_search_results. Carefully check each one.

3. Answer Using the Function:
give some files that you think are related to the problem report. Sort them by how relevant you think they are.
limit the number of files to 6 or less.


Think step by step and write down your thoughts in the scratch_pad field.
"""


class FilesFilterRes(BaseModel):
    scratch_pad: str = Field(description="Your thoughts on how to identify the relevant code and why.")
    files: List[str] = Field(description="List of files to relate to the issue. sorted by relevance. max: 6 files.")


class FilesFilter(OpenAIAgent):
    name = "FilesFilter"
    response: Optional[FilesFilterRes]
    responseType = FilesFilterRes

    def __init__(self, ctx, search_results):
        super().__init__(ctx=ctx)
        self.search_results = search_results

    def create_messages(self):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"<issue>{self.ctx.issue}</issue>\n<keyword_search_results>\n{json.dumps(self.search_results)}</keyword_search_results>"},
        ]

    def run(self):
        self.messages = self.create_messages()
        self._call_openai(self.messages)
