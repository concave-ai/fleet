from concave.internal.datasets.swe_bench.constants import SPECS_PYTEST
from concave.internal.workspace.config import Config
from concave.internal.workspace.manager import WorkspaceManager
from datasets import load_dataset


def prepare(swe_bench_id: str):
    ds = load_dataset("princeton-nlp/SWE-bench_Verified")
    rows = ds.get("test")
    filter_rows = [row for row in rows if swe_bench_id in row["instance_id"]]
    if len(filter_rows) == 0:
        raise ValueError(f"Could not find {swe_bench_id} in SWE-bench_Verified")
    row = filter_rows[0]

    spec = SPECS_PYTEST[row["version"]]
    setup = [spec["install"]]
    if "pip_packages" in spec:
        setup.append('pip install {}'.format(
            " ".join(spec["pip_packages"])
        ))

    config = Config(
        name=swe_bench_id,
        language='python',
        version=f'{spec["python"]}-alpine3.13',
        codebase=f'github.com/pytest-dev/pytest/commit/{row["base_commit"]}',
        project_setup=setup
    )

    manager = WorkspaceManager()
    ws = manager.create(config)

    code = ws.execute("echo '1' > /tmp/version.txt")
    print("exec code", code)
    version = ws.open("/tmp/version.txt").read()
    print(f"Python version: {version}")


prepare("pytest-dev__pytest-5262")
