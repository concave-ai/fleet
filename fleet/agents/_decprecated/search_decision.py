from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from agents.base.base import Agent

SYSTEM_PROMPT = """
You will be provided a reported issue and the file context containing existing code from the project's git repository. 
Your task is to make a decision if the code related to a reported issue is provided in the file context. 

# Input Structure:

* <issue>: Contains the reported issue.
* <file_context>: The file context.

Instructions:

 * Analyze the Issue:
   * Review the reported issue to understand what functionality or bug fix is being requested.

 * Analyze File Context:
  * Examine the provided file context to identify if the relevant code for the reported issue is present.
  * If the issue suggests that code should be implemented and doesn't yet exist in the code, consider the task completed if relevant code is found that would be modified to implement the new functionality.
  * If relevant code in the file context points to other parts of the codebase not included, note these references.

 * Make a Decision:
  * Decide if the relevant code is found in the file context.
  * If you believe all existing relevant code is identified, mark the task as complete.
  * If the specific method or code required to fix the issue is not present, still mark the task as complete as long as the relevant class or area for modification is identified.
  * If you believe more relevant code can be identified, mark the task as not complete and provide your suggestions on how to find the relevant code.

Important:
 * You CANNOT change the codebase. DO NOT modify or suggest changes to any code.
 * Your task is ONLY to determine if the file context is complete. Do not go beyond this scope.
"""


class DecisionRes(BaseModel):

    scratch_pad: str = Field(
        description="Your thoughts on if the spans where relevant or not and if you found all relevant spans and can finish.."
    )

    relevant: bool = Field(
        description="Set to true if the relevant code have been identified.",
    )

    search_suggestions: Optional[str] = Field(
        description="Suggestions on how to find the relevant code not found in the file context.",
    )


class SearchDecision(Agent):
    def __init__(self, ctx, file_context: str):
        super().__init__(ctx)
        self.file_context = file_context

    def run(self):
        client = OpenAI()
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            # model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",
                 "content": f"<issue>{self.ctx.issue}</issue><file_context>{self.file_context}</file_context>"},
            ],
            response_format=DecisionRes,
        )
        print("out")
        print(completion.model_dump_json(indent=4))
