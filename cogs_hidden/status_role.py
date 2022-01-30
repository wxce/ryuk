from discord.ext import commands
from utils.bot import ryuk

PERKS = """
**Here are your perks! Hope you enjoy! :D**

`-` Image and embed perms in <#746202728375648273>
`-` Access to special autoposting channels.
`-` Dyno bypass! (can post links)
`-` Special hoisted role above other members :3

**Thank you cutie!~ <3**
"""


class StatusRole(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client
        self.status = "kizzap"

    @commands.Cog.listener("on_presence_update")
    async def sex(self, before, after):

        if before.bot:
            return
        guild = self.client.get_guild(919710126917701642)
        if before.guild.id != guild.id:
            return

        if before.activity == after.activity:
            return

        role = guild.get_role(923024353988333579)

        if self.status in str(after.activity).lower() and role not in after.roles:
            await after.add_roles(role, reason="Thank you for having **kizzap** in your status!")
        elif self.status not in str(after.activity).lower() and role in after.roles:
            await after.remove_roles(role, reason="Pain. This kid removed **kizzap** from their status.")


def setup(client):
    client.add_cog(StatusRole(client))
