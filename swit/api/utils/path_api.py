from pathlib import Path

root = Path(__file__).parents[3]


class PathAPI:
    @staticmethod
    def get_root() -> Path:
        return root

    @staticmethod
    def join_path(*args) -> Path:
        return Path(root,*args)