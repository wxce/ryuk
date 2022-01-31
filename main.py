from logging import basicConfig, INFO
from config import BOT_TOKEN, BOT_TOKEN_BETA, OWNERS
from utils.bot import ryuk
from os import environ
import discord
import os
import sys
basicConfig(level=INFO)
import asyncio


client = ryuk()



environ.setdefault("JISHAKU_HIDE", "1")
environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

@client.check
async def check_commands(ctx):
    if client.beta:
        if ctx.message.author.id not in OWNERS:
            return False  # if running beta version, then only allow owners
        return True
    if ctx.guild is None:
        return False
    g = await client.get_guild_config(ctx.guild.id)
    dc = g['disabled_cmds']
    dch = g['disabled_channels']
    dcc = g.get('disabled_categories', [])
    dcc_cogs = [client.get_cog(cog) for cog in dcc]
    return (ctx.command.name not in dc) and (ctx.channel.id not in dch) and (ctx.command.cog not in dcc_cogs)



@client.listen('on_global_commands_update')
async def on_global_commands_update(commands: list):
    print(f'{len(commands)} Global commands updated')


@client.listen('on_guild_commands_update')
async def on_guild_commands_update(commands: list, guild_id: int):
    print(f"{len(commands)} Guild commands updated for guild ID: {guild_id}")




async def mobile(self):
    payload = {'op': self.IDENTIFY,'d': {'token': self.token,'properties': {'$os': sys.platform,'$browser': 'Discord iOS','$device': 'discord.py','$referrer': '','$referring_domain': ''},'compress': True,'large_threshold': 250,'v': 3}}
    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]
    state = self._connection
    if state._activity is not None or state._status is not None: 
        payload["d"]["presence"] = {"status": state._status, "game": state._activity, "since": 0, "afk": False}
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value
    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
discord.gateway.DiscordWebSocket.identify = mobile

if __name__ == '__main__':
    client.run(BOT_TOKEN if not client.beta else BOT_TOKEN_BETA)
