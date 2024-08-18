from concave.internal.workspace.workspace import Workspace
from openai.types import ChatModel

from fleet.utils.searcher.searcher import SymbolSearcher


class Context:
    workspace: Workspace
    searcher: SymbolSearcher
    def __init__(self,
                 model: ChatModel = "gpt-4o-mini",
                 issue: str = "",
                 task_id: str = "",
                 work_dir: str = ".",
                 trace: bool = False,
                 file_context: str = ""):
        self.trace= trace
        self.issue = issue
        self.task_id = task_id
        self.file_context = file_context
        self.model = model
        self.work_dir = work_dir


    def __str__(self):
        return f"Context(issue={self.issue}, file_context={self.file_context})"
