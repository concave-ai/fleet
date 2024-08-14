from datasets import load_dataset

verified = load_dataset("princeton-nlp/SWE-bench_Verified")
ds = load_dataset("princeton-nlp/SWE-bench_Lite")

# get all pytest test cases
lite_rows = [row["instance_id"] for row in verified.get("test") if "pytest" in row["instance_id"]]
verified_rows = [row["instance_id"] for row in ds.get("test") if "pytest" in  row["instance_id"]]

print("lite")
for r in lite_rows:
    print(r)

print("verified")
for r in verified_rows:
    print(r)

rows = set(lite_rows) & set(verified_rows)
print(rows)
