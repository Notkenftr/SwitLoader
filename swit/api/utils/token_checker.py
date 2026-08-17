import aiohttp


async def token_checker(discord_bot_token):
    """
    This function checks whether the Discord bot token is valid.

    status
        - True: Valid token
        - False: Invalid token

    :param discord_bot_token: bot token
    :return: (status,data)
    """

    headers = {
        "Authorization": f"Bot {discord_bot_token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/v10/users/@me",
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return True, data

            if response.status == 401:
                return False, "Invalid token"

            if response.status == 429:
                return False, "Rate limited"

            return False, f"HTTP {response.status}"