import json
from typing import Optional

from pydantic import BaseModel, Field

from agents.base.base import Agent


class KeywordSearchResponse(BaseModel):
    results: dict[str, list[str]] = Field(
        description="key is the keyword, value is the list of paths where the keyword is found.")


class KeywordSearch(Agent):
    response: Optional[KeywordSearchResponse]
    def __init__(self, ctx, tokens):
        super().__init__("KeywordSearch", ctx, KeywordSearchResponse)
        self.tokens = tokens
        self.response = None

    def get_cmd(self):
        args = [f"-e '{t}'" for t in self.tokens]

        return f"rg --json -n -w {' '.join(args)} --glob '*.py' src/"

    def run_from_jsonl(self, path):
        with open(path) as f:
            rows = [json.loads(l) for l in f.readlines()]
        self.response = KeywordSearchResponse(results=self.parse(rows))
        if self.ctx.trace:
            self.save_log()

    def parse(self, rows):
        results = {
        }
        for row in rows:
            if row['type'] != 'match':
                continue
            path = row['data']['path']['text']
            for m in row['data']['submatches']:
                match = m['match']['text']
                if match not in results:
                    results[match] = []
                results[match].append(path)
        for i in results:
            results[i] = list(set(results[i]))
        return results
