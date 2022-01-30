import discord

from discord.ext import commands
from utils.embed import success_embed, error_embed
from utils.bot import ryuk
from config import (
    COOLDOWN_BYPASS, EMOJIS, OWNERS,
    PREFIX, MAIN_COLOR, EMPTY_CHARACTER, WEBSITE_LINK,
    SUPPORT_SERVER_LINK
)


class Logs(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client

    @commands.Cog.listener(name="on_command_completion")
    async def add_cmd_used_count_user_profile(self, ctx: commands.Context):
        p = await self.client.get_user_profile_(ctx.author.id)
        await self.client.update_user_profile_(ctx.author.id, cmds_used=p.cmds_used + 1)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if ctx.author.id in COOLDOWN_BYPASS:
            ctx.command.reset_cooldown(ctx)
        if ctx.author.id in OWNERS:
            return

        embed = success_embed(
            "Ah yes",
            "someone used me"
        ).add_field(name="Command:", value=f"```{ctx.message.content}```", inline=False
        ).add_field(name="User:", value=f"{ctx.author.mention}```{ctx.author}\n{ctx.author.id}```", inline=False
        ).add_field(name="Server:", value=f"```{ctx.guild}\n{ctx.guild.id}```", inline=False
        ).add_field(name="Channel:", value=f"{ctx.channel.mention}```{ctx.channel}\n{ctx.channel.id}```", inline=False)
        webhooks = self.client.get_cog("Webhooks").webhooks
        webhook = webhooks.get("cmd_uses")
        await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if str(message.channel.type) != 'private':
            return
        files = [await e.to_file() for e in message.attachments]
        embed = success_embed("New DM!", message.system_content).add_field(
            name="user:",
            value=f"{message.author.mention}```{message.author}\n{message.author.id}```",
            inline=False
        ).set_footer(text=f"Message ID: {message.id}").set_author(name=message.author, icon_url=message.author.display_avatar.url)
        for sticker in message.stickers:
            embed.add_field(
                name="Sticker:",
                value=f"[{sticker.name} (ID: {sticker.id})]({sticker.url})"
            )
        if len(message.stickers) == 1:
            embed.set_image(url=message.stickers[0].url)
        await self.client.get_channel(922646687766421504 if not self.client.beta else 913657200747114529).send(embed=embed, files=files)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.client.get_guild_config(guild.id)

        embed = success_embed(
            f"{EMOJIS['add']}  ryuk Added",
            f"""
**Server:** ```{guild} ({guild.id})```
**Owner:** {guild.owner.mention}```{guild.owner} ({guild.owner_id})```
**Members:** {guild.member_count}
**Humans:** {len(list(filter(lambda m: not m.bot, guild.members)))}
**Bots:** {len(list(filter(lambda m: m.bot, guild.members)))}
            """
        ).set_author(name=guild.owner, icon_url=guild.owner.display_avatar.url)
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        try:
            webhook = self.client.get_cog("Webhooks").webhooks.get("add_remove")
            await webhook.send(embed=embed)
        except Exception:
            pass

        send_embed = discord.Embed(
            title=f"hello",
            description=f"""
Thank you very much for inviting me.
My prefix is `{PREFIX}`, but you can change it to whatever you want!

                        """,
            color=MAIN_COLOR
        ).set_thumbnail(url=self.client.user.display_avatar.url
        ).set_author(name=self.client.user.name, icon_url=self.client.user.display_avatar.url
        ).add_field(name=EMPTY_CHARACTER, value=f"[invite ryuk]({WEBSITE_LINK}/invite) | [support server]({SUPPORT_SERVER_LINK})", inline=False)

        for channel in guild.channels:
            if "general" in channel.name:
                try:
                    return await channel.send(embed=send_embed)
                except Exception:
                    pass

        for channel in guild.channels:
            if "bot" in channel.name or "cmd" in channel.name or "command" in channel.name:
                try:
                    return await channel.send(embed=send_embed)
                except Exception:
                    pass

        for channel in guild.channels:
            try:
                return await channel.send(embed=send_embed)
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        embed = error_embed(
            f"ryuk removed",
            f"""
**Server:** ```{guild} ({guild.id})```
**Owner:** {guild.owner.mention}```{guild.owner} ({guild.owner_id})```
**Members:** {guild.member_count}
**Humans:** {len(list(filter(lambda m: not m.bot, guild.members)))}
**Bots:** {len(list(filter(lambda m: m.bot, guild.members)))}
            """
        ).set_author(name=guild.owner, icon_url=guild.owner.display_avatar.url)
        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)
        for e in self.client.serverconfig_cache:
            if e['_id'] == guild.id:
                self.client.serverconfig_cache.remove(e)
                await self.client.serverconfig.delete_one({"_id": guild.id})
                break
        webhook = self.client.get_cog("Webhooks").webhooks.get("add_remove")
        await webhook.send(embed=embed)


def setup(client):
    client.add_cog(Logs(client))
