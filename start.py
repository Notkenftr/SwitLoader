from swit.bootstrap.bootstrap import bootstrap

if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    bootstrap()
