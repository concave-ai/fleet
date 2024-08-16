import json
from typing import Optional

from pydantic import BaseModel, Field

from fleet.agents.base.base import Agent


class FilesKeywordSearchRes(BaseModel):
    results: dict[str, list[str]] = Field(
        description="key is the keyword, value is the list of paths where the keyword is found.")


class FilesKeywordSearchReq(BaseModel):
    tokens: list[str]


def str_to_jsonl(raw):
    return [json.loads(l) for l in raw.split('\n') if l]


class FilesKeywordSearch(Agent):
    name = "FilesKeywordSearch"
    responseType = FilesKeywordSearchRes
    response = Optional[FilesKeywordSearchRes]

    def __init__(self, ctx, req: FilesKeywordSearchReq):
        super().__init__(ctx)
        self.response = None
        self.request = req

    def get_cmd(self):
        args = [f"-e '{t}'" for t in self.request.tokens]
        return f"rg --json -n -w {' '.join(args)} --glob '*.py' src/"

    def run_from_jsonl(self, path):
        with open(path) as f:
            rows = [json.loads(l) for l in f.readlines()]
        self.response = FilesKeywordSearchRes(results=self.parse(rows))
        if self.ctx.trace:
            self.save_log()

    def run(self):
        cmd = self.get_cmd()
        code, out = self.ctx.workspace.exec(["sh", "-c", cmd])
        rows = str_to_jsonl(out)

        self.response = FilesKeywordSearchRes(results=self.parse(rows))
        self.after_run()
        return self.response

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
