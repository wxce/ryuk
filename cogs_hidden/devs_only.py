import discord
import time

from discord.ext import commands
from utils.embed import success_embed, error_embed
from discord.utils import escape_markdown
from utils.custom_checks import bot_mods_only
from utils.bot import ryuk
from config import (
    EMOJIS, DB_UPDATE_INTERVAL, OWNERS, ryuk_GUILD_ID
)


class Devsonly(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client
        self.forced_nicks = {}

    @commands.is_owner()
    @commands.command(help="ajajajjaaj")
    async def forcenick(self, ctx: commands.Context, user: discord.Member, *, nick: str = None):
        if nick is None:
            if user.id in self.forced_nicks:
                self.forced_nicks.pop(user.id)
        else:
            self.forced_nicks[user.id] = nick
        await ctx.message.add_reaction('💋')

    @commands.Cog.listener('on_member_update')
    async def force_nick_update_lma(self, before: discord.Member, after: discord.Member):
        if before.guild.id != ryuk_GUILD_ID:
            return
        if before.id not in self.forced_nicks:
            return
        if before.nick == after.nick:
            return
        await after.edit(nick=self.forced_nicks[before.id], reason="haha forcenick go br")

    @commands.is_owner()
    @commands.command(name="new", description="Update the avatar & icon", hidden=True)
    async def new(self, ctx, new_avatar):
      avatar = new_avatar.replace(" -i", "")
      response = await ctx.bot.session.get(avatar)
      try: await ctx.bot.user.edit(avatar=await response.read())
      except Exception as error: 
        embed = discord.Embed(color=0x010101)
        embed.set_author(name=ctx.author, icon_url= ctx.author.avatar.url)
        embed.description = f"```\n{error}```"
        return await ctx.send(embed=embed)
      try:
        if "-i" in new_avatar:
          await ctx.guild.edit(icon=await response.read())
      except: pass
      await ctx.message.add_reaction("👍")     

    @commands.is_owner()
    @commands.command(help="Change the bot's status")
    async def changestatus(self, ctx: commands.Context, *, status: str):
        await self.client.change_presence(
            activity=discord.Game(name=status),
            status=discord.Status.online
        )
        await ctx.message.add_reaction('👌')

    @commands.is_owner()
    @commands.command(help="Load jsk!")
    async def loadjsk(self, ctx):
        msg = await ctx.reply(f"{EMOJIS['loading']} Working on it...")
        self.client.load_extension('jishaku')
        await msg.edit(content="Done!")

    @commands.is_owner()
    @commands.command(aliases=['getcache'], help="Get cache!")
    async def get_cache(self, ctx: commands.Context):
        msg = await ctx.reply(f"{EMOJIS['loading']} Working on it...")
        await self.client.get_cache()
        await msg.edit(content="Done!")

    @commands.is_owner()
    @commands.command(aliases=['updatedb'], help="Update the database!")
    async def update_db(self, ctx: commands.Context, db=None):
        if db is None:
            return await ctx.reply("""
please select a database next time:

- prefixes
- serverconfig
            """)
        msg = await ctx.reply(f"{EMOJIS['loading']} Updating...")
        if db.lower() in ['prefixes', 'prefix']:
            await self.client.update_prefixes_db()
        if db.lower() in ['server', 'serverconfig']:
            await self.client.update_serverconfig_db()
        return await msg.edit(content="Updated!")

    @commands.is_owner()
    @commands.command(help="Check when the database was last updated.")
    async def lastdb(self, ctx: commands.Context):
        await ctx.reply(embed=success_embed(
            f"{EMOJIS['tick_yes']} Database info!",
            f"""
```yaml
Prefix DB: {round(time.time() - self.client.last_updated_prefixes_db)} seconds ago
Serverconfig DB: {round(time.time() - self.client.last_updated_serverconfig_db)} seconds ago
Leveling DB: {round(time.time() - self.client.last_updated_leveling_db)} seconds ago
```
            """
        ).set_footer(text=f"Database is updated every {DB_UPDATE_INTERVAL} seconds."))
    
    @commands.is_owner()
    @commands.command(help="Blacklist some kid.")
    @commands.cooldown(3, 120, commands.BucketType.user)
    async def blacklist(self, ctx: commands.Context, user: discord.User = None, *, reason='No Reason Provided'):
        prefix = ctx.clean_prefix
        if user is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid Usage!",
                f"Mention who you wanna blacklist next time.\nExample: `{prefix}blacklist @egirl spamming`"
            ))
        if user == ctx.author or user.id in OWNERS:
            return await ctx.reply("no")
        for e in self.client.blacklisted_cache:
            if e['_id'] == user.id:
                ctx.command.reset_cooldown(ctx)
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} Error!",
                    f"this user is already blacklisted.\n```yaml\nReason: {e['reason']}\n```"
                ))
        await self.client.blacklisted.insert_one({
            "_id": user.id,
            "reason": reason
        })
        await self.client.get_blacklisted_users()
        return await ctx.reply(embed=success_embed(
            f"{EMOJIS['tick_yes']} user blacklisted!",
            f"i blacklisted **{escape_markdown(str(user))}**."
        ))

    @commands.is_owner()
    @commands.command(help="Unblacklist some kid.")
    @commands.cooldown(3, 120, commands.BucketType.user)
    async def unblacklist(self, ctx: commands.Context, user: discord.User = None):
        prefix = ctx.clean_prefix
        if user is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid Usage!",
                f"mention who you wanna unblacklist next time.\nExample: `{prefix}unblacklist @son`"
            ))
        for e in self.client.blacklisted_cache:
            if e['_id'] == user.id:
                await self.client.blacklisted.delete_one({
                    "_id": user.id
                })
                await self.client.get_blacklisted_users()
                return await ctx.message.reply(embed=success_embed(
                    f"{EMOJIS['tick_yes']} Kid Unblacklisted!",
                    f"Done! I have unblacklisted **{escape_markdown(str(user))}**.\n```yaml\nReason: {e['reason']}\n```"
                ))
        ctx.command.reset_cooldown(ctx)
        return await ctx.message.reply(embed=error_embed(
            f"{EMOJIS['tick_yes']} Kid Not Found!",
            f"looks like **{escape_markdown(str(user))}** is not blacklisted, please try again."
        ))

    @commands.is_owner()
    @commands.command(help="DM some kid.")
    async def dm(self, ctx: commands.Context, user_id: int = None, *, msg=None):
        prefix = ctx.clean_prefix
        if user_id is None:
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid Usage!",
                f"Mention who you wanna unblacklist next time.\nExample: `{prefix}dm 915624518645596160 hello`"
            ))
        if msg is None:
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid Usage!",
                f"please enter a message next time.\nExample: `{prefix}dm 915624518645596160 hello`"
            ))
        user = self.client.get_user(user_id)
        if user is None:
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid User!",
                "looks like that user doesn't exist, please try again."
            ))
        await user.send(msg)
        await ctx.reply(f"{EMOJIS['tick_yes']} DMed **{escape_markdown(str(user))} ({user_id})**")


def setup(client):
    client.add_cog(Devsonly(client))
