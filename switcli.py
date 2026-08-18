import argparse

from cli.build_workspace import build_workspace


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--setup-workspace",
        action="store_true"
    )

    args = parser.parse_args()

    if args.setup_workspace:
        build_workspace()


if __name__ == "__main__":
    main()