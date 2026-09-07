import importlib.metadata
import importlib.util
import os
import subprocess
import sys
import tarfile
import zipfile
import zlib
from pathlib import Path

START_PACK_FILE = """import os
import sys
from pathlib import Path


def switch_venv():
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        target_venv = (Path(__file__).resolve().parent / ".venv").resolve()

        if sys.platform == "win32":
            venv_python = target_venv / "Scripts" / "python.exe"
        else:
            venv_python = target_venv / "bin" / "python"

        if not venv_python.exists():
            raise FileNotFoundError(
                f"Python not found: {venv_python}. "
                "Please create .venv and install packages via 'pip install -r requirements.txt'"
            )

        os.environ["VIRTUAL_ENV"] = str(target_venv)
        bin_dir = str(venv_python.parent)
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"

        os.execv(str(venv_python), [str(venv_python)] + sys.argv)


if __name__ == "__main__":
    switch_venv()

    import logging
    from swit.bootstrap.bootstrap import bootstrap

    bootstrap()
"""


def get_root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def setup_venv():
    in_venv = sys.prefix != sys.base_prefix

    if not in_venv:
        root_dir = get_root_dir()
        venv_dir = root_dir / ".venv"

        if sys.platform == "win32":
            venv_python = venv_dir / "Scripts" / "python.exe"
        else:
            venv_python = venv_dir / "bin" / "python"

        if not venv_dir.exists():
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

        os.execv(str(venv_python), [str(venv_python)] + sys.argv)


def ensure_pip():
    if importlib.util.find_spec("pip") is None:
        subprocess.run(
            [sys.executable, "-m", "ensurepip", "--upgrade"],
            check=True,
        )

def get_package():
    result = {}
    dists = importlib.metadata.distributions()
    for dist in sorted(dists, key=lambda x: x.name.lower()):
        result[dist.name] = f"{dist.name}=={dist.version}"
    return result


def install_packages(packages_dict: dict):
    ensure_pip()
    pkg_list = list(packages_dict.values())
    if not pkg_list:
        return
    subprocess.run([sys.executable, "-m", "pip", "install", *pkg_list], check=True)


def create_root_files(packages_dict: dict):
    root_dir = get_root_dir()

    start_file_path = root_dir / "run.py"
    with open(start_file_path, "w", encoding="utf-8") as f:
        f.write(START_PACK_FILE.lstrip())

    req_file_path = root_dir / "requirements.txt"
    with open(req_file_path, "w", encoding="utf-8") as f:
        f.writelines(f"{pkg_spec}\n" for pkg_spec in packages_dict.values())


def archive_project():
    root_dir = get_root_dir()
    build_dir = root_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    ignore_dirs = {".git", ".idea", "__pycache__", "build"}

    files_to_pack = []
    for file_path in root_dir.rglob("*"):
        rel_path = file_path.relative_to(root_dir)
        if any(part in ignore_dirs for part in rel_path.parts):
            continue
        if file_path.is_file():
            files_to_pack.append((file_path, rel_path))

    zip_file = build_dir / "swit-pack.zip"
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path, rel_path in files_to_pack:
            zipf.write(file_path, rel_path)

    tar_path = build_dir / "temp.tar"
    zlib_file = build_dir / "swit-pack.tar.zlib"

    with tarfile.open(tar_path, "w") as tar:
        for file_path, rel_path in files_to_pack:
            tar.add(file_path, arcname=rel_path)

    with open(tar_path, "rb") as f_in, open(zlib_file, "wb") as f_out:
        f_out.write(zlib.compress(f_in.read()))

    tar_path.unlink()

    rar_file = build_dir / "swit-pack.rar"
    rar_cmd = "rar" if sys.platform != "win32" else "rar.exe"

    try:
        cmd = [rar_cmd, "a", "-r", str(rar_file), *[str(f[0]) for f in files_to_pack]]
        subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass


def make_pack():
    setup_venv()
    packages = get_package()
    install_packages(packages)
    create_root_files(packages)
    archive_project()


if __name__ == "__main__":
    make_pack()
