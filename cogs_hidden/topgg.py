import dbl

from discord.ext import commands
from config import TOP_GG_TOKEN, EMOJIS
from utils.bot import ryuk


class TopGG(commands.Cog):
    def __init__(self, client: ryuk):
        self.client = client
        self.token = TOP_GG_TOKEN
        self.vote_c_id = 923039310817689701
        self.dblpy = dbl.DBLClient(
            self.client,
            self.token,
            webhook_path='/sus',
            webhook_auth='amogus',
            webhook_port=8080
        )


    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        user = self.client.get_user(data['user'])
        channel = self.client.get_channel(self.vote_c_id)
        await channel.send(f"Thank you {user.mention} for voting! {EMOJIS['heawt']}")

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        test_user = self.client.get_user(data['user'])
        channel = self.clent.get_channel(self.vote_c_id)
        await channel.send(f"webhooks works lmfao {test_user.mention}")


def setup(client):
    client.add_cog(TopGG(client))
