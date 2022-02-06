import util
import discord
from discord.ext import commands
class help_ong(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="help", description="shows information fr")
    async def help(self, ctx, *, command=None):
      if command != None:
        valid_command = self.bot.get_command(command)
        if valid_command == None: return await ctx.send("that isn't a valid command")
        command = valid_command
        embed = discord.Embed(color=ctx.author.color, title=command.usage or command.qualified_name)
        embed.description = command.description
        embed.add_field(name="aliases", value=", ".join(command.aliases) if len(command.aliases) != 0 else "None")
        return await ctx.send(embed=embed)
      main_embed = discord.Embed(color=ctx.author.color)
      main_embed.title = "this does something ig"
      main_embed.description = "use da buttons"
      modules = []
      for temp_cog in self.bot.cogs:
        if temp_cog.lower() in ("jishaku"): continue
        cog = ctx.bot.get_cog(temp_cog)
        commands = []
        for command in cog.walk_commands():
          commands.append(command.usage or command.qualified_name)
        if len(commands) != 0: modules.append({"module": temp_cog, "commands": commands})
      embeds = []
      embeds.append(main_embed)
      for item in modules:
        embed = discord.Embed(color=ctx.author.color, title=item["module"], description="```\n"+"\n".join(item["commands"])+"\n```")
        embed.set_footer(text=f"{len(item['commands'])} commands")
        embeds.append(embed)
      await util.page(ctx, embeds)
def setup(bot):
    bot.add_cog(help_ong(bot))