import json
import os

import requests
from datasets import load_dataset

benchs = [
    "20240620_sweagent_claude3.5sonnet",
    "20240402_sweagent_claude3opus",
    "20240402_sweagent_gpt4"
]

download_url = "https://raw.githubusercontent.com/swe-bench/experiments/main/evaluation/verified/{bench_name}/trajs/{task_id}.traj"


def download_task(bench_name, task_id):
    url = download_url.format(bench_name=bench_name, task_id=task_id)
    response = requests.get(url)
    if not os.path.exists(f"./{task_id}"):
        os.mkdir(f"./{task_id}")
    try:
        data = response.json()
        if "info" in data:
            if not data["info"]["submission"]:
                print(f"Task {bench_name}/{task_id} has no submission, {data['info']['exit_status']}")

            with open(f"./{task_id}/{bench_name}.patch", "w") as f:
                if not data["info"]["submission"]:
                    f.write("")
                    return
                f.write(data["info"]["submission"])
    except json.decoder.JSONDecodeError:
        print(f"Task {bench_name}/{task_id}  parse failed, {response.text}")


def get_all_pytest_ids():
    ds = load_dataset("princeton-nlp/SWE-bench_Verified")
    rows = ds.get("test")
    return [row["instance_id"] for row in rows if "pytest" in row["instance_id"]]


for task_id in get_all_pytest_ids():
    for bench in benchs:
        download_task(bench, task_id)
