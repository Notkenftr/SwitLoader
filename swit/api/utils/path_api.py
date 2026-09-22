from pathlib import Path

root = Path(__file__).parents[3]


class PathAPI:
    @staticmethod
    def get_root() -> Path:
        return root

    @staticmethod
    def join_path(*args,create_parent = False) -> Path:
        if create_parent:
            Path(root,*args).mkdir(parents=True,exist_ok=True)
        return Path(root, *args)
