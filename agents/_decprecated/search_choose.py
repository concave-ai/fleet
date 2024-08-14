from typing import List

from openai import OpenAI
from pydantic import BaseModel, Field

from fleet.context import Context

SYSTEM_PROMPT = """
You are an smart autonomous AI assistant.
"You are an autonomous AI assistant tasked with finding relevant code in an existing 
codebase based on a reported issue. Your task is to identify the relevant code spans in the provided search 
results and decide whether the search task is complete.

# Input Structure:

* <issue>: Contains the reported issue.
* <file_context>: Contains the context of already identified files and code spans.
* <search_results>: Contains the new search results with code divided into "code spans".

# Your Task:

1. Analyze User Instructions:
Carefully read the reported issue within the <issue> tag.

2. Review Current Context:
Examine the current file context provided in the <file_context> tag to understand already identified relevant files.

3. Process New Search Results:
3.1. Thoroughly analyze each code span in the <search_results> tag.
3.2. Match the code spans with the key elements, functions, variables, or patterns identified in the reported issue.
3.3. Evaluate the relevance of each code span based on how well it aligns with the reported issue and current file context.
3.4. If the issue suggests new functions or classes, identify the existing code that might be relevant to be able to implement the new functionality.
3.5. Review entire sections of code, not just isolated spans, to ensure you have a complete understanding before making a decision. It's crucial to see all code in a section to accurately determine relevance and completeness.
3.6. Verify if there are references to other parts of the codebase that might be relevant but not found in the search results. 
3.7. Identify and extract relevant code spans based on the reported issue. 
3.8. You will select code spans from the search_results that are worth further investigation.

4. Respond Using the Function:
Use the Identify function to provide your response.
You will select code spans from the search_results that are worth deeper insight.


Think step by step and write out your thoughts in the scratch_pad field.
"""


class Indentify(BaseModel):
    files: List[str] = Field(description="List of files worth deeper insight.")
    scratch_pad: str = Field(
        description="Your thoughts on how to identify the relevant code and why."
    )


class SearchResultChoose:
    def __init__(self, context: Context, search_results: str):
        self.context = context
        self.search_results = search_results

    def run(self):
        client = OpenAI()
        completion = client.beta.chat.completions.parse(
            # model="gpt-4o-2024-08-06",
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",
                 "content": f"<issue>{self.context.issue}</issue><search_results>{self.search_results}</search_results>"},
            ],
            response_format=Indentify,
        )
        print("out")
        print(completion.model_dump_json(indent=4))
