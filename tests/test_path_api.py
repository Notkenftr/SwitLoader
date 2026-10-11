from pathlib import Path

from swit.api.utils.path_api import PathAPI


def test_path_api_get_root():
    root = PathAPI.get_root()
    assert isinstance(root, Path)
    assert root.exists()


def test_path_api_join_path_create_parent(tmp_path):
    # Test that create_parent creates parent dir, but does NOT create the file as directory
    file_path = PathAPI.join_path("test_dir_sample", "sample_file.json", create_parent=True)
    try:
        assert file_path.parent.exists()
        assert file_path.parent.is_dir()
        assert not file_path.exists()
    finally:
        if file_path.parent.exists():
            file_path.parent.rmdir()
