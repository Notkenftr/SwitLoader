import argparse

from cli.build import build
from cli.build_workspace import build_workspace
from cli.make_pack import make_pack
from cli.update_swit import update_swit


def main():
    parser = argparse.ArgumentParser(description="SwitLoader CLI Tool")

    parser.add_argument("--setup-workspace", action="store_true", help="Scaffold a new module workspace")
    parser.add_argument("--pack-bot", action="store_true", help="Package bot into distribution zip/tar")
    parser.add_argument("--build", action="store_true", help="Prepare build tools and packages")
    parser.add_argument("--update", action="store_true", help="Update Swit framework from upstream repository")
    args = parser.parse_args()

    if not any([args.setup_workspace, args.pack_bot, args.build, args.update]):
        parser.print_help()
        return

    if args.setup_workspace:
        build_workspace()

    if args.pack_bot:
        make_pack()

    if args.build:
        build()

    if args.update:
        update_swit()


if __name__ == "__main__":
    main()
