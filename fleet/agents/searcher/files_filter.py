import json
from typing import List, Optional

from pydantic import BaseModel, Field

from fleet.agents.base.base import Agent, OpenAIAgent

SYSTEM_PROMPT = """You are an autonomous AI assistant tasked with finding relevant code in an existing codebase based on a reported issue. 
Your task is to find the relative files in the keyword_search_results.

# What You Get:

* <issue>: Has the problem report.
* <keyword_search_results>: search results for keywords, and their matching files.

# What You Do:

1. Read the Problem:
Carefully read the reported issue within the <issue> tag.

2. Look at Keyword Search Results:
2.1. Think about each keyword and its matching files in the <keyword_search_results> tag.
2.2. Consider if these files are related to the reported problem.
2.3. Be aware that some unrelated files and keywords may also be in the keyword_search_results. Carefully check each one.
2.4. The issues will not be complex, meaning the related files and content will not be extensive.  

3. Answer Using the Function:
give some file paths that you think are related to the problem report. Sort them by how relevant you think they are.
limit the number of files to 6 or less.


Think step by step and write down your thoughts in the scratch_pad field.
"""


class FilesFilterRes(BaseModel):
    scratch_pad: str = Field(description="Your thoughts on how to identify the relevant code and why.")
    file_paths: List[str] = Field(description="List of file paths to relate to the issue. sorted by relevance. max: 6 paths.")


class FilesFilterReq(BaseModel):
    keyword_search_results: dict


class FilesFilter(OpenAIAgent):
    name = "FilesFilter"
    response: Optional[FilesFilterRes]
    requestType = FilesFilterReq
    responseType = FilesFilterRes

    def __init__(self, ctx, req: FilesFilterReq):
        super().__init__(ctx=ctx)
        self.request = req

    def create_messages(self):
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": self.content_template(
                 issue=self.ctx.issue,
                 keyword_search_results=self.request.keyword_search_results
             )},
        ]

    def run(self):
        self.messages = self.create_messages()
        self._call_openai(self.messages)
