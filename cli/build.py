import subprocess
import sys

package_for_build = ["rope","pipdeptree"]


def build():
    print("Preparing to build...")
    for package in package_for_build:
        subprocess.call([sys.executable, "-m", "pip", "install", package])
