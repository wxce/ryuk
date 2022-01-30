import motor.motor_asyncio as motor
import time
import os
import re
import discord
import aiohttp
import sys
import traceback

from config import (
    MONGO_DB_URL, MONGO_DB_URL_BETA, DEFAULT_AUTOMOD_CONFIG,
    DB_UPDATE_INTERVAL, OWNERS, RED_COLOR, EMOJIS
)
from discord.ext import commands, tasks
from pymongo import UpdateOne
from utils.classes import Profile
from utils.embed import success_embed
from utils.ui import TicketView, DropDownSelfRoleView, ButtonSelfRoleView
from utils.help import ryukHelp
import pyfade

class ryuk(commands.AutoShardedBot):
    def __init__(self, beta: bool = False):
        self.app_cmds: dict = {}
        self.beta = beta
        intents = discord.Intents.all()
        intents.members = True
        super().__init__(
            owner_ids=OWNERS,
            command_prefix=ryuk.get_custom_prefix,
            intents=intents,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions.none(),
            strip_after_prefix=True,
            help_command=ryukHelp(),
            cached_messages=10000,
            activity=discord.Activity(type=discord.ActivityType.playing, name="under maintenance"),
        )
        cluster = motor.AsyncIOMotorClient(MONGO_DB_URL if not beta else MONGO_DB_URL_BETA)
        self.session = aiohttp.ClientSession()
        

        self.cache_loaded = False
        self.cogs_loaded = False
        self.views_loaded = False
        self.rolemenus_loaded = False

        self.last_updated_serverconfig_db = 0
        self.last_updated_prefixes_db = 0
        self.last_updated_leveling_db = 0

        self.db = cluster['ryuk']

        self.prefixes = self.db['prefixes']
        self.blacklisted = self.db['blacklisted']
        self.serverconfig = self.db['serverconfig']
        self.warnings = self.db['warnings']
        self.before_invites = self.db['before_invites']
        self.invites = self.db['invites']
        self.reminders_db = self.db['reminders']
        self.alarms_db = self.db['alarms']
        self.leveling_db = self.db['leveling']
        self.user_profile_db = self.db['user_profile']
        self.starboard = self.db['starboard']
        self.bookmarks = self.db['bookmarks']
        self.self_roles = self.db['self_roles']
        self.afk = self.db['afk']

        self.prefixes_cache = []
        self.blacklisted_cache = []
        self.serverconfig_cache = []
        self.leveling_cache = []

        self.reminders = []
        self.alarms = []

        self.update_prefixes_db.start()
        self.update_serverconfig_db.start()
        self.update_leveling_db.start()

        if not self.cache_loaded:
            self.loop.run_until_complete(self.get_cache())
            self.loop.run_until_complete(self.get_blacklisted_users())
            self.cache_loaded = True

        if not self.cogs_loaded:
            self.load_extension('jishaku')
            print("loaded jishaku")
            self.loaded, self.not_loaded = self.loop.run_until_complete(self.load_extensions('./cogs'))
            self.loaded_hidden, self.not_loaded_hidden = self.loop.run_until_complete(self.load_extensions('./cogs_hidden'))
            if self.beta:
                self.loop.run_until_complete(self.load_extensions('./tests'))
            self.cogs_loaded = True

    async def close(self):
        await self.db.cleanup()
        await super().close()

    async def set_default_guild_config(self, guild_id):
        pain = {
            "_id": guild_id,
            "disabled_cmds": [],
            "disabled_channels": [],
            "custom_cmds": [],
            "welcome": {"channel_id": None, "message": None, "embed": False},
            "leave": {"channel_id": None, "message": None, "embed": False},
            "autorole": {"humans": [], "bots": [], "all": []},
            "nqn": False,
            "leveling": {"enabled": False, "channel_id": None, "message": None, " roles": {}},
            "autoposting": [],
            "youtube": {"channel_id": None, "youtube_id": None, "message": None},
            "twitch": {"channel_id": None, "username": None, "message": None, "currently_live": False},
            "starboard": {"enabled": False, "star_count": 3, "channel_id": None},
            "logging": None,
            "chatbot": None,
            "automod": DEFAULT_AUTOMOD_CONFIG,
            "ghost_ping": False,
            "bump_reminders": False,
            "antialts": False,
            "globalchat": False,
            "counting": None,
            "antihoisting": False,
            "tickets": {"message_id": None, "channel": None, "roles": []},
            "counters": {"members": None, "huamns": None, "bots": None, "channels": None, "categories": None, "roles": None, "emojis": None}
        }
        self.serverconfig_cache.append(pain)
        return await self.get_guild_config(guild_id)

    async def get_guild_config(self, guild_id):
        for e in self.serverconfig_cache:
            if e['_id'] == guild_id:
                if "disabled_channels" not in e:
                    e.update({"disabled_channels": []})
                if "logging" not in e:
                    e.update({"logging": None})
                if "chatbot" not in e:
                    e.update({"chatbot": None})
                if "automod" not in e:
                    e.update({"automod": DEFAULT_AUTOMOD_CONFIG})
                if "ghost_ping" not in e:
                    e.update({"ghost_ping": False})
                if "bump_reminders" not in e:
                    e.update({"bump_reminders": False})
                if "antialts" not in e:
                    e.update({"antialts": False})
                if "globalchat" not in e:
                    e.update({"globalchat": False})
                if "counting" not in e:
                    e.update({"counting": None})
                if "antihoisting" not in e:
                    e.update({"antihoisting": False})
                if "tickets" not in e:
                    e.update({"tickets": {"message_id": None, "channel": None, "roles": []}})
                if "counters" not in e:
                    e.update({"counters": {"members": None, "huamns": None, "bots": None, "channels": None, "categories": None, "roles": None, "emojis": None}})
                return e
        return await self.set_default_guild_config(guild_id)

    async def get_user_profile_(self, user_id: int) -> Profile:
        profile_dict = await self.user_profile_db.find_one({"_id": user_id})
        if not profile_dict:
            return Profile(user_id)
        return Profile(**profile_dict)

    async def update_user_profile_(self, user_id: int, **options):
        await self.user_profile_db.update_one({"_id": user_id}, {"$set": options}, upsert=True)

    async def update_guild_before_invites(self, guild_id):
        invites = await self.before_invites.find_one({"_id": guild_id})
        guild = self.get_guild(guild_id)
        invites_list = await guild.invites()
        invites_list_but_weird = {}
        for invite in invites_list:
            invites_list_but_weird.update({invite.code: invite.uses})
        if invites is None:
            return await self.before_invites.insert_one({"_id": guild_id, "invites": invites_list_but_weird})
        await self.before_invites.update_one(
            filter={"_id": guild_id},
            update={"$set": {
                "invites": invites_list_but_weird
            }}
        )

    async def get_guild_invites(self, guild_id):
        invites = await self.before_invites.find_one({"_id": guild_id})
        if invites is None:
            await self.update_guild_before_invites(guild_id)
            return 'pain'
        return invites['invites']

    async def update_invites(self, user_id, guild_id, type_, amount):  # type can be 'fake', 'left', 'real'
        user = await self.invites.find_one({"_id": user_id})
        default_user = {
            "_id": user_id,
            "guilds": {
                str(guild_id): {
                    'real': 0 if type_ != 'real' else amount,
                    'left': 0 if type_ != 'left' else amount,
                    'fake': 0 if type_ != 'fake' else amount
                }
            }
        }
        if user is None:
            return await self.invites.insert_one(default_user)
        guilds_dict = user['guilds']
        if str(guild_id) in guilds_dict:
            guilds_dict[str(guild_id)].update({type_: amount})
        else:
            guilds_dict.update({str(guild_id): {
                type_: amount
            }})
        await self.invites.update_one(
            filter={"_id": user_id},
            update={"$set": {
                'guilds': guilds_dict
            }}
        )

    async def fetch_invites(self, user_id, guild_id, type_='real'):
        user = await self.invites.find_one({"_id": user_id})
        if user is None:
            return 0 if type_ != 'all' else [0, 0, 0]
        if str(guild_id) not in user['guilds']:
            return 0 if type_ != 'all' else [0, 0, 0]
        pain = user['guilds'][str(guild_id)]
        if type_ == 'all':
            return [0 if 'real' not in pain else pain['real'], 0 if 'fake' not in pain else pain['fake'], 0 if 'left' not in pain else pain['left']]
        if type_ == 'total':
            return (0 if 'real' not in pain else pain['real']) + (0 if 'fake' not in pain else pain['fake']) + (0 if 'left' not in pain else pain['left'])
        if type_ not in pain:
            return 0 if type_ != 'all' else [0, 0, 0]
        return pain[type_]

    async def get_inviter(self, user_id, guild_id):  # put the id of the user who got invited
        user = await self.invites.find_one({"_id": user_id})
        if user is None:
            return 'Unknown'
        if "inviters" not in user:
            return 'Unknown'
        if not user['inviters']:
            return 'Unknown'
        if str(guild_id) not in user['inviters']:
            return 'Unknown'
        return user["inviters"][str(guild_id)]

    async def update_inviter(self, user_id, inviter_id, guild_id):
        user = await self.invites.find_one({"_id": user_id})
        if user is None:
            return await self.invites.insert_one({
                "_id": user_id,
                "guilds": {},
                "inviters": {str(guild_id): inviter_id}
            })
        await self.invites.update_one(
            filter={"_id": user_id},
            update={"$set": {
                "inviters": {str(guild_id): inviter_id} if 'inviters' not in user or not user['inviters'] else user['inviters'].update({str(guild_id): inviter_id})
            }}
        )

    @tasks.loop(seconds=DB_UPDATE_INTERVAL, reconnect=True)
    async def update_serverconfig_db(self):
        if self.cache_loaded:
            cancer = []
            for eee in self.serverconfig_cache:
                hmm = UpdateOne(
                    {"_id": eee['_id']},
                    {"$set": {
                        "disabled_cmds": eee['disabled_cmds'],
                        "disabled_channels": eee.get('disabled_channels', []),
                        "disabled_categories": eee.get('disabled_categories', []),
                        "custom_cmds": eee.get("custom_cmds", []),
                        "welcome": eee['welcome'],
                        "leave": eee['leave'],
                        "autorole": eee['autorole'],
                        "nqn": eee['nqn'],
                        "leveling": eee['leveling'],
                        "autoposting": eee['autoposting'],
                        "youtube": eee['youtube'],
                        "twitch": eee['twitch'],
                        "starboard": eee['starboard'],
                        "logging": eee.get("logging", None),
                        "chatbot": eee.get("chatbot", None),
                        "automod": eee.get("automod", DEFAULT_AUTOMOD_CONFIG),
                        "ghost_ping": eee.get("ghost_ping", False),
                        "bump_reminders": eee.get("bump_reminders", False),
                        "antialts": eee.get("antialts", False),
                        "globalchat": eee.get("globalchat", False),
                        "counting": eee.get("counting", None),
                        "antihoisting": eee.get("antihoisting", False),
                        "tickets": {"message_id": None, "channel": None, "roles": []} if "tickets" not in eee else eee['tickets'],
                        "counters": {"members": None, "huamns": None, "bots": None, "channels": None, "categories": None, "roles": None, "emojis": None} if "counters" not in eee else eee['counters']
                    }},
                    upsert=True
                )
                cancer.append(hmm)
            if len(cancer) != 0:
                await self.serverconfig.bulk_write(cancer)
            self.last_updated_serverconfig_db = time.time()

    @tasks.loop(seconds=DB_UPDATE_INTERVAL, reconnect=True)
    async def update_prefixes_db(self):
        if self.cache_loaded:
            cancer = []
            for e in self.prefixes_cache:
                hmm = UpdateOne(
                    {"_id": e["_id"]},
                    {"$set": {"prefix": e['prefix']}},
                    upsert=True
                )
                cancer.append(hmm)
            if len(cancer) != 0:
                await self.prefixes.bulk_write(cancer)
            self.last_updated_prefixes_db = time.time()

    @tasks.loop(seconds=DB_UPDATE_INTERVAL, reconnect=True)
    async def update_leveling_db(self):
        if self.cache_loaded:
            cancer = []
            for e in self.leveling_cache:
                hmm = UpdateOne(
                    {"id": e["id"], "guild_id": e['guild_id']},
                    {"$set": {
                        "xp": e['xp'],
                        "messages": e['messages']
                    }},
                    upsert=True
                )
                cancer.append(hmm)
            if len(cancer) != 0:
                await self.leveling_db.bulk_write(cancer)
            self.last_updated_leveling_db = time.time()

    @update_serverconfig_db.before_loop
    async def before_update_serverconfig_db(self):
        await self.wait_until_ready()

    @update_prefixes_db.before_loop
    async def before_update_prefixes_db(self):
        await self.wait_until_ready()

    @update_leveling_db.before_loop
    async def before_update_leveling_db(self):
        await self.wait_until_ready()

    async def get_cache(self):
        cursor = self.prefixes.find({})
        self.prefixes_cache = await cursor.to_list(length=None)
        print(f"prefixes cache has been loaded. | {len(self.prefixes_cache)} items")

        cursor = self.serverconfig.find({})
        self.serverconfig_cache = await cursor.to_list(length=None)
        print(f"server config cache has been loaded. | {len(self.serverconfig_cache)} configs")

        cursor = self.reminders_db.find({})
        self.reminders = await cursor.to_list(length=None)
        print(f"reminders cache has been loaded. | {len(self.reminders)} reminders")

        cursor = self.leveling_db.find({})
        self.leveling_cache = await cursor.to_list(length=None)
        print(f"leveling cache has been loaded. | {len(self.leveling_cache)} items")

    async def get_blacklisted_users(self):
        cursor = self.blacklisted.find({})
        self.blacklisted_cache = await cursor.to_list(length=None)
        print(f"blacklisted users cache has been loaded. | {len(self.blacklisted_cache)} users")

    async def load_extensions(self, filename_):
        loaded = []
        not_loaded = {}
        i = 0
        total = 0
        for filename in os.listdir(filename_):
            if filename.endswith('.py'):
                total += 1
                h = f'{filename_[2:]}.{filename[:-3]}'
                try:
                    self.load_extension(h)
                    loaded.append(h)
                    i += 1
                except Exception as e:
                    not_loaded.update({h: e})
        print(f"loaded {i}/{total} extensions from {filename_}")
        return loaded, not_loaded

    async def fetch_prefix(self, message: discord.Message):
        if not message.guild:
            return [""]

        guild_id = message.guild.id
        prefix_cache = self.prefixes_cache

        for ee in prefix_cache:
            if ee['_id'] == guild_id:
                if isinstance(ee['prefix'], str):
                    str_prefix = ee['prefix']
                    ee.update({"prefix": [str_prefix]})
                return ee['prefix']

        prefix_cache.append({"_id": guild_id, "prefix": [";"]})
        return [";"]

    async def get_custom_prefix(self, message: discord.Message):
        prefix = await self.fetch_prefix(message)
        bot_id = self.user.id
        prefixes = [f"<@{bot_id}> ", f"<@!{bot_id}> "]
        for h in prefix:
            prefixes.append(h)

        comp = re.compile(
            "^(" + "|".join(re.escape(p) for p in prefixes) + ").*", flags=re.I
        )
        match = comp.match(message.content)
        if match is not None:
            return match.group(1)
        return prefix

    async def load_rolemenus(self, dropdown_view, button_view):
        i = 0
        cursor = self.self_roles.find({})
        h = await cursor.to_list(length=None)
        for amogus in h:
            guild = self.get_guild(amogus['_id'])
            if guild is not None:
                role_menus = amogus['role_menus']
                for msg_id, menu in role_menus.items():
                    if menu['type'] == 'dropdown':
                        self.add_view(dropdown_view(guild, menu['stuff']), message_id=int(msg_id))
                        i += 1
                    if menu['type'] == 'button':
                        self.add_view(button_view(guild, menu['stuff']), message_id=int(msg_id))
                        i += 1
        self.rolemenus_loaded = True

        print(f"self role views has been loaded. | {i} views")

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        (exc_type, exc, tb) = sys.exc_info()
        if isinstance(exc, commands.CommandInvokeError):
            return

        e = discord.Embed(title="Error in an event", color=RED_COLOR)
        e.add_field(name="Event", value=event_method)
        e.description = f"```py\n{''.join(traceback.format_exception(exc_type, exc, tb))}\n```"

        args_str = ['```py']
        for index, arg in enumerate(args):
            args_str.append(f'[{index}]: {arg!r}')
        args_str.append('```')
        e.add_field(name='Args', value='\n'.join(args_str), inline=False)
        webhooks = self.get_cog("Webhooks").webhooks
        webhook = webhooks.get("event_error")
        try:
            await webhook.send(embed=e)
        except Exception:
            return await super().on_error(event_method, *args, **kwargs)

    async def on_message(self, message: discord.Message):
        if not self.cache_loaded:
            return
        if message.author.bot:
            return
        for e in self.blacklisted_cache:
            if message.author.id == e['_id']:
                return
        if message.content.lower() in [f'<@{self.user.id}>', f'<@!{self.user.id}>']:
            prefixes = await self.fetch_prefix(message)
            prefix_text = ""
            for prefix in prefixes:
                prefix_text += f"`{prefix}`, "
            prefix_text = prefix_text[:-2]
            return await message.reply(embed=success_embed(
                f"{EMOJIS['wave_1']} hello!",
                f"my prefix{'es' if len(prefixes) > 1 else ''} for this server {'are' if len(prefixes) > 1 else 'is'}: {prefix_text}"
            ))

        await self.process_commands(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content or before.author.bot or not self.cache_loaded or not self.cogs_loaded:
            return
        self.dispatch("message", after)

    async def on_ready(self):
        if not self.views_loaded:
            self.add_view(TicketView())
            self.views_loaded = True
            print("ticket view has been loaded.")

        if not self.rolemenus_loaded:
            await self.load_rolemenus(DropDownSelfRoleView, ButtonSelfRoleView)

        print(pyfade.Fade.DiagonalBackwards(pyfade.Colors.purple_to_blue,"""



   ▄████████ ▄██   ▄   ███    █▄     ▄█   ▄█▄ 
  ███    ███ ███   ██▄ ███    ███   ███ ▄███▀ 
  ███    ███ ███▄▄▄███ ███    ███   ███▐██▀   
 ▄███▄▄▄▄██▀ ▀▀▀▀▀▀███ ███    ███  ▄█████▀    
▀▀███▀▀▀▀▀   ▄██   ███ ███    ███ ▀▀█████▄    
▀███████████ ███   ███ ███    ███   ███▐██▄   
  ███    ███ ███   ███ ███    ███   ███ ▀███▄ 
  ███    ███  ▀█████▀  ████████▀    ███   ▀█▀ 
  ███    ███                        ▀         


        """))
        print(f"\033[35mLogged in as {self.user}")
        print(f"\033[35mConnected to: {len(self.guilds)} guilds")
        print(f"\033[35mConnected to: {len(self.users)} users")
        print(f"\033[35mConnected to: {len(self.cogs)} cogs")
        print(f"\033[35mConnected to: {len(self.commands)} commands")
        print(f"\033[35mConnected to: {len(self.emojis)} emojis")
        print(f"\033[35mConnected to: {len(self.voice_clients)} voice clients")
        print(f"\033[35mConnected to: {len(self.private_channels)} private_channels")
        print('\033[39m')
        embed = success_embed(
            "Bot is ready!",
            f"""
    **Loaded cogs:** {len(self.loaded)}/{len(self.loaded) + len(self.not_loaded)}
    **Loaded hidden cogs:** {len(self.loaded_hidden)}/{len(self.loaded_hidden) + len(self.not_loaded_hidden)}
            """
        )
        if self.not_loaded:
            embed.add_field(
                name="Not loaded cogs",
                value="\n".join([f"`{cog}` - {error}" for cog, error in self.not_loaded.items()]),
                inline=False
            )
        if self.not_loaded_hidden:
            embed.add_field(
                name="Not loaded hidden cogs",
                value="\n".join([f"`{cog}` - {error}" for cog, error in self.not_loaded_hidden.items()]),
                inline=False
            )
        if self.beta:
            embed.set_footer(text="Beta version.")
        webhook = self.get_cog("Webhooks").webhooks.get("startup")
        await webhook.send(embed=embed)
