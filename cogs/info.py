from handler.app_commands import InteractionContext
from utils.time import datetime_to_seconds
import discord
import time
import datetime
import aiohttp
import io
import pygit2
import itertools
from discord.utils import escape_markdown
from discord.ext import commands

from config import (
    EMOJIS_FOR_COGS, MAIN_COLOR, ORANGE_COLOR,
    EMOJIS, WEBSITE_LINK, SUPPORT_SERVER_LINK,
    INVITE_BOT_LINK, start_time
)
from utils.embed import error_embed
from utils.bot import ryuk
from utils.ui import BasicView
from handler import user_command
from typing import List, Optional, Union


USER_FLAGS = {
    'staff': '<:staff:895391901778346045> Discord Staff',
    'partner': '<:partnernew:895391927271309412> Partnered Server Owner',
    'hypesquad': '<:hypesquad:895391957638070282> HypeSquad Events',
    'bug_hunter': '<:bughunter:895392105386631249> Discord Bug Hunter',
    'hypesquad_bravery': '<:bravery:895392137225584651> HypeSquad Bravery',
    'hypesquad_brilliance': '<:brilliance:895392183950131200> HypeSquad Brilliance',
    'hypesquad_balance': '<:balance:895392209564733492> HypeSquad Balance',
    'early_supporter': '<:supporter:895392239356903465> Early Supporter',
    'bug_hunter_level_2': '<:bughunter_gold:895392270369579078> Discord Bug Hunter',
    'verified_bot_developer': '<:earlybotdev:895392298895032364> Early Verified Bot Developer',
    'verified_bot': '<:verified_bot:897876151219912754> Verified Bot',
    'discord_certified_moderator': '<:certified_moderator:895393984308981930> Certified Moderator',
    'premium_since': '<:booster4:895413288219861032>'
}


COMMON_DISCRIMINATORS = ['0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009',
                         '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999',
                         '1010', '2020', '3030', '4040', '5050', '6060', '7070', '8080', '9090',
                         '1001', '2002', '3003', '5004', '5005', '6006', '7007', '8008', '9009',
                         '1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000',
                         '1337', '6969', '0420', '2021', '0666', '0333','1738']

def get_user_badges(user: discord.Member, fetched_user: discord.User = None):
    flags = dict(user.public_flags)

    user_flags = []
    for flag, text in USER_FLAGS.items():
        try:
            if flags[flag]:
                user_flags.append(text)
        except KeyError:
            continue

    if user.display_avatar.is_animated():
        user_flags.append(f'<:Nitro:923234115095003187>')

    elif fetched_user and fetched_user.banner:
        user_flags.append(f'<:Nitro:923234115095003187>')

    elif user.premium_since:
        user_flags.append(f'<:Nitro:923234115095003187>')

    elif user.discriminator in COMMON_DISCRIMINATORS:
        print('this triggered')
        user_flags.append(f'<:Nitro:923234115095003187>')

    elif user.discriminator in COMMON_DISCRIMINATORS:
        print('this triggered')
        user_flags.append(f'<:Nitro:923234115095003187>')

    else:
        pass

    return '\n'.join(user_flags) if user_flags else None


def deltaconv(s):
    hours = s // 3600
    s = s - (hours * 3600)
    minutes = s // 60
    seconds = s - (minutes * 60)
    if hours > 0:
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
    return '{:02}:{:02}'.format(int(minutes), int(seconds))

def format_commit(commit: pygit2.Commit) -> str:
    short, _, _ = commit.message.partition('\n')
    short_sha2 = commit.hex[0:6]
    commit_tz = datetime.timezone(
        datetime.timedelta(minutes=commit.commit_time_offset))
    commit_time = datetime.datetime.fromtimestamp(
        commit.commit_time).astimezone(commit_tz)

    offset = f'<t:{int(commit_time.astimezone(datetime.timezone.utc).timestamp())}:R>'
    return f'[`{short_sha2}`](https://github.com/Nirlep5252/ryuk/commit/{commit.hex}) {short} ({offset})'


def get_commits(count: int = 3):
    repo = pygit2.Repository('.git')
    commits = list(itertools.islice(
        repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
    return '\n'.join(format_commit(commit) for commit in commits)


class UserinfoView(BasicView):

    def __init__(self, ctx: commands.Context, timeout: Optional[int] = None, embeds: List[discord.Embed] = None):
        super().__init__(ctx, timeout=timeout)
        self.embeds = embeds or []

    @discord.ui.button(label="Info", emoji=EMOJIS_FOR_COGS['info'], style=discord.ButtonStyle.blurple, disabled=True)
    async def info(self, b: discord.ui.Button, interaction: discord.Interaction):
        self.susu(b)
        await interaction.message.edit(embed=self.embeds[0], view=self)

    @discord.ui.button(label="Roles", emoji='<:role:890807676697710622>', style=discord.ButtonStyle.blurple)
    async def roles(self, b: discord.ui.Button, interaction: discord.Interaction):
        self.susu(b)
        await interaction.message.edit(embed=self.embeds[1], view=self)

    @discord.ui.button(label="Permissions", emoji='🛠️', style=discord.ButtonStyle.blurple)
    async def permissions(self, b: discord.ui.Button, interaction: discord.Interaction):
        self.susu(b)
        await interaction.message.edit(embed=self.embeds[2], view=self)

    def susu(self, b):
        for i in self.children:
            i.disabled = False
        b.disabled = True


class info(commands.Cog, description="Statistic related commands"):
    def __init__(self, client: ryuk):
        self.client = client

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(help="Get COVID-19 stats about any country.")
    async def covid(self, ctx, *, country=None):
        PREFIX = ctx.clean_prefix
        if country is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.message.reply(embed=error_embed("Invalid Usage!", f"please use it like this: `{PREFIX}covid <country>`"))

        try:
            async with self.client.session.get(f"https://coronavirus-19-api.herokuapp.com/countries/{country.lower()}") as r:
                response = await r.json()
        except Exception:
            ctx.command.reset_cooldown(ctx)
            return await ctx.message.reply(embed=error_embed("Error!", f"Couldn't find COVID-19 stats about `{country}`."))

        country = response['country']
        total_cases = response['cases']
        today_cases = response['todayCases']
        total_deaths = response['deaths']
        today_deaths = response['todayDeaths']
        recovered = response['recovered']
        active_cases = response['active']
        critical_cases = response['critical']
        total_tests = response['totalTests']
        cases_per_one_million = response['casesPerOneMillion']
        deaths_per_one_million = response['deathsPerOneMillion']
        tests_per_one_million = response['testsPerOneMillion']

        embed = discord.Embed(
            title=f"COVID-19 Status of {country}",
            description="This information isn't always live, so it may not be accurate.",
            color=ORANGE_COLOR
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/564520348821749766/701422183217365052/2Q.png")

        embed.add_field(
            name="Total",
            value=f"""
```yaml
Total Cases: {total_cases}
Total Deaths: {total_deaths}
Total Tests: {total_tests}
```
            """,
            inline=False
        )
        embed.add_field(
            name="Today",
            value=f"""
```yaml
Today Cases: {today_cases}
Today Deaths: {today_deaths}
```
            """,
            inline=False
        )
        embed.add_field(
            name="Other",
            value=f"""
```yaml
Recovered: {recovered}
Active Cases: {active_cases}
Critical Cases: {critical_cases}
```
            """,
            inline=False
        )
        embed.add_field(
            name="Per One Million",
            value=f"""
```yaml
Cases Per One Million: {cases_per_one_million}
Deaths Per One Million: {deaths_per_one_million}
Tests Per One Million: {tests_per_one_million}
```
            """,
            inline=False
        )

        await ctx.message.reply(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(help="Get info about a role.")
    async def roleinfo(self, ctx: commands.Context, role: discord.Role = None):
        prefix = ctx.clean_prefix
        if role is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Invalid Usage!",
                f"please mention a role to get info about.\nCorrect Usage: `{prefix}roleinfo @role`"
            ))
        embed = discord.Embed(
            title=f"{EMOJIS['tick_yes']} Role Information",
            color=role.color
        )
        embed.add_field(
            name="Basic Info:",
            value=f"""
```yaml
Name: {role.name}
ID: {role.id}
Position: {role.position}
Color: {str(role.color)[1:]}
Hoisted: {role.hoist}
Members: {len(role.members)}
```
            """,
            inline=False
        )
        something = ""
        for permission in role.permissions:
            a, b = permission
            a = ' '.join(a.split('_')).title()
            hmm = '+' if b else '-'
            something += hmm + ' ' + a + '\n'
        embed.add_field(
            name="Permissions:",
            value=f"```diff\n{something}\n```",
            inline=False
        )
        await ctx.reply(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(help="Get info about users!",aliases=['whois','ui'])
    @user_command(name="Userinfo")
    async def userinfo(self, ctx: Union[commands.Context, InteractionContext], user: Optional[Union[discord.Member, discord.User]] = None):
        if isinstance(ctx, commands.Context):
            user = user or ctx.author
        else:
            user = user or ctx.target

        _user = await self.client.fetch_user(user.id)  

        embed = discord.Embed(
            color=_user.accent_color or user.color or MAIN_COLOR,
            description=f"{user.mention} {escape_markdown(str(user))} ({user.id})",
            timestamp=datetime.datetime.utcnow()
        ).set_author(name=user, icon_url=user.display_avatar.url
        ).set_footer(text=self.client.user.name, icon_url=self.client.user.display_avatar.url
        ).set_thumbnail(url=user.display_avatar.url
        )
        if _user.banner is not None:
            embed.set_image(url=_user.banner.url)

        embed1 = embed.copy()
        c = str(int(user.created_at.astimezone(datetime.timezone.utc).timestamp()))
        j = str(int(user.joined_at.astimezone(datetime.timezone.utc).timestamp())) if isinstance(user, discord.Member) else None
        embed1.add_field(
            name="Account Info:",
            value=f"""
**Username:** {escape_markdown(user.name)}
**Nickname:** {escape_markdown(user.display_name)}
**ID:** {user.id}
            """,
            inline=False
        )
        if user.premium_since:
            embed1.add_field(name=f"Boosting since:",
                            value=f"╰ {discord.utils.format_dt(user.premium_since, style='f')} "
                                  f"({discord.utils.format_dt(user.premium_since, style='R')})",
                            inline=False)
        embed1.add_field(
            name="Age Info:",
            value=f"""
**Created At:** <t:{c}:F> <t:{c}:R>
**Joined At:** {'<t:' + j + ':F> <t:' + j + ':R>' if j is not None else 'Not in the server.'}
            """,
            inline=False
        )
        spotify = discord.utils.find(lambda act: isinstance(act, discord.Spotify), user.activities)

        embed1.add_field(name=f"Spotify:",
                        value=(f"**[{spotify.title}]({spotify.track_url})**"
                               f"\nBy __{spotify.artist}__"
                               f"\nOn __{spotify.album}__"
                               f"\n**Time:** {deltaconv((ctx.message.created_at - spotify.start).total_seconds())}/"
                               f"{deltaconv(spotify.duration.total_seconds())}"
                               if spotify else 'Not listening to anything...'))
        embed1.add_field(
            name="URLs:",
            value=f"""
**Avatar URL:** [Click Me]({user.display_avatar.url})
**Guild Avatar URL:** [Click Me]({(user.guild_avatar.url if user.guild_avatar is not None else user.display_avatar.url) if isinstance(user, discord.Member) else user.display_avatar.url})
**Banner URL:** {'[Click Me](' + _user.banner.url + ')' if _user.banner is not None else 'None'}
            """,
            inline=False
        )
        member = user or ctx.author

        embed1.add_field(name=f"Badges",
                        value=get_user_badges(user=member,fetched_user=user) or "No Badges", inline=True)
        embed2 = embed.copy()
        r = (', '.join(role.mention for role in user.roles[1:][::-1]) if len(user.roles) > 1 else 'No Roles.') if isinstance(user, discord.Member) else 'Not in server.'
        embed2.add_field(
            name="Roles:",
            value=r if len(r) <= 1024 else r[0:1006] + ' and more...',
            inline=False
        )

        embed3 = embed.copy()
        embed3.add_field(
            name="Permissions:",
            value=', '.join([perm.replace('_', ' ').title() for perm, value in iter(user.guild_permissions) if value]) if isinstance(user, discord.Member) else 'Not in server.',
            inline=False
        )
        embeds = [embed1, embed2, embed3]
        v = UserinfoView(ctx, None, embeds)
        await ctx.reply(embed=embed1, view=v)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(help="Get info about the server!",aliases=['si'])
    async def serverinfo(self, ctx: commands.Context):
        guild: discord.Guild = ctx.guild
        embed = discord.Embed(
            title=f"{EMOJIS_FOR_COGS['info']} Server Information",
            description=f"Description: {guild.description}",
            color=MAIN_COLOR
        ).set_author(
            name=guild.name,
            icon_url=guild.me.display_avatar.url if guild.icon is None else guild.icon.url
        ).set_footer(text=f"ID: {guild.id}")
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(
            name="Basic Info:",
            value=f"""
**Owner:** <@{guild.owner_id}>
**Created At:** <t:{round(time.time() - (datetime_to_seconds(guild.created_at) - time.time()))}:F>
**Region:** {str(guild.region).title()}
**System Channel:** {"None" if guild.system_channel is None else guild.system_channel.mention}
**Verification Level:** {str(guild.verification_level).title()}
            """,
            inline=False
        )
        last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
        if last_boost.premium_since is not None:
            boost = f"\n{last_boost}" \
                    f"\n╰ {discord.utils.format_dt(last_boost.premium_since, style='R')}"
        else:
            boost = "\n╰ No active boosters"

        embed.add_field(name=f" Boosts:",
                        value=f"Level: {guild.premium_tier}"
                              f"\n╰ Amount: {guild.premium_subscription_count}"
                              f"\n**Last booster:**{boost}",
                              inline=True)
        if guild.premium_subscribers:
            index = len(guild.premium_subscribers)
            sort_subs = sorted(guild.premium_subscribers, key=lambda m: m.premium_since or m.created_at, reverse=True)
            boosters = [f"{m} ({m.premium_since.strftime('%d %b %Y. %H:%M')})" for m in sort_subs[:5]]
            boosters.reverse()
            boost_order = '\n'.join([f"{n}.{' ' * (7 - len(str(n)) + 1)}{s}" for n, s in enumerate(boosters, start=index)])
            embed.add_field(name=f"💎 Recent Boosters:", inline=False,
                            value='```py\n' + boost_order + '\n```' +
                                  f'**Boosts** {guild.premium_subscription_count} • '
                                  f'**Boosters** {len(guild.premium_subscribers)}')
        embed.add_field(
            name="Members Info:",
            value=f"""
**Members:** `{len(guild.members)}`
**Humans:** `{len(list(filter(lambda m: not m.bot, guild.members)))}`
**Bots:** `{len(list(filter(lambda m: m.bot, guild.members)))}`
            """,
            inline=True
        )
        embed.add_field(
            name="Channels Info:",
            value=f"""
**Categories:** `{len(guild.categories)}`
**Text Channels:** `{len(guild.text_channels)}`
**Voice Channels:** `{len(guild.voice_channels)}`
**Threads:** `{len(guild.threads)}`
            """,
            inline=True
        )
        embed.add_field(
            name="Other Info:",
            value=f"""
**Roles:** `{len(guild.roles)}`
**Emojis:** `{len(guild.emojis)}`
**Stickers:** `{len(guild.stickers)}`
                """
        )
        if guild.features:
            embed.add_field(
                name="Features:",
                value=', '.join([feature.replace('_', ' ').title() for feature in guild.features]),
                inline=False
            )
        if guild.banner is not None:
            embed.set_image(url=guild.banner.url)

        return await ctx.reply(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(aliases=['av', 'pfp'], help="Get the user's avatar")
    async def avatar(self, ctx: commands.Context, user: Optional[Union[discord.Member, discord.User]] = None):
        user = user or ctx.author
        embed = discord.Embed(
            title=f"Avatar of {escape_markdown(str(user))}",
            color=user.color,
            description=f'Link as: [`png`]({user.display_avatar.replace(format="png").url}) | [`jpg`]({user.display_avatar.replace(format="jpg").url}) | [`webp`]({user.display_avatar.replace(format="webp").url})'
        ).set_image(url=user.display_avatar.url)
        await ctx.message.reply(embed=embed)

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(aliases=['stats','bi'], help="Get info about me!")
    async def botinfo(self, ctx: commands.Context):
        embed = discord.Embed(
            title="info about me!",
            description="a simple multipurpose discord bot.",
            color=MAIN_COLOR,
            timestamp=datetime.datetime.utcnow()
        ).add_field(
            name="Stats:",
            value=f"""
**Servers:** {len(self.client.guilds)}
**Users:** {len(self.client.users)}
**Commands:** {len(self.client.commands)}
**Uptime:** {str(datetime.timedelta(seconds=int(round(time.time()-start_time))))}
**Version:** V 1.0.0
            """,
            inline=True
        ).add_field(
            name="Links:",
            value=f"""
- [Support]({SUPPORT_SERVER_LINK})
- [Invite]({INVITE_BOT_LINK})    
      """,
            inline=True
        ).set_footer(text=self.client.user.name, icon_url=self.client.user.display_avatar.url
        ).set_author(name=self.client.user.name, icon_url=self.client.user.display_avatar.url
        ).set_thumbnail(url=self.client.user.display_avatar.url)
        try:
            embed.add_field(
                name="ryuk",
                value="created with love",
                inline=False
            )
        except Exception:
            pass
        await ctx.reply(embed=embed)

    @commands.command()
    async def spotify(self, ctx, member: discord.Member = None):
        """ Get the spotify link of a member """
        try:
            async with ctx.typing():
                member = member or ctx.author
                spotify: discord.Spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)
                if spotify is None:
                    return await ctx.send(f"**{member}** is not listening or connected to Spotify.")
                params = {
                    'title': spotify.title,
                    'cover_url': spotify.album_cover_url,
                    'duration_seconds': spotify.duration.seconds,
                    'start_timestamp': spotify.start.timestamp(),
                    'artists': spotify.artists
                }

                async with self.client.session.get('https://api.jeyy.xyz/discord/spotify', params=params) as response:
                    buf = io.BytesIO(await response.read())
                artists = ', '.join(spotify.artists)
                file = discord.File(buf, 'spotify.png')
                embed = discord.Embed(description=f"**{spotify.title}** by **{artists}**")
                embed.set_author(name=f"{member}'s Spotify", icon_url=member.display_avatar.url)
                embed.set_image(url='attachment://spotify.png')
                view = discord.ui.View()
                view.add_item(discord.ui.Button(emoji="<:spotify:928699098205397032>", url=spotify.track_url, label='Listen to this track'))
            await ctx.send(embed=embed, file=file, view=view)
        except aiohttp.ClientConnectorCertificateError:
            await ctx.send("⚠ **|** SSL certificate thing stupid!! Use DuckBot at `db.spotify`")
            
def setup(client):
    client.add_cog(info(client))
