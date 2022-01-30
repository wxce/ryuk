import discord
import time
import traceback

from utils.embed import success_embed
from discord.ext import commands, tasks
from config import ERROR_LOG_CHANNEL
from utils.bot import ryuk


class BumpReminder(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client
        self.auth_str = "bump done"
        self.disboard_id = 302050872383242240
        self.peng = discord.AllowedMentions(
            everyone=False,
            roles=True,
            users=True,
            replied_user=False
        )
        self.bumploop.start()

    @commands.Cog.listener("on_message")
    async def on_bump_message(self, message):
        if message.author.id != self.disboard_id or len(message.embeds) == 0 or not message.guild:
            return
        if self.auth_str not in str(message.embeds[0].description).lower():
            return
        g = await self.client.get_guild_config(message.guild.id)
        if not g['bump_reminders']:
            return
        next_bump_time = time.time() + 60 * 60 * 2

        bumper = None
        async for msg in message.channel.history(limit=3):
            if msg.content.lower().startswith("!d bump"):
                bumper = msg.author.id

        g['bump_reminders'].update({
            'channel_id': message.channel.id,
            'time': next_bump_time,
            'bumper': message.author.id if bumper is None else bumper
        })
        await message.add_reaction("⏱️")

        reward_id = g['bump_reminders'].get('reward')
        if reward_id is None:
            return
        role = message.guild.get_role(reward_id)
        if role is None:
            return
        if bumper is None:
            return
        lemao_bumper = message.guild.get_member(bumper)
        if lemao_bumper is None:
            return

        await lemao_bumper.add_roles(role)
        await message.channel.send(
            f"{lemao_bumper.mention} you have been rewarded the {role.mention} role for **2 hours**.",
            delete_after=5
        )

    @tasks.loop(seconds=30)
    async def bumploop(self):
        await self.client.wait_until_ready()
        try:
            time_now = time.time()
            for e in self.client.serverconfig_cache:
                if e['bump_reminders']:
                    e = e['bump_reminders']

                    if e['time'] is not None:
                        if round(e['time']) <= round(time_now):
                            try:
                                await self.client.get_channel(e['channel_id']).send(
                                    f"<@&{e['role']}>" if e['role'] is not None else f"<@{e['bumper']}>",
                                    embed=success_embed("It's Bump Time", "please bump using `!d bump`."),
                                    allowed_mentions=self.peng
                                )
                            except Exception:
                                pass
                            e.update({"time": None})
                            role_id = e.get("reward")
                            if role_id is not None:
                                channel = self.client.get_channel(e['channel_id'])
                                guild = channel.guild
                                role = guild.get_role(role_id)
                                member = guild.get_member(e.get('bumper'))
                                if role is not None and member is not None:
                                    await member.remove_roles(role)
        except Exception:
            cancer_error = traceback.format_exc()
            await self.client.get_channel(ERROR_LOG_CHANNEL).send(f"ERROR IN BUMP LOOP ```py\n{cancer_error}\n```")


def setup(client):
    client.add_cog(BumpReminder(client))
