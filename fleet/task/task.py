import json
import os
import time
from datetime import datetime

from loguru import logger
from pydantic import BaseModel

from fleet.context import Context


class TaskTelemetry:

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.spans = []
        self.total_cost = 0

    def add_span(self, span, cost=0):
        self.total_cost += cost
        self.spans.append(span)

    def save(self):
        logs_path = os.path.abspath(f"{self.ctx.work_dir}/logs/{self.ctx.task_id}")
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        path = f"{logs_path}/telemetry.json"
        with open(path, "w") as f:
            json.dump({
                "total_cost": self.total_cost,
                "task_id": self.ctx.task_id,
                "model": self.ctx.model,
                "spans": self.spans
            }, f, indent=2)
        logger.info(f"Saving telemetry, {path}")


class Task:

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.telemetry = TaskTelemetry(ctx)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.telemetry.save()

    def run(self, agent_class, **kwargs):
        start = time.time()
        agent = agent_class(self.ctx, **kwargs)
        response: BaseModel = agent.run()

        raw = agent.dump()
        cost = 0
        if raw["metadata"]:
            cost = raw["metadata"].get("cost", 0)


        self.telemetry.add_span({
            "name": agent.name,
            "metadata": {
                "start": datetime.fromtimestamp(start).isoformat(),
                "usage": f"{1000 * (time.time() - start)} ms"
            },
            "request": raw["request"],
            "response": raw["response"]
        }, cost)

        return response
