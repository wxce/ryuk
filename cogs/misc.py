

import discord
import time
import humanfriendly
from discord import Embed, Colour
from utils.embed import error_embed, success_embed
from discord.ext import commands
from config import EMOJIS, MAIN_COLOR, WEBSITE_LINK, SUPPORT_SERVER_LINK, start_time, SUGGESTION_CHANNEL, BUG_REPORT_CHANNEL
from utils.bot import ryuk
import bs4
import requests
from random import randint



class misc(commands.Cog, description="Commands mostly related to the bot!"):
    def __init__(self, client: ryuk):
        self.client = client
    @staticmethod
    def RGB(value):
        if value is not None:
            try:
                value = int(str(value).replace(",", ""))
                return value if 0 <= value <= 255 else randint(0, 255)
            except ValueError:
                return randint(0, 255)
        else:
            return randint(0, 255)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="hex",description="Generates a random colour.",
                      aliases=["color", "randomcolor", "randomcolour", "colors", "colours", "rgb"])
    async def hex(self, ctx, r=None, g=None, b=None):
        if r:
            colour = r[(1 if len(r) == 7 else 2 if r.casefold().startswith("0x") else 0):]
            if len(colour) == 6:
                try:
                    r, g, b = (int(colour[i:i + 2], 16) for i in (0, 2, 4))
                except ValueError:
                    r = self.RGB(r)
            else:
                r = self.RGB(r)
        else:
            r = self.RGB(r)
        g = self.RGB(g)
        b = self.RGB(b)
        colour = "%02x%02x%02x" % (r, g, b)
        e = Embed(colour=Colour(int(colour, 16)), title="#" + colour.casefold(),
                  description=f"Requested by: {ctx.author.mention}")
        e.add_field(name="RGB", value=f"`{r}, {g}, {b}`")
        e.set_image(url=f"https://www.colorhexa.com/{colour}.png")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="misc", help="Check bot's ping.")
    async def ping(self, ctx):
        time1 = time.perf_counter()
        msg = await ctx.message.reply(embed=discord.Embed(title=f"Pinging... {EMOJIS['loading']}", color=MAIN_COLOR))
        time2 = time.perf_counter()

        db_time1 = time.perf_counter()
        await self.client.prefixes.find_one({"_id": ctx.guild.id})
        db_time2 = time.perf_counter()

        shard_text = ""
        for shard, latency in self.client.latencies:
            shard_text += f"Shard {shard}" + ' ' * (3 - len(str(shard))) + f': {round(latency*1000)}ms\n'

        embed = success_embed(
            "🏓  Pong!",
            f"""
**Basic:**
```yaml
API      : {round(self.client.latency*1000)}ms
Bot      : {round((time2-time1)*1000)}ms
Database : {round((db_time2-db_time1)*1000)}ms
```
**Shards:**
```yaml
{shard_text}
```
            """
        ).set_thumbnail(url=self.client.user.display_avatar.url)
        await msg.edit(embed=embed)

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(category="misc", help="invite ryuk")
    async def invite(self, ctx):
        await ctx.message.reply(embed=discord.Embed(
            title="invite ryuk",
            description="Thank you so much!",
            color=MAIN_COLOR,
            url=f"https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=bot%20applications.commands"
        ))

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(category="misc", help="Vote ryuk for a chance to gain some perks")
    async def vote(self, ctx):
        await ctx.message.reply(embed=discord.Embed(
            title="vote ryuk",
            description=f"""
you can vote for me on these links:

- [top.gg](https://top.gg/bot/{self.client.user.id}/vote)
- [bots.discordlabs.org](https://bots.discordlabs.org/bot/{self.client.user.id}/vote)
- [discordbotlist.com](https://discordbotlist.com/bots/{self.client.user.id}/upvote)
            """,
            color=MAIN_COLOR,
        ).set_footer(text="I love you!"))

    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.command(category="misc", aliases=['discord'], help="join ryuk's support server")
    async def support(self, ctx):
        await ctx.message.reply(SUPPORT_SERVER_LINK)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="misc", help="check ryuk's uptime")
    async def uptime(self, ctx):
        await ctx.message.reply(embed=discord.Embed(
            title="Uptime",
            description=f"I have been up for **{humanfriendly.format_timespan(round(time.time()-start_time))}**",
            color=MAIN_COLOR
        ))

    @commands.cooldown(3, 120, commands.BucketType.user)
    @commands.command(category="misc", help="Submit a suggestion!")
    async def suggest(self, ctx, *, suggestion=None):
        prefix = ctx.clean_prefix

        if suggestion is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.message.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Incorrect Usage!",
                f"please use it like this: `{prefix}suggest <suggestion>`"
            ))

        user_profile = await self.client.get_user_profile_(ctx.author.id)
        stuff = {"suggestions_submitted": user_profile.suggestions_submitted + 1}
        await self.client.update_user_profile_(ctx.author.id, **stuff)

        files = []
        for file in ctx.message.attachments:
            files.append(await file.to_file())

        embed = success_embed("Suggestion!", suggestion
                ).set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url
                ).set_footer(text=f"User ID: {ctx.author.id} | Guild ID: {ctx.guild.id}")

        msg = await self.client.get_channel(SUGGESTION_CHANNEL).send(embed=embed, files=files)
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')
        await ctx.reply(embed=success_embed(
            f"{EMOJIS['tick_yes']} Suggestion submitted!",
            f"Thank you for submitting the suggestion!\nyou have suggested a total of `{user_profile.suggestions_submitted + 1}` suggestions!"
        ))

    @commands.cooldown(2, 7200, commands.BucketType.user)
    @commands.command(category="misc", aliases=['bug'], help="Report a buggie >~<")
    async def bugreport(self, ctx, *, bug=None):
        prefix = ctx.clean_prefix
        if bug is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.message.reply(embed=error_embed("Incorrect Usage", f"please use it like this: `{prefix}bug <bug>`"))
        user_profile = await self.client.get_user_profile_(ctx.author.id)
        stuff = {"bugs_reported": user_profile.bugs_reported + 1}
        await self.client.update_user_profile_(ctx.author.id, **stuff)
        embed = discord.Embed(
            title="Bug",
            description=f"""
```
{bug}
```
            """,
            color=MAIN_COLOR
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"User ID: {ctx.author.id} | Guild ID: {ctx.guild.id}")
        await self.client.get_channel(BUG_REPORT_CHANNEL).send(embed=embed)
        await ctx.reply(embed=success_embed(
            f"{EMOJIS['tick_yes']} Bug submitted!",
            f"Thank you for submitting the bug!\nyou have reported a total of `{user_profile.bugs_reported + 1}` bugs"
        ))

    @commands.command(name='wyr', aliases=['wouldyourather', 'would-you-rather'])
    async def _wyr(self, ctx):
      r = requests.get('https://www.conversationstarters.com/wyrqlist.php').text
      soup = bs4(r, 'html.parser')
      qa = soup.find(id='qa').text
      qor = soup.find(id='qor').text
      qb = soup.find(id='qb').text
      paradox = discord.Embed(description=f'{qa}\n{qor}\n{qb}', color = 16202876)
      await ctx.send(embed=paradox)

def setup(client):
    client.add_cog(misc(client))
