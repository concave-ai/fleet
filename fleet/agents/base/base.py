import json
import datetime
import os.path

from loguru import logger
from openai import OpenAI
from openai.types.chat import ParsedChatCompletion

from fleet.agents.base.state import State
from fleet.context import Context

# gpt-4o-2024-08-06  $2.50 / 1M input tokens
MODAL_PRICE_PER_TOKEN = {
    "gpt-4o-2024-08-06": 2.5/1e6,
    "gpt-4o-mini": 0.15/1e6
}

class Agent:
    request = None
    response = None
    responseType = None
    name = ""

    def __init__(self, ctx: Context):
        self._response = None
        self.ctx = ctx
        self.metadata = {
        }

    def save_log(self):
        d = datetime.datetime.now()
        logs_path = os.path.abspath(f"{self.ctx.work_dir}/logs/{self.ctx.task_id}/agents/{self.name}")
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        path = f"{logs_path}/{d.isoformat()}.json"
        with open(path, "w") as f:
            json.dump(self.dump(), f, indent=2)
        logger.info(f"Log saved to {path}")

    def dump(self):
        return {
            "name": self.name,
            "model": self.ctx.model,
            "metadata": self.metadata,
            "issue": self.ctx.issue,
            "request": self.request.model_dump(),
            "response": self.response.model_dump()
        }

    def after_run(self):
        if self.ctx.trace:
            self.save_log()

    def load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
            self.name = data["name"]
            self.metadata = data["metadata"]
            self.ctx.model = data["model"]
            self.ctx.issue = data["issue"]
            self.request = self.responseType(**data["request"])
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
        return self.response

    def _call_openai(self, messages):
        self.messages = messages
        client = OpenAI()
        completion = client.beta.chat.completions.parse(
            model=self.ctx.model,
            messages=messages,
            response_format=self.responseType,
        )
        res = self.set_response(completion)
        self.after_run()
        self.metadata["token_count"] = completion.usage.total_tokens
        self.metadata["cost"] =completion.usage.total_tokens * MODAL_PRICE_PER_TOKEN[self.ctx.model]
        return res

    # input {a: b, c: d}
    # output "<a>b</a>\n<c>d</c>"
    def content_template(self, **kwargs):
        return "\n".join([f"<{k}>{v}</{k}>" for k, v in kwargs.items()])

    def dump(self):
        if self.responseType is None:
            raise ValueError("responseType is not defined")

        base = super().dump()
        base["messages"] = self.messages
        base["completion"] = self.completion.model_dump()
        base["response"] = self.response.model_dump()
        base["metadata"]["token_count"] = self.metadata.get("token_count", 0)
        base["metadata"]["cost"] = self.metadata.get("price", 0)
        return base
