import discord
from typing import Union
from discord.ext import commands
from config import TOP_GG_TOKEN, BOT_MOD_ROLE, ryuk_GUILD_ID, SUPPORTER_ROLE, OWNERS

import aiohttp

from utils.classes import Profile


class NotVoted(commands.CheckFailure):
    pass


class NotBotMod(commands.CheckFailure):
    pass


class OptedOut(commands.CheckFailure):
    pass


class PrivateCommand(commands.CheckFailure):
    pass


class ComingSoon(commands.CheckFailure):
    pass


async def check_voter(user_id):
    async with aiohttp.ClientSession() as s:
        async with s.get(f'https://top.gg/api/bots/751100444188737617/check?userId={user_id}', headers={'Authorization': TOP_GG_TOKEN}) as r:
            pain = await r.json()
            if pain['voted'] == 1:
                return True
            else:
                return False


async def check_supporter(ctx):
    guild = ctx.bot.get_guild(ryuk_GUILD_ID)
    if guild not in ctx.author.mutual_guilds:
        return False
    member = guild.get_member(ctx.author.id)
    role = guild.get_role(SUPPORTER_ROLE)
    if not member:
        return False
    if role not in member.roles:
        return False
    return True


def voter_only():
    async def predicate(ctx):
        thing = await check_voter(ctx.author.id)
        if not thing:
            raise NotVoted('vote')
        return True
    return commands.check(predicate)


def bot_mods_only():
    async def predicate(ctx: commands.Context):
        guild = ctx.bot.get_guild(ryuk_GUILD_ID)
        if guild not in ctx.author.mutual_guilds:
            raise NotBotMod('h')
        member = guild.get_member(ctx.author.id)
        role = guild.get_role(923024353988333579)
        if not member:
            raise NotBotMod('h')
        if role in member.roles:
            return True
        else:
            raise NotBotMod('h')
    return commands.check(predicate)


def not_opted_out():
    async def predicate(ctx: commands.Context):
        user_profile: Profile = await ctx.bot.get_user_profile_(ctx.author.id)
        if not user_profile.snipe:
            raise OptedOut('h')
        else:
            return True
    return commands.check(predicate)


def mutual_guild(guild_id: int):

    async def predicate(ctx: commands.Context):
        person: Union[discord.Member, discord.User] = ctx.author
        if guild_id not in [guild.id for guild in person.mutual_guilds]:
            raise PrivateCommand('h')
        return True

    return commands.check(predicate)


def coming_soon():
    def predicate(ctx):
        if ctx.author.id in OWNERS:
            return True
        raise ComingSoon()
    return commands.check(predicate)
