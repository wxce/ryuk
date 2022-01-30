import discord
import datetime
import time
from discord.ext import commands
from config import ORANGE_COLOR
from utils.bot import ryuk
from utils.time import datetime_to_seconds


class AntiAlts(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client

    @commands.Cog.listener("on_member_join")
    async def actual_anti_alt_system_lmfao(self, member: discord.Member):
        if member.bot:
            return
        g = await self.client.get_guild_config(member.guild.id)
        aa = g['antialts']
        enabled = False if not aa else True
        if not enabled:
            return

        delv = ((datetime.datetime.utcnow() - member.created_at.replace(tzinfo=None)).total_seconds()) / (60 * 60 * 24)
        if delv >= aa['min_account_age']:
            return

        logchannel = self.client.get_channel(aa['log_channel'])
        restricted_role = member.guild.get_role(aa['restricted_role'])
        level = aa['level']

        if logchannel is None or restricted_role is None:
            return

        account_age = f"<t:{round(2 * time.time() - datetime_to_seconds(member.created_at))}:F>"

        embed = discord.Embed(
            title="Alt account detected.",
            description=f"{member.mention} {discord.utils.escape_markdown(str(member))}\n\n**Account Age:** {account_age}",
            color=ORANGE_COLOR,
            timestamp=datetime.datetime.utcnow()
        ).set_author(name=member, icon_url=member.display_avatar.url
        ).set_footer(text=f"ID: {member.id}")

        if level == 1:
            await member.add_roles(restricted_role, reason="ryuk alt protection system.")
            action_value = "RESTRICTED"
        elif level == 2:
            await member.kick(reason="ryuk alt protection system.")
            action_value = "KICKED"
        else:
            await member.ban(reason="ryuk alt protection system.")
            action_value = "BANNED"
        embed.add_field(name="Action:", value=action_value, inline=False)
        await logchannel.send(embed=embed)


def setup(client):
    client.add_cog(AntiAlts(client))
