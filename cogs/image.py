import discord
import functools

from discord.ext import commands
from config import (
    EMOJIS, PINK_COLOR_2, MAIN_COLOR
)
from utils.embed import error_embed
from utils.bot import ryuk
from utils.flags import EnhanceCmdFlags
from typing import Optional, Union
from epicbot_images import memes, effects, gif_effects
from handler import SlashCommandOption, InteractionContext, slash_command

wiggle_concurrency = []


class image(commands.Cog, description="Cool image commands!"):
    def __init__(self, client: ryuk):
        self.client = client

    async def get_img_from_api(self, embed_stuff, api_url, thingy):
        e = discord.Embed(
            title=embed_stuff[0],
            color=embed_stuff[1]
        )
        async with self.client.session.get(api_url) as r:
            j = await r.json()
            e.set_image(url=j[thingy])
        return e

    @commands.command(help="Blur your friends ugly face...")
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 45, commands.BucketType.user)
    async def blur(self, ctx: commands.Context, user: Optional[discord.Member] = None, intensity: Optional[int] = 5):
        user = user or ctx.author
        if intensity > 25 or intensity < -25:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}The blur intensity can't be greater than `25`")
        avatar_bytes = await user.display_avatar.replace(format='png', size=256).read()
        async with ctx.channel.typing():
            await ctx.reply(
                file=discord.File(await self.client.loop.run_in_executor(None, functools.partial(effects.blur, avatar_bytes, intensity)))
            )

    @commands.command(help="Enhance your image... or maybe deepfry it!")
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 60, commands.BucketType.user)
    async def enhance(self, ctx: commands.Context, user: Optional[discord.Member] = None, *, flags: EnhanceCmdFlags = None):
        user = user or ctx.author
        limit = 25

        if not flags:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(
                f"{EMOJIS['tick_no']}please mention some flags.\nExample: `{ctx.clean_prefix}enhance --contrast 10 --sharpness 20`\n\nAvailable flags: `contrast`, `color`, `sharpness`, `brightness`"
            )

        conditions = [
            flags.contrast > limit,
            flags.color > limit,
            flags.brightness > limit,
            flags.sharpness > limit,
            -1 * limit > flags.contrast,
            -1 * limit > flags.color,
            -1 * limit > flags.brightness,
            -1 * limit > flags.sharpness,
        ]
        if any(conditions):
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}The max limit for enhancements is `25`")

        amogus = {
            "contrast": flags.contrast,
            "color": flags.color,
            "brightness": flags.brightness,
            "sharpness": flags.sharpness
        }
        if user == ctx.author and len(ctx.message.attachments) != 0:
            for attachment in ctx.message.attachments:
                if attachment.content_type in ["image/png"]:
                    avatar_bytes = await attachment.read()
                    break
        else:
            avatar_bytes = await user.display_avatar.replace(format='png', size=512).read()
        async with ctx.channel.typing():
            await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, functools.partial(effects.enhance, avatar_bytes, **amogus))))

    @slash_command(name="enhance", help="Enhance or deepfry someone 😏")
    async def _enhance(
        self, ctx: InteractionContext, member: discord.Member = None,
        contrast: int = 15, color: int = 15, brightness: int = 15, sharpness: int = 15
    ):
        member = member or ctx.author
        avatar = await member.display_avatar.replace(format='png', size=512).read()
        limit = 30
        conditions = [
            contrast > limit,
            color > limit,
            brightness > limit,
            sharpness > limit,
            -1 * limit > contrast,
            -1 * limit > color,
            -1 * limit > brightness,
            -1 * limit > sharpness,
        ]
        if any(conditions):
            return await ctx.reply(f"{EMOJIS['tick_no']}The max limit for enhancements is `{limit}`", ephemeral=True)
        await ctx.response.defer()
        amogus = {
            "contrast": contrast,
            "color": color,
            "brightness": brightness,
            "sharpness": sharpness
        }
        path = await self.client.loop.run_in_executor(None, functools.partial(effects.enhance, avatar, **amogus))
        await ctx.followup.send(file=discord.File(path))

    @commands.command(help="Wiggle your friends...")
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.bot_has_permissions(attach_files=True)
    @slash_command(
        help="Wiggle your friends...",
        options=[SlashCommandOption(name='person', type=6, description="Pick someone to wiggle!", required=True)]
    )
    async def wiggle(self, ctx: Union[commands.Context, InteractionContext], *, person: Optional[Union[discord.Member, discord.PartialEmoji]] = None):
        if ctx.guild.id in wiggle_concurrency:
            text = f"{EMOJIS['tick_no']}Wiggling is already running in this guild!\nDue to this command being resource intensive, it can only be run one at a time per guild."
            if isinstance(ctx, InteractionContext):
                return await ctx.reply(text, ephemeral=True)
            else:
                return await ctx.reply(text)
        thingy_bytes = None
        if not person:
            if not person and len(ctx.message.attachments) == 0:
                thingy_bytes = await ctx.author.display_avatar.replace(format='png', size=128).read()
            elif not person and len(ctx.message.attachments) != 0:
                for attachment in ctx.message.attachments:
                    if attachment.content_type == "image/png":
                        thingy_bytes = await attachment.read()
                        break
                thingy_bytes = thingy_bytes or await ctx.author.display_avatar.replace(format='png', size=128).read()
        else:
            thingy_bytes = await person.display_avatar.replace(format='png', size=128).read() if isinstance(person, discord.Member) else await person.read()

        if isinstance(ctx, InteractionContext):
            await ctx.response.defer()
            wiggle_concurrency.append(ctx.guild.id)
            file = discord.File(await self.client.loop.run_in_executor(None, functools.partial(gif_effects.wiggle, img=thingy_bytes)))
            wiggle_concurrency.remove(ctx.guild.id)
            await ctx.followup.send(file=file)
        else:
            async with ctx.typing():
                file = discord.File(await self.client.loop.run_in_executor(None, functools.partial(gif_effects.wiggle, img=thingy_bytes)))
                await ctx.send(file=file)

    @commands.command(help="Why...", aliases=['why'])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def disappointed(self, ctx: commands.Context, *, sentences: str = None):
        async def why_u_do_this():
            ctx.command.reset_cooldown(ctx)
            thing = functools.partial(memes.disappointed, f"{ctx.author.name} is using this command", "But they don't know how to use it")
            return await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, thing)))
        if sentences is None:
            return await why_u_do_this()
        thingies = sentences.split(",", 1)
        if len(thingies) < 2:
            return await why_u_do_this()
        if len(thingies[0]) > 100 or len(thingies[1]) > 100:
            ctx.command.reset_cooldown(ctx)
            thing = functools.partial(memes.disappointed, f"{ctx.author.name} is using this command", "They put more than 100 characters")
            return await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, thing)))

        thing = functools.partial(memes.disappointed, thingies[0], thingies[1])
        return await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, thing)))

    @commands.command(help="Panik... Kalm... PANIK!!!!", aliases=['kalm', 'panic'])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def panik(self, ctx: commands.Context, *, sentences: str = None):
        async def why_u_do_this():
            ctx.command.reset_cooldown(ctx)
            thing = functools.partial(
                memes.panik,
                f"{ctx.author.name} is using the panik command",
                "They don't know how to use it",
                "THEY DON'T KNOW HOW TO USE IT"
            )
            path = await self.client.loop.run_in_executor(None, thing)
            return await ctx.reply(file=discord.File(path))
        if sentences is None:
            return await why_u_do_this()
        thingies = sentences.split(",", 2)
        if len(thingies) < 3:
            return await why_u_do_this()
        if len(thingies[0]) > 100 or len(thingies[1]) > 100 or len(thingies[2]) > 100:
            ctx.command.reset_cooldown(ctx)
            thing = functools.partial(
                memes.panik,
                f"{ctx.author.name} is using the panik command",
                "They put more than 100 characters",
                "THEY PUT MORE THAN 100 CHARACTERS"
            )
            path = await self.client.loop.run_in_executor(None, thing)
            return await ctx.reply(file=discord.File(path))
        thing = functools.partial(memes.panik, thingies[0], thingies[1], thingies[2])
        path = await self.client.loop.run_in_executor(None, thing)
        return await ctx.reply(file=discord.File(path))

    @commands.command(help="My heart when...", aliases=['myheart'])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def my_heart(self, ctx: commands.Context, *, sentences: str = None):
        async def why_u_do_this():
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(
                None, functools.partial(
                    memes.my_heart,
                    "No one is using this command",
                    f"{ctx.author.name} is using this command",
                    "THEY DON'T KNOW HOW TO USE IT"
                )
            )
            return await ctx.reply(file=discord.File(path))
        if sentences is None:
            return await why_u_do_this()
        thingies = sentences.split(",", 2)
        if len(thingies) < 3:
            return await why_u_do_this()
        if len(thingies[0]) > 100 or len(thingies[1]) > 100 or len(thingies[2]) > 100:
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(
                None, functools.partial(
                    memes.my_heart,
                    "No one is using this command",
                    f"{ctx.author.name} is using this command",
                    "THEY PUT MORE THAN 100 CHARACTERS"
                )
            )
            return await ctx.reply(file=discord.File(path))
        return await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, functools.partial(memes.my_heart, thingies[0], thingies[1], thingies[2]))))

    @commands.command(help="The flex tape meme.", aliases=['tape', 'flex_tape'])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def flextape(self, ctx: commands.Context, user: Optional[discord.Member] = None, *, sentences: str = None):
        if sentences is None:
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(None, functools.partial(
                memes.flex_tape,
                "Leaving the command empty",
                "please type some sentences while using this command",
                "ryuk"
            ))
            return await ctx.reply(file=discord.File(path))
        thingies = sentences.split(',', 1)
        if len(thingies) < 2:
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(None, functools.partial(
                memes.flex_tape,
                "Someone doesn't know how to use the flex tape command",
                "please put 2 sentences seperated with a comma",
                "ryuk"
            ))
            return await ctx.reply(file=discord.File(path))
        if len(thingies[0]) > 100 or len(thingies[1]) > 100:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}The maximum length of a sentence is **100** characters.")
        return await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, functools.partial(memes.flex_tape, thingies[0], thingies[1], None if not user else user.name))))

    @commands.command(help="I am once again asking for...", aliases=['asking', 'once_again', 'onceagain'])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def bernie(self, ctx: commands.Context, *, text: str = None):
        if text is None:
            text = "for you to enter some text."
        if len(text) > 100:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}A bit too much there... max character limit is **100**.")
        return await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, functools.partial(memes.bernie, text))))

    @commands.command(help="The Drake meme.")
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def drake(self, ctx: commands.Context, *, sentences: str = None):
        if sentences is None:
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(None, functools.partial(
                memes.drake,
                "Putting 2 sentences seperated with a comma in ryuk's drake command",
                "Leaving it empty"
            ))
            return await ctx.reply(file=discord.File(path))
        thingies = sentences.split(',', 1)
        if len(thingies) < 2:
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(None, functools.partial(
                memes.drake,
                "Putting 2 sentences seperated with a comma in ryuk's drake command",
                "Putting only 1"
            ))
            return await ctx.reply(file=discord.File(path))
        if len(thingies[0]) > 100 or len(thingies[1]) > 100:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}The maximum length of a sentence is **100** characters.")
        return await ctx.reply(file=discord.File(await self.client.loop.run_in_executor(None, functools.partial(memes.drake, thingies[0], thingies[1]))))

    @commands.command(help="Create the Buff Doge vs. Cheems meme!", aliases=['cheems'])
    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def doge(self, ctx: commands.Context, *, sentences: str = None):
        if sentences is None:
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(None, functools.partial(
                memes.doge,
                "Putting 2 sentences seperated with a comma",
                "Being a lazy idiot and not putting any"
            ))
            return await ctx.reply(file=discord.File(path))
        thingies = sentences.split(',', 1)
        if len(thingies) < 2:
            ctx.command.reset_cooldown(ctx)
            path = await self.client.loop.run_in_executor(None, functools.partial(
                memes.doge,
                "Putting 2 sentences seperated with a comma",
                "Putting only 1"
            ))
            return await ctx.reply(file=discord.File(path))
        if len(thingies[0]) > 100 or len(thingies[1]) > 100:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}The maximum length of a sentence is **100** characters.")
        path = await self.client.loop.run_in_executor(None, functools.partial(memes.doge, thingies[0], thingies[1]))
        return await ctx.reply(file=discord.File(path))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", help="Get a random anime image.")
    async def anime(self, ctx):
        await ctx.message.reply(embed=await self.get_img_from_api(["uwu", PINK_COLOR_2], "https://shiro.gg/api/images/neko", 'url'))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", aliases=['meow', 'cats'], help="Gives a random cute cat picture.")
    async def cat(self, ctx):
        await ctx.message.reply(embed=await self.get_img_from_api(["Meow!", MAIN_COLOR], "http://aws.random.cat/meow", 'file'))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", aliases=['dogs'], help="Gives a random cute dog picture.")
    async def dog(self, ctx):
        await ctx.message.reply(embed=await self.get_img_from_api(["Woof!", MAIN_COLOR], "https://some-random-api.ml/img/dog", 'link'))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", help="Gives a random cute fox picture.")
    async def fox(self, ctx):
        await ctx.message.reply(embed=await self.get_img_from_api(["Fox!", MAIN_COLOR], "https://randomfox.ca/floof/", 'image'))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", help="Gives a random panda picture.")
    async def panda(self, ctx):
        await ctx.message.reply(embed=await self.get_img_from_api(["Panda!", MAIN_COLOR], "https://some-random-api.ml/img/panda", 'link'))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", help="Gives a random redpanda picture.")
    async def redpanda(self, ctx):
        await ctx.message.reply(embed=await self.get_img_from_api(["Panda but red!", MAIN_COLOR], "https://some-random-api.ml/img/red_panda", 'link'))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", aliases=['pika'], help="Gives a random pikachu picture.")
    async def pikachu(self, ctx):
        await ctx.message.reply(embed=await self.get_img_from_api(["Pika!", MAIN_COLOR], "https://some-random-api.ml/img/pikachu", 'link'))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", help="Makes a youTube comment.")
    async def comment(self, ctx, *, message=None):
        PREFIX = ctx.clean_prefix
        if message is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.message.reply(embed=error_embed("Error!", f"Incorrect Usage! Use like this: `{PREFIX}comment <text>`"))
        url = f"https://some-random-api.ml/canvas/youtube-comment?avatar={ctx.author.display_avatar.with_format('png')}&username={ctx.author.name}&comment={message}"
        await ctx.send(embed=discord.Embed(color=MAIN_COLOR).set_image(url=url.replace(" ", "%20")))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(category="images", help="The user is wasted (meme)")
    async def wasted(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        url = f"https://some-random-api.ml/canvas/wasted?avatar={user.display_avatar.with_format('png')}"
        await ctx.send(embed=discord.Embed(color=MAIN_COLOR).set_image(url=url))


def setup(client):
    client.add_cog(image(client))
