from discord.ext import commands
from utils.bot import ryuk
import statcord
import os


class StatcordPost(commands.Cog):
    def __init__(self, bot: ryuk):
        self.bot = bot
        if not bot.beta:
            self.key = os.environ.get("statcord")
            self.api = statcord.Client(self.bot, self.key)
            self.api.start_loop()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if not self.bot.beta:
            self.api.command_run(ctx)


def setup(bot: ryuk):
    if not bot.beta:
        bot.add_cog(StatcordPost(bot))
