import argparse

from cli.build_workspace import build_workspace
from cli.make_pack import make_pack
from cli.update_swit import update_swit


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--setup-workspace", action="store_true")
    parser.add_argument("--pack-bot", action="store_true")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    if args.setup_workspace:
        build_workspace()

    if args.pack_bot:
        make_pack()

    if args.update:
        update_swit()


if __name__ == "__main__":
    main()
