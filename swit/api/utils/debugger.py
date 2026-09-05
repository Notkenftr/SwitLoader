from swit.app import Swit


async def object_information(obj, swit: Swit):
    logger = swit.get_logger()
    await logger.info(f"{'==' * 15} Object: {obj}{'==' * 15}")
    await logger.info(f"Object ID: {obj.id}")
    await logger.info(f"Object Parent: {obj.parent}")
    await logger.info(f"Type: {type(obj)}")
    for name in dir(obj):
        try:
            await logger.info(f"{name}: {getattr(obj, name)}")
        except Exception as e: # noqa: BLE001
            await logger.info(f"{name}: <error: {e}>")

    await logger.info(f"{'==' * 15} End {'==' * 15}")
