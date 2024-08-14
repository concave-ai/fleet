import json
import datetime
import os.path

from openai import OpenAI
from openai.types.chat import ParsedChatCompletion

from fleet.agents.base.state import State
from fleet.context import Context


class Agent:
    request = None
    response = None
    responseType = None
    name = ""

    def __init__(self, ctx: Context):
        self._response = None
        self.ctx = ctx

    def save_log(self):
        d = datetime.datetime.now()
        logs_path = os.path.abspath(f"{self.ctx.work_dir}/logs/{self.ctx.task_id}/{self.name}")
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        path = f"{logs_path}/{d.isoformat()}.json"
        with open(path, "w") as f:
            json.dump(self.dump(), f, indent=2)
        print(f"Log saved to {path}")

    def dump(self):
        return {
            "name": self.name,
            "model": self.ctx.model,
            "issue": self.ctx.issue,
            "request": self.request,
            "response": self.response.model_dump()
        }

    def load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
            self.name = data["name"]
            self.ctx.model = data["model"]
            self.ctx.issue = data["issue"]
            self.request = data["request"]
            self.response = self.responseType(**data["response"])
        return data

    @classmethod
    @property
    def state(cls):
        return State(cls.name)


class OpenAIAgent(Agent):
    responseType = None
    def __init__(self, ctx: Context):
        super().__init__(ctx)
        self.messages = []

    def load(self, path):
        data = super().load(path)
        self.messages = data["messages"]
        self.completion = ParsedChatCompletion(**data["completion"])
        self.response = self.responseType(**data["response"])

    def set_response(self, completion):
        self.completion = completion
        self.response = completion.choices[0].message.parsed

    def _call_openai(self, messages):
        self.messages = messages
        client = OpenAI()
        completion = client.beta.chat.completions.parse(
            model=self.ctx.model,
            messages=messages,
            response_format=self.responseType,
        )
        self.set_response(completion)
        if self.ctx.trace:
            self.save_log()
        return completion

    def dump(self):
        if self.responseType is None:
            raise ValueError("responseType is not defined")

        base = super().dump()
        base["messages"] = self.messages
        base["completion"] = self.completion.model_dump()
        base["response"] = self.response.model_dump()
        return base
