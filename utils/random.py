

import random

from discord.ext import commands

letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
characters = "!@#$%&amp;*"
numbers = "1234567890"
email_fun = [
    '69420', '8008135', 'eatsA$$', 'PeekABoo',
    'TheShire', 'isFAT', 'Dumb_man', 'Ruthless_gamer',
    'Sexygirl69', 'Loyalboy69', 'likesButts'
]
passwords = [
    'animeislife69420', 'big_awoogas', 'red_sus_ngl',
    'IamACompleteIdiot', 'youWontGuessThisOne',
    'yetanotherpassword', 'iamnottellingyoumypw',
    'SayHelloToMyLittleFriend', 'ImUnderyourBed',
    'TellMyWifeILoveHer', 'P@$$w0rd', 'iLike8008135', 'IKnewyouWouldHackIntoMyAccount',
    'BestPasswordEver', 'JustARandomPassword', 'VoteryukUwU'
]
DMs = [
    "send nudes please", "i invited ryuk and i got a cookie",
    "i hope my mum doesn't find my nudes folder",
    "please dont bully me", "https://youtu.be/oHg5SJYRHA0",
    "i like bananas", "i use discord in light mode",
    "if you are reading this u shud vote ryuk", "send feet pics when",
    "sUbScRiBe To mY youTuBe ChAnNeL", "the impostor is sus", "python makes me horny"
]
discord_servers = [
    "Sons of Virgins", "Small Benis Gang", "Gamers United",
    "Anime Server 69420", "Cornhub", "Femboy Gang"
]


def gen_random_string(l_: int):
    uwu = ""
    for i in range(l_ + 1):
        uwu += random.choice((letters + numbers))
    return uwu


async def send_random_tip(ctx: commands.Context, msg: str, chances: int):
    if random.randint(1, chances) == chances:
        return await ctx.send(f"**Pro Tip:** {msg}")
    else:
        pass
