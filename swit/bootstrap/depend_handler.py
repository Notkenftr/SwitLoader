from swit.api.utils.package import install_package
from swit.api.utils.path_api import PathAPI

with open(PathAPI.join_path("requirements.txt"),'r',encoding='utf-8') as f:
    dependencies = f.readlines()

def depend_handler():
    for dependency in dependencies:
        package = dependency.split("==")[0].strip()
        if not package:
            continue
        install_package(package)