import json
import shutil
import subprocess
from pathlib import Path

swit_repo = "https://github.com/Notkenftr/SwitLoader"


def update_swit():
    print(f"checking {swit_repo}")

    root = Path(__file__).parents[1]
    tmp = Path("/tmp/SwitLoader")

    if tmp.exists():
        shutil.rmtree(tmp)

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            swit_repo,
            str(tmp),
        ],
        check=True,
    )

    try:
        with open(tmp / "swit" / "meta.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

        swit_path = metadata["swit_path"]

        for path in swit_path:
            source = tmp / path
            destination = root / path

            if not source.exists():
                print(f"skip: {path}")
                continue

            if source.is_dir():
                if destination.exists():
                    shutil.rmtree(destination)

                shutil.copytree(source, destination)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

            print(f"updated: {path}")

    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    update_swit()
