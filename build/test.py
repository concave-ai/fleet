import json
with open("/Users/justwph/Downloads/20230726_cosine_genie.cosine-genie-v4-25-07-24.json") as f:
    data = json.load(f)

ides = data["resolved_ids"]
problems = []

for id in ides:
    repo, pr = id.split("__")
    problems.append({
        "repo": repo,
        "pr": pr
    })

print(problems)