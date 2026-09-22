from pathlib import Path

root = Path(__file__).parents[3]


class PathAPI:
    """
    Provide utilities for resolving paths relative to the project root.
    """

    @staticmethod
    def get_root() -> Path:
        """
        Get the root directory of the project.

        :return: The project root path.
        """
        return root

    @staticmethod
    def join_path(*args, create_parent=False) -> Path:
        """
        Join path components with the project root directory.

        If ``create_parent`` is enabled, the resulting directory and all
        of its parent directories are created if they do not already exist.

        :param args: Path components to join with the project root.
        :param create_parent: Whether to create the resulting directory
            and its parent directories.
        :return: The resulting path.
        """
        if create_parent:
            Path(root, *args).mkdir(parents=True, exist_ok=True)

        return Path(root, *args)