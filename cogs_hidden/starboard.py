import discord

from discord.ext import commands
from datetime import datetime
from config import EMPTY_CHARACTER, STARBOARD_COLOR
from utils.bot import ryuk


class Starboard(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client

    @commands.Cog.listener("on_raw_reaction_add")
    async def starboard(self, payload):
        if payload.emoji.name != '⭐':
            return

        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        guild_config = await self.client.get_guild_config(msg.guild.id)
        sb_config = guild_config['starboard']

        if msg.author.bot:
            return
        if not sb_config['enabled']:
            return

        if msg.author == payload.member:
            return await msg.remove_reaction(payload.emoji, payload.member)

        msg_star_count = 0

        for e in msg.reactions:
            if e.emoji == '⭐':
                msg_star_count += e.count
                if e.count < sb_config['star_count']:
                    return
                break

        embed = discord.Embed(
            description=msg.content or EMPTY_CHARACTER,
            color=STARBOARD_COLOR,
            timestamp=datetime.utcnow()
        ).set_author(name=msg.author, icon_url=msg.author.display_avatar.url, url=msg.jump_url
        ).set_footer(text=f"Message ID: {msg.id}"
        )

        if len(msg.attachments):
            embed.set_image(url=msg.attachments[0].url)

        atch_text = ""

        for file in msg.attachments:
            atch_text += f"**[{file.filename}]({file.url})**\n"
        if atch_text != "":
            embed.add_field(name="Attachments:", value=atch_text, inline=False)

        for sticker in msg.stickers:
            embed.add_field(
                name=f"Sticker: `{sticker.name}`",
                value=f"ID: [`{sticker.id}`]({sticker.url})"
            )
        if len(msg.stickers) == 1:
            embed.set_thumbnail(url=msg.stickers[0].url)

        embed.add_field(name="Original message:", value=f"[**Click to jump to message!**]({msg.jump_url})")

        starboard_msg = await self.client.starboard.find_one({"_id": msg.id})

        if starboard_msg is None:
            m = await self.client.get_channel(sb_config['channel_id']).send(
                content=f"{'⭐' if msg_star_count < 10 else '🌟'} **{msg_star_count}** | {msg.channel.mention}",
                embed=embed
            )
            await self.client.starboard.insert_one({
                "_id": msg.id,
                "m_id": m.id
            })
        else:
            msg_to_edit = await self.client.get_channel(sb_config['channel_id']).fetch_message(starboard_msg['m_id'])
            await msg_to_edit.edit(
                content=f"{'⭐' if msg_star_count < 10 else '🌟'} **{msg_star_count}** | {msg.channel.mention}",
                embed=embed
            )

    @commands.Cog.listener("on_raw_reaction_remove")
    async def edit_starboard_msg(self, payload):
        if payload.emoji.name != '⭐':
            return

        msg = await self.client.get_channel(payload.channel_id).fetch_message(payload.message_id)
        guild_config = await self.client.get_guild_config(msg.guild.id)
        sb_config = guild_config['starboard']

        if msg.author.bot:
            return
        if not sb_config['enabled']:
            return
        if msg.author == payload.member:
            return

        eee = await self.client.starboard.find_one({"_id": msg.id})
        if eee is None:
            return

        msg_star_count = 0

        for e in msg.reactions:
            if e.emoji == '⭐':
                msg_star_count += e.count
                break

        starboard_channel = self.client.get_channel(sb_config['channel_id'])
        if starboard_channel is None:
            return

        sb_msg = await starboard_channel.fetch_message(eee['m_id'])

        embed = discord.Embed(
            description=msg.content or EMPTY_CHARACTER,
            color=STARBOARD_COLOR,
            timestamp=datetime.utcnow()
        ).set_author(name=msg.author, icon_url=msg.author.display_avatar.url, url=msg.jump_url
        ).set_footer(text=f"Message ID: {msg.id}"
        )

        if len(msg.attachments):
            embed.set_image(url=msg.attachments[0].url)

        atch_text = ""

        for file in msg.attachments:
            atch_text += f"**[{file.filename}]({file.url})**\n"
        if atch_text != "":
            embed.add_field(name="Attachments:", value=atch_text, inline=False)

        for sticker in msg.stickers:
            embed.add_field(
                name=f"Sticker: `{sticker.name}`",
                value=f"ID: [`{sticker.id}`]({sticker.url})"
            )
        if len(msg.stickers) == 1:
            embed.set_thumbnail(url=msg.stickers[0].url)

        embed.add_field(name="Original message:", value=f"[**Click to jump to message!**]({msg.jump_url})")

        await sb_msg.edit(
            content=f"{'⭐' if msg_star_count < 10 else '🌟'} **{msg_star_count}** | {msg.channel.mention}",
            embed=embed
        )

    @commands.Cog.listener("on_message_delete")
    async def del_starboard_msg(self, message: discord.Message):
        guild_config = await self.client.get_guild_config(message.guild.id)
        sb_config = guild_config['starboard']
        if not sb_config['enabled']:
            return

        h = await self.client.starboard.find_one({"_id": message.id})

        if h is None:
            return

        sb_channel = self.client.get_channel(sb_config['channel_id'])
        if sb_channel is None:
            return

        sb_msg = await sb_channel.fetch_message(h['m_id'])

        await sb_msg.delete()


def setup(client):
    client.add_cog(Starboard(client))
