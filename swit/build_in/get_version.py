import json
from pathlib import Path


def get_swit_version():
    root = Path(__file__).parents[2]

    with open(root / "swit" / "meta.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["swit-version"]


if __name__ == "__main__":
    get_swit_version()
