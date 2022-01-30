

import discord
import aiohttp
import random
from config import MAIN_COLOR


async def check_for_images(url, subreddit, embed_title):
    if ".png" in url or ".jpg" in url:
        return discord.Embed(title=embed_title, color=MAIN_COLOR).set_image(url=url)
    else:
        await pick_random_url_from_reddit(subreddit, embed_title)


async def pick_random_url_from_reddit(subreddit, embed_title):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f'https://www.reddit.com/r/{subreddit}/new.json?sort=hot') as r:
            res = await r.json()
            try:
                url = res['data']['children'][random.randint(0, 20)]['data']['url']
            except IndexError:
                return pick_random_url_from_reddit(subreddit, embed_title)
            return await check_for_images(url, subreddit, embed_title)
