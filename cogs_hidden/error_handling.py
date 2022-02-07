import discord
import traceback
import json

from discord.ext import commands
from humanfriendly import format_timespan
from config import (
    OWNERS, EMOJIS, MAIN_COLOR, SUPPORT_SERVER_LINK,
    VOTE_LINK, RED_COLOR
)
from utils.random import gen_random_string
from utils.custom_checks import NotVoted, NotBotMod, OptedOut, PrivateCommand, ComingSoon
from utils.converters import ImportantCategory, InvalidTimeZone, InvalidCategory
from utils.exceptions import AutomodModuleAlreadyEnabled, AutomodModuleNotEnabled, MusicGone, InvalidUrl
from utils.bot import ryuk
from utils.embed import (
    replace_things_in_string_fancy_lemao,
    process_embeds_from_json,
    error_embed, success_embed
)


class ErrorHandling(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client
        self.cd_mapping = commands.CooldownMapping.from_cooldown(5, 20, commands.BucketType.user)
        self.nice_spam_idiot = commands.CooldownMapping.from_cooldown(2, 10, commands.BucketType.user)

    async def process_custom_cmds(self, ctx: commands.Context, cmd_name):
        interseting_allowed_mentions = discord.AllowedMentions(
            everyone=False,
            roles=False,
            replied_user=False,
            users=True
        )
        guild_config = await self.client.get_guild_config(ctx.guild.id)
        if "custom_cmds" not in guild_config:
            guild_config.update({"custom_cmds": []})
        custom_cmds_list = guild_config["custom_cmds"]
        for e in custom_cmds_list:
            if e['name'] == cmd_name:
                if not e['embed']:
                    h = await replace_things_in_string_fancy_lemao(self.client, [ctx.author, ctx.guild], e['reply'])
                    await ctx.send(h, allowed_mentions=interseting_allowed_mentions)
                else:
                    embed_json = json.loads(e['reply'])
                    thing = await process_embeds_from_json(self.client, [ctx.author, ctx.guild], embed_json)
                    if thing[0] is not None:
                        await ctx.send(thing[0], embed=thing[1])  # use the function from utils.embed
                    else:
                        await ctx.send(embed=thing[1])
                return

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        bucket_pain = self.nice_spam_idiot.get_bucket(ctx.message)
        retry_after_pain = bucket_pain.update_rate_limit()
        prefix = ctx.clean_prefix
        if retry_after_pain:
            return
        if isinstance(error, commands.CommandNotFound):
            bucket = self.cd_mapping.get_bucket(ctx.message)
            retry_after = bucket.update_rate_limit()
            if retry_after and ctx.author.id not in OWNERS:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} slow down",
                    f"please try again after **{format_timespan(round(error.retry_after, 2))}**."),
                    delete_after=5
                )
            await self.process_custom_cmds(ctx, ctx.invoked_with)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} slow down",
                f"please try again after **{format_timespan(round(error.retry_after, 2))}**.".format(error.retry_after)),
                delete_after=5
            )
        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} slow down",
                f"An instance of this command is already running...\nyou can only run `{error.number}` instances at the same time."
            ))
        elif isinstance(error, commands.MissingPermissions):
            if ctx.author.id == 915624518645596160:
                return await ctx.reinvoke()
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} missing permissions",
                "you need **{}** perms to run this command.".format(' '.join(error.missing_permissions[0].split('_')).title())
            ))
        elif isinstance(error, commands.BotMissingPermissions):
            ctx.command.reset_cooldown(ctx)
            if error.missing_permissions[0] == 'send_messages':
                return
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Error!",
                "I am missing **{}** permissions.".format(' '.join(error.missing_permissions[0].split('_')).title())
            ))
        elif isinstance(error, commands.NSFWChannelRequired):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Go away horny!",
                "This command can only be used in a **NSFW** channel."
            ))
        elif isinstance(error, commands.NotOwner):
            await self.client.get_channel(922646664110551090).send(
                embed=discord.Embed(
                    title="Someone tried to use Owner only command!",
                    description=f"```{ctx.message.content}```",
                    color=MAIN_COLOR
                ).add_field(name="User", value=f"{ctx.author.mention}```{ctx.author} ({ctx.author.id})```", inline=False)
                .add_field(name="Server", value=f"```{ctx.guild} ({ctx.guild.id})```", inline=False)
            )
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} missing access",
                "you dont have access to use this command"
            ))
        elif isinstance(error, commands.MemberNotFound):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} not found",
                "I wasn't able to find **{}**, please try again.".format(error.argument)
            ))
        elif isinstance(error, commands.UserNotFound):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} not found",
                "I wasn't able to find **{}**, please try again.".format(error.argument)
            ))
        elif isinstance(error, commands.ChannelNotFound):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} not found",
                "No channel named **{}** was found, please try again.".format(error.argument)
            ))
        elif isinstance(error, commands.RoleNotFound):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} not found",
                "No role named **{}** was found, please try again.".format(error.argument)
            ))
        elif isinstance(error, commands.EmojiNotFound):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} not found",
                f"I wasn't able to find any emoji named: `{error.argument}`."
            ))
        elif isinstance(error, commands.PartialEmojiConversionFailure):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} not found",
                f"I wasn't able to find any emoji named: `{error.argument}`."
            ))
        elif isinstance(error, NotVoted):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['weirdchamp']} voter only",
                f"this command is restricted to voters only.\nClick **[here]({VOTE_LINK})** to vote!"
            ))
        elif isinstance(error, NotBotMod):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} No!",
                "only bot moderators can use this command"
            ))
        elif isinstance(error, OptedOut):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} No!",
                f"you cannot snipe, because you opted out!\nplease use `{prefix}optout` to be able to snipe again."
            ))
        elif isinstance(error, InvalidTimeZone):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid Timezone!",
                f"please use a valid timezone"
            ))
        elif isinstance(error, InvalidCategory):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid Category!",
                f"The category `{error.category}` is not a valid category!\nplease use `{prefix}help` to see the list of valid categories."
            ))
        elif isinstance(error, ImportantCategory):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Important Category!",
                f"you cannot disable the `{error.category}` category!\nIt has contains the core features of ryuk\nFor more info join our [support server]({SUPPORT_SERVER_LINK})."
            ))
        elif isinstance(error, PrivateCommand):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Private Command!",
                "This command is private and you cannot use it."
            ))
        elif isinstance(error, MusicGone):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['cry_']} Music unavailable! ",
                f"""
The music system is currently unavailable.
The devs are working hard on remaking it!
It will be back soon!

For more info you can join our [**support server**]({SUPPORT_SERVER_LINK})
                """
            ))
        elif isinstance(error, InvalidUrl):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid URL!",
                f"The URL `{error.argument}` is not a valid URL!"
            ))
        elif isinstance(error, AutomodModuleAlreadyEnabled):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Automod Module is already enabled!",
                f"The automod module `{error.module}` is already enabled!"
            ))
        elif isinstance(error, AutomodModuleNotEnabled):
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Automod Module is not enabled!",
                f"The automod module `{error.module}` is not enabled!\nplease enable it using `{prefix}automod enable {error.module}`."
            ))
        elif isinstance(error, commands.CheckFailure):
            ctx.command.reset_cooldown(ctx)
            if not self.client.beta:
                await ctx.message.add_reaction('❌')
        else:
            random_error_id = gen_random_string(10)
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} An unknown error occured!",
                error
            ).set_footer(text=f"ERROR ID: {random_error_id}"))
            error_text = "".join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))[:2000]
            error_embed_ = discord.Embed(
                title="Traceback",
                description=("```py\n" + error_text + "\n```"),
                color=RED_COLOR
            ).add_field(name="Command", value=f"```{ctx.message.content}```", inline=False
            ).add_field(name="User", value=f"{ctx.author.mention} ```{ctx.author} ({ctx.author.id})```", inline=False
            ).add_field(name="Server", value=f"```{ctx.guild}({ctx.guild.id})```", inline=False
            ).set_footer(text=f"ERROR ID: {random_error_id}")

            try:
                webhooks = self.client.get_cog("Webhooks").webhooks
                webhook = webhooks.get("cmd_error")
                await webhook.send(embed=error_embed_)
            except Exception:
                traceback.print_exception(etype=type(error), value=error, tb=error.__traceback__)


def setup(client):
    client.add_cog(ErrorHandling(client))
