import json
from typing import Optional

from pydantic import BaseModel, Field
from openai import OpenAI

from fleet.context import Context

SYSTEM_PROMPT = """You are an smart autonomous AI assistant.
Your task is to locate the code relevant to an issue.

# Instructions:

1. Understand The Issue:
Read the <issue> tag to understand the issue. just this repo caused the bug.

2. Review Current File Context:
Examine the <file_context> tag to see which files and code spans have already been identified.
If you believe that all relevant files have been identified, you can finish the search by setting complete to true.

3. Consider the Necessary Search Parameters:
Determine if specific file types, directories, function or class names or code patterns are mentioned in the issue.
If you can you should always try to specify the search parameters as accurately as possible.
You can do more than one search request at the same time so you can try different search parameters to cover all possible relevant code.
do not search tests, logs code 


4. Ensure Search Parameter:
- `search(key: string)`: 
    With the search function, you can search for any code snippet. If a class or method is found during the search, the search function will also provide the corresponding reference information.
- `lookup(file, start_line, end_line)`: 
    With the lookup function, you can search for a specific code span in a file.

5. If you have enough info, you can finish search by setting complete to true.
"""

SEARCH_FUNCTIONS_FEW_SHOT_OPENAI_FUNC = """
6. Execute the Search function:
Use the Search function with the search parameters and your thoughts on how to approach this task.
Think step by step and write out your thoughts in the thoughts field.

Examples:
User:
The file uploader intermittently fails with "TypeError: cannot unpack non-iterable NoneType object". This issue appears sporadically during high load conditions..

AI Assistant:
search("TypeError: cannot unpack non-iterable NoneType object",)

User:
There's a bug in the PaymentProcessor class where transactions sometimes fail to log correctly, resulting in missing transaction records.

AI Assistant:
search("PaymentProcessor")


User:
The generate_report function sometimes produces incomplete reports under certain conditions. This function is part of the reporting module. Locate the generate_report function in the reports directory to debug and fix the issue.

AI Assistant:
search("generate_report")

User:
The extract_data function in HTMLParser throws an "AttributeError: 'NoneType' object has no attribute 'find'" error when parsing certain HTML pages.

AI Assistant:
Search(HTMLParser)
Search(extract_data)

User:
The database connection setup is missing SSL configuration, causing insecure connections.

Here's the stack trace of the error:

File "/opt/app/db_config/database.py", line 45, in setup_connection
    engine = create_engine(DATABASE_URL)
File "/opt/app/db_config/database.py", line 50, in <module>
    connection = setup_connection()

AI Assistant:
search("create_engine(DATABASE_URL)")
lookup("db_config/database.py", 45, 50)
"""


class Search(BaseModel):
    query: str
    path: Optional[str] = Field(description="endswith file path")
    scratch_pad: str = Field(description="Your thoughts on how to approach this task.")


class Lookup(BaseModel):
    file: str
    start_line: int
    end_line: int


class SearchRes(BaseModel):
    complete: bool
    calls: list[Search | Lookup]


class SearchAgent:

    def __init__(self, context: Context):
        self.context = context

    def run(self):
        client = OpenAI()
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + SEARCH_FUNCTIONS_FEW_SHOT_OPENAI_FUNC},
                {"role": "user", "content": f"<issue>{self.context.issue}</issue>"},
            ],
            response_format=SearchRes,
        )
        print("out")
        print(completion.model_dump_json(indent=4))
