import json
import datetime
import os.path

from openai.types.chat import ParsedChatCompletion

from fleet.context import Context


class Agent:
    request = None
    response = None

    def __init__(self, name: str, ctx: Context, responseType=None):
        self._response = None
        self.name = name
        self.ctx = ctx
        self.responseType = responseType

    def save_log(self):
        d = datetime.datetime.now()
        logs_path = os.path.abspath(f"{self.ctx.work_dir}/logs/{self.name}/{self.ctx.task_id}")
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        path = f"{logs_path}/{d.isoformat()}.json"
        with open(path, "w") as f:
            json.dump(self.dump(), f, indent=2)
        print(f"Log saved to {path}")



    def dump(self):
        return {
            "model": self.ctx.model,
            "issue": self.ctx.issue,
            "request": self.request,
            "response": self.response.model_dump()
        }

    def load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
            self.ctx.model = data["model"]
            self.ctx.issue = data["issue"]
            self.request = data["request"]
            self.response = self.responseType(**data["response"])
        return data


class OpenAIAgent(Agent):
    def __init__(self, name: str, ctx: Context, responseType=None):
        super().__init__(name, ctx, responseType)
        self.messages = []

    def load(self, path):
        data = super().load(path)
        self.messages = data["messages"]
        self.completion = ParsedChatCompletion(**data["completion"])
        self.response = self.responseType(**data["response"])

    def set_response(self, completion):
        self.completion = completion
        self.response = completion.choices[0].message.parsed

    def dump(self):
        base = super().dump()
        base["messages"] = self.messages
        base["completion"] = self.completion.model_dump()
        base["response"] = self.response.model_dump()
        return base

