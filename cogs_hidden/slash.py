

# import discord
from discord.ext import commands
from utils.bot import ryuk
# from utils.embed import success_embed
# from random import randint


class LolSlashCmdGoBrr(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client

    # @commands.Cog.listener("on_interaction")
    # async def haha_slash_go_brr(self, interaction: discord.Interaction):
    #     if interaction.type == discord.InteractionType.application_command:
    #         await interaction.response.send_message(
    #             embed=success_embed(
    #                 title="<:amogus:871732356233429014>  Sussometer",
    #                 description=f"you are **{randint(0, 100)}%** sus!"
    #             )
    #         )


def setup(client: ryuk):
    client.add_cog(LolSlashCmdGoBrr(client))
