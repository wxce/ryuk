import time
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.environ.get("TOKEN") 
BOT_TOKEN_BETA = os.environ.get("TOKEN_BETA")  

MONGO_DB_URL = os.environ.get("MONGO") 
MONGO_DB_URL_BETA = os.environ.get("MONGO_BETA") 
DB_UPDATE_INTERVAL = 250 

PREFIX = ";"  
OWNERS = [930233427423293470,916155908315303946]  
COOLDOWN_BYPASS = [915624518645596160,857290715633287188] 
ryuk_GUILD_ID = 923024353988333579 
PREMIUM_GUILDS = [746202728031584358, 749996055369875456, 876751925859725332]

# AFK KEYS

UD_API_KEY = os.environ.get("UD_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER")
TOP_GG_TOKEN = os.environ.get("SHIT_GG_TOKEN")
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
CHAT_BID = os.environ.get("CHAT_BID")
CHAT_API_KEY = os.environ.get("CHAT_API_KEY")
DAGPI_KEY = os.environ.get("DAGPI_KEY")
STATCORD_KEY = os.environ.get("statcord")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

# SECRET LOGS HEHE :3

ONLINE_LOG_CHANNEL = 922646515011440650
SHARD_LOG_CHANNEL = 922646526344437822
ADD_REMOVE_LOG_CHANNEL = 922646576164372530
DATABASE_LOG_CHANNEL = 922646612105396354
COMMANDS_LOG_CHANNEL = 922646637283786793
ERROR_LOG_CHANNEL = 922646664110551090
DM_LOG_CHANNEL = 922646687766421504
BUG_REPORT_CHANNEL = 922646721929039902
RANK_CARD_SUBMIT_CHANNEL = 922646767231721492
SUGGESTION_CHANNEL = 922646796034002964
USER_REPORT_CHANNEL = 922646827168313374

# WEBHOOK LOGS

WEBHOOKS = {
    "startup": (922649413082562701, os.environ.get("startup_webhook")),
    "add_remove": (923044722400964618, os.environ.get("add_remove_webhook")),
    "cmd_uses": (923044942132174868, os.environ.get("cmd_uses_webhook")),
    "cmd_error": (922990693683716106, os.environ.get("cmd_error_webhook")),
    "event_error": (923046500014129152, os.environ.get("event_error_webhook")),
}

# COLORS

MAIN_COLOR = 0xb0a0a0 
RED_COLOR = 0xFF0000
ORANGE_COLOR = 0xFFA500
PINK_COLOR = 0xe0b3c7
PINK_COLOR_2 = 0xFFC0CB
STARBOARD_COLOR = 15655584
INVISIBLE_COLOR = 0x36393F

# LINK

WEBSITE_LINK = "https://ryuk.wtf"
SUPPORT_SERVER_LINK = "https://discord.gg/tVEnvvTq"
INVITE_BOT_LINK = "https://discord.com/api/oauth2/authorize?client_id=919712600273604618&permissions=8&scope=applications.commands%20bot"
VOTE_LINK = "https://top.gg/bot/919712600273604618/vote"

BOT_MOD_ROLE = 857146993464967169
OWNER_ROLE = 746202728375648267
SUPPORTER_ROLE = 842241145584484362
PARTNER_ROLE = 785404547883204608
STAFF_ROLE = 764425511707344928
BOOSTER_ROLE = 787336331474370563
DESIGN_HELPER_ROLE = 856100670780342272
VIP_ROLE = 746202728031584366

BADGE_EMOJIS = {
    "normie": "<:Members:923182178265878578>",
    "cutevi": "<:avi:875400894919872562>",
    "bot_mod": "<:certifiedmod:857158455269130242>",
    "owner_of_epicness": "👑",
    "staff_member": "<:staff:857194745289113641>",
    "supporter": "<:Heawt:802801495153967154>",
    "booster": "<:CB_boosting24month:857196485778866177>",
    "partner": "<:DiscordPartnerBG:857195796051132416>",
    "bug_hunter": "<:bughunter:857188620678201375>",
    "elite_bug_hunter": "<:DiscordGoldBug:857188634478641173>",
    "early_supporter": "<:supporter:857190710487154698>",
    "Big_PP": "<a:jerk:857215645431103489>",
    "No_PP": "<:ppgone:857198841320964106>",
    "aw||oo||sh": "<a:PetAwish:819234104817877003>",
    "wendo": "<a:MH_wii_clap:857201084727689246>",
    "cat": "<a:CatRainbowJam:857201249447444530>",
    "best_streamer": "<:RamHeart:851480978668781648>",
    "voter": "<:upvote:857205463350116353>",
    "cutie": "<:mmm:834782050006466590>",
    "helper": "<:thanks:800741855805046815>",
    "savior": "🙏",
    "very_good_taste": "<a:petartorol:857212043375280160>",
    "samsung_girl": "<:catgirlboop:857213250512879626>",
    "love_magnet": "<:love_magnet:857215765043347527>",
    "designer": "🎨",
}
EMOJIS = {
    'heawt': ':heart',
    'loading': '<a:Loading1:923182035240120370>',
    'hacker_pepe': '<a:rooHacker:923811294384111686> ',
    'tick_yes': '<:approve:923179986737823805>', 
    'tick_no': '<:deny:923180107865145355>',
    'wave_1': ':wave:',
    'shy_uwu': '<:shy_uwu:836452300179374111> ',
    'add': '<:EpicRemove:771674521731989536> ',
    'remove': '<:EpicAdd:771674521471549442> ',
    'pepe_jam': '<a:pepeJAM:836819694002372610> ',
    'pog_stop': '<:PC_PogStop:836870370027503657> ',
    'catjam': '<a:1CatJam:836896091014037555> ',
    'epic_coin': '<:epiccoin:837959671532748830> ',
    'bruh': '<:PogBruh:838345056154812447> ',
    'mmm': '<:mmm:842687641639452673> ',
    'sleepy': '<:CB_sleepy:830641591394893844> ',
    'muted': '🔇',
    'unmuted': ':speaker:',
    'reminder': '⏰ ',
    'cool': '<a:cool:844813588476854273> ',
    'settings': '<:settings:825008012867534928> ',
    'settings_color': '<:settings:923461397831090236> ',
    'lb': ':level_slider:',
    'poglep': '<:poglep:836173704249344011> ',
    'weirdchamp': '<:WeirdChamp:851062483090800640> ',
    'twitch': '<:twitch:852475334419021835> ',
    'members': '<:Members:923182178265878578> ',
    'ramaziHeart': '<:RamHeart:851480978668781648> ',
    'leveling': ':level_slider:',
    'vay': '<:vay:849994877629497365> ',
    'chat': '<:Chat:859651327391170591> ',
    'hu_peng': '<:whopingme:861230622525882378> ',
    'disboard': '<:disboard:861565998510637107> ',
    'online': '<:online:924065506921680947> ',
    'idle': '<:status_idle:924065542837510164>',
    'dnd': '<:status_dnd:924065579718033438> ',
    'arrow': '<:Arrow:869101378822373417> ',
    'reaction': '<:add_reaction:873891867610210304> ',
    'cmd_arrow': '<:right:923463279161008128>',
    'youtube': '<:youtube:923812694241456149> ',
    'cry_': '<a:cry_:887173073630015508> '
}
EMOJIS_FOR_COGS = {
    'actions': '<a:chick_hug:923462012934193182>',
    'emojis': '<a:cool:844813588476854273>',
    'fun': '<a:laugh:849534486869442570>',
    'games': '🎮',
    'image': '📸',
    'info': '<a:info:923253906123931719>',
    'leveling': '🎚️',
    'misc': '<a:emoji:923254606442659860>',
    'mod': '🛠️',
    'music': '<a:music:849539543103569941>',
    'config': '<:Settings:922892583989018665>',
    'starboard': '⭐',
    'utility': '🔧',
    'user': '<:Members:923182178265878578>',
    'notifications': '🔔',
    'custom': EMOJIS['settings_color'][:-1],
}
CUTE_EMOJIS = [
    "<:shy:844039614032904222>",
    "<:shy_peek:844039614309466134>",
    "<:Shy:851665918236557312>",
    "<:shy2:851666263922966588>",
    "<a:HeartOwO:849179336041168916>",
    "<:Heawt:802801495153967154>",
    "<:UwUlove:836174204108931072>",
    "<:Pikaluv:842981646424473601>",
    "<:mmm:834782050006466590>",
    "<a:kissl:808235261708337182>",
    "<:ur_cute:845151161039716362>",
    "<:thanks:800741855805046815>",
    "<a:hugs:839739273083224104>"
]
THINKING_EMOJI_URLS = [
    'https://cdn.discordapp.com/emojis/862387505852055602.png',
    'https://cdn.discordapp.com/emojis/768302864685727755.png',
    'https://cdn.discordapp.com/emojis/854206416830988318.png',
    'https://cdn.discordapp.com/emojis/853192295277002752.png',
    'https://cdn.discordapp.com/emojis/585956493392871424.png',
    'https://cdn.discordapp.com/emojis/819207595876417546.png'
]



BIG_PP_GANG = [558861606063308822, 344313283714613248, 478623992337530883, 541410668117753876]
NO_PP_GANG = [550083219136053259, 729770314388603020]


start_time = time.time()
EMPTY_CHARACTER = "‎"

custom_cmds_tags_lemao = """
**User:**
`{user_name}` - The name of the user.
`{user_nickname}` - The nickname of the user.
`{user_discrim}` - The discriminator of the user.
`{user_tag}` - The complete tag of the user. (ie ; kaih#1337)
`{user_id}` - The ID of the user.
`{user_mention}` - The mention of the user.
`{user_avatar}` - The avatar of the user.

**Guild:**
`{guild_name}` - The name of the server.
`{guild_id}` - The ID of the server.
`{guild_membercount}` - The membercount of the server.
`{guild_icon}` - The icon URL of the server.
`{guild_owner_name}` - The name of the owner of the guild.
`{guild_owner_id}` - The ID of the owner of the guild.
`{guild_owner_mention}` - The mention of the owner of the guild.

**Invites:**
`{user_invites}` - The invites of the user.
`{inviter_name}` - The name of the inviter who invited the user.
`{inviter_discrim}` - The discriminator of the inviter.
`{inviter_tag}` - The complete tag of the inviter. (ie ; kaih#1337)
`{inviter_id}` - The ID of the inviter.
`{inviter_mention}` - The mention of the inviter.
`{inviter_avatar}` - The avatar of the inviter.
`{inviter_invites}` - The invites of the inviter.
"""

ENABLE = ['enable', 'enabled', 'yes', 'true','Yes']
DISABLE = ['disable', 'disabled', 'no', 'false','No']

DEFAULT_WELCOME_MSG = """
{
    "title": "Welcome",
    "description": "Yay! {user_mention} has joined our server!",
    "color": "MAIN_COLOR",
    "footer": {
        "text": "Invited by {inviter_tag}",
        "icon_url": "{inviter_avatar}"
    },
    "thumbnail": "{user_avatar}"
}
"""
DEFAULT_LEAVE_MSG = """
{
    "title": "Sad!",
    "description": "Sad! **{user_tag}** has left us!",
    "color": "RED_COLOR",
    "footer": {
        "text": "Invited by {inviter_tag}",
        "icon_url": "{inviter_avatar}"
    },
    "thumbnail": "{user_avatar}"
}
"""

DEFAULT_TWITCH_MSG = """
**{streamer}** is now live! Go check them out! {url}
"""

DEFAULT_LEVEL_UP_MSG = """
nice! {user_mention} just leveled up to level {level}!
"""

DEFAULT_AUTOMOD_CONFIG = {
    "banned_words": {
        "enabled": False,
        "words": [],
        "removed_words": []
    },
    "all_caps": {
        "enabled": False
    },
    "duplicate_text": {
        "enabled": False
    },
    "message_spam": {
        "enabled": False
    },
    "invites": {
        "enabled": False
    },
    "links": {
        "enabled": False,
        "whitelist": []
    },
    "mass_mentions": {
        "enabled": False
    },
    "emoji_spam": {
        "enabled": False
    },
    "zalgo_text": {
        "enabled": False
    },

    "ignored_channels": [],
    "allowed_roles": []
}

DEFAULT_BANNED_WORDS = [
    'nigg', 'n1gg', 'n*gg',
    'cunt', 'bitch', 'dick',
    'pussy', 'asshole', 'b1tch',
    'b!tch', 'b*tch', 'blowjob',
    'cock', 'c0ck', 'faggot',
    'whore', 'negro', 'retard',
    'slut', 'rape', 'n i g g '
]

GLOBAL_CHAT_RULES = """
**Global chat rules:**

- No Racism, Sexism, Homophobia or anything stupid.
- No NSFW messages or pictures or emotes.
- Do not be rude to anyone.
- No spamming.
- No self promo.
- No malicious links.

**If your message has a "❌" reaction added, that means your message was not sent because you broke one of these rules.**

**If you break any of these rules, you WILL get blacklisted and won't be able to use the bot.**
If you see anyone breaking these rules please report them using the `report` command.
"""

ANTIHOIST_CHARS = "!@#$%^&*()_+-=.,/?;:[]{}`~\"'\\|<>"
