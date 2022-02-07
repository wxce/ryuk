from discord.ext import commands
import discord
import toml


def get_color(color: str):
    if not color in ["ok_color", "error_color"]:
        return discord.Color.default()

    t = toml.load("configoptions.toml")
    return int(str(t["options"][color]).replace("#", "0x"), base=16)


class MeifwaContext(commands.Context):
    """Custom Context"""

    async def send_ok(self, content: str):
        await self.send(embed=discord.Embed(description=content, color=0x01010))

    async def send_error(self, content: str):
        await self.send(embed=discord.Embed(description=content, color=0x010101))