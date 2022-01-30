import discord
from discord.ext import commands
from utils.bot import ryuk


class Events(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client

    @commands.Cog.listener("on_thread_join")
    async def ticket_roles_mention(self, thread: discord.Thread):
        if not thread.name.startswith("ticket-"):
            return
        try:
            int(thread.name[7:])
        except Exception:
            return
        g = await self.client.get_guild_config(thread.guild.id)
        if not g['tickets']['channel']:
            return
        if not g['tickets']['message_id']:
            return
        if thread.parent_id != g['tickets']['channel']:
            return
        if len(g['tickets']['roles']) == 0:
            return
        role_text = ""
        for role in g['tickets']['roles']:
            role_text += f"<@&{role}> "
        await thread.send(role_text, allowed_mentions=discord.AllowedMentions(
            roles=True,
            everyone=False,
            users=False,
            replied_user=False
        ))


def setup(client: ryuk):
    client.add_cog(Events(client))
