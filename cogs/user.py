import operator
from typing import List, Optional
from utils.classes import Profile
from utils.converters import Lower
import discord
import time

from discord.ext import commands
from config import (
    RANK_CARD_SUBMIT_CHANNEL,
    USER_REPORT_CHANNEL,
    EMOJIS, VOTE_LINK, TOP_GG_TOKEN,
    EMPTY_CHARACTER, MAIN_COLOR, WEBSITE_LINK, SUPPORT_SERVER_LINK,
    ryuk_GUILD_ID, PARTNER_ROLE, OWNER_ROLE, BOT_MOD_ROLE,
    STAFF_ROLE, SUPPORTER_ROLE, BOOSTER_ROLE, DESIGN_HELPER_ROLE,
    BIG_PP_GANG, NO_PP_GANG, BADGE_EMOJIS, DEFAULT_BANNED_WORDS,
    PINK_COLOR_2, RED_COLOR, ORANGE_COLOR
)
from cogs_hidden.leveling import rank_card_templates
from humanfriendly import format_timespan
from utils.custom_checks import check_voter, check_supporter
from utils.bot import ryuk
from utils.ui import Confirm, Paginator
from utils.embed import success_embed, error_embed


class user(commands.Cog, description="Commands related to the user!"):
    def __init__(self, client: ryuk):
        self.client = client
        self.default_vote_dict = {
            "top.gg": 0,
            "bots.discordlabs.org": 0,
            "reminders": False,
            "last_voted": {}
        }

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(help="Check if a user has voted or not!")
    async def checkvote(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            user = ctx.author
        async with self.client.session.get(f'https://top.gg/api/bots/751100444188737617/check?userId={user.id}', headers={'Authorization': TOP_GG_TOKEN}) as r:
            pain = await r.json()
            if pain['voted'] == 1:
                voted = True
            else:
                voted = False
            if voted:
                title = f"{EMOJIS['poglep']} Poggers!"
                description = "you have voted in the last **12** hours."
                embed = success_embed(title, description)
            else:
                title = f"{EMOJIS['weirdchamp']} Not pog!"
                description = f"you haven't voted in the last **12** hours.\nClick **[here]({VOTE_LINK})** to vote!"
                embed = error_embed(title, description)
            return await ctx.reply(embed=embed)

    @commands.command(help="Check your total votes!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def votes(self, ctx: commands.Context, user: Optional[discord.User] = None):
        user = user or ctx.author
        up = await self.client.get_user_profile_(user.id)
        vote_dict = up.votes
        top_gg_time = f"<t:{vote_dict['last_voted'].get('top.gg')}:R>" if 'top.gg' in vote_dict['last_voted'] else "Not voted currently."
        bots_discordlabs_org_time = f"<t:{vote_dict['last_voted'].get('bots.discordlabs.org')}:R>" if 'bots.discordlabs.org' in vote_dict['last_voted'] else "Not voted currently."
        discordbotlist_com_time = f"<t:{vote_dict['last_voted'].get('discordbotlist.com')}:R>" if 'discordbotlist.com' in vote_dict['last_voted'] else "Not voted currently."

        total = vote_dict.get("top.gg", 0) + vote_dict.get("bots.discordlabs.org", 0) + vote_dict.get("discordbotlist.com", 0)
        embed = success_embed(
            "your Votes",
            f"""
- **[top.gg](https://top.gg/bot/{self.client.user.id})**: `{vote_dict["top.gg"]}` - {top_gg_time}
- **[discordlabs.org](https://bots.discordlabs.org/bot/{self.client.user.id})**: - `{vote_dict["bots.discordlabs.org"]}` - {bots_discordlabs_org_time}
- **[discordbotlist.com](https://discordbotlist.com/bots/{self.client.user.id})**: - `{vote_dict.get("discordbotlist.com", 0)}` - {discordbotlist_com_time}
- **Total:** `{total}`
            """
        ).set_author(name=user, icon_url=user.display_avatar.url
        ).set_thumbnail(url="https://cdn.discordapp.com/emojis/882239026688569434.png"
        ).set_footer(text=f"you have vote reminders {'✅ Enabled' if vote_dict['reminders'] else '❌ Disabled'}", icon_url=self.client.user.display_avatar.url)
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def votereminder(self, ctx: commands.Context):
        up = await self.client.get_user_profile_(ctx.author.id)
        vote_dict = up.votes
        vote_dict["reminders"] = not vote_dict["reminders"]
        stuff = {"votes": vote_dict}
        await self.client.update_user_profile_(ctx.author.id, **stuff)
        await ctx.reply(f"Vote reminders are now {'enabled 💋' if vote_dict['reminders'] else 'disabled'}.")

    @commands.cooldown(3, 30, commands.BucketType.user)
    @commands.command(help="Check how many invites you have!")
    async def invites(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            user = ctx.author
        prefix = ctx.clean_prefix
        guild_config = await self.client.get_guild_config(ctx.guild.id)
        if guild_config['welcome']['channel_id'] is None:
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} Not enabled!",
                f"Welcome messages and invite tracking is not enabled yet!\nplease use `{prefix}welcome` to enable it!"
            ))
        all_ = await self.client.fetch_invites(user.id, ctx.guild.id, 'all')
        real = all_[0]
        fake = all_[1]
        left = all_[2]
        total = real + left + fake
        embed = discord.Embed(
            description=f"you have **{real}** invites (**{total}** total, **{'-' if left != 0 else ''}{left}** left, **{'-' if fake != 0 else ''}{fake}** fake)",
            color=MAIN_COLOR
        ).set_author(name=user, icon_url=user.display_avatar.url)
        await ctx.reply(embed=embed)

    async def get_actions_leaderboard(self, action_type: str) -> List[dict]:
        cursor = self.client.user_profile_db.find({}).sort([(action_type, -1)]).limit(50)
        final = await cursor.to_list(length=None)
        return final

    @commands.cooldown(3, 30, commands.BucketType.user)
    @commands.command(aliases=['lb'], help="Check the leaderboard!")
    async def leaderboard(self, ctx, option: Lower = None):
        guild_config = await self.client.get_guild_config(ctx.guild.id)
        prefix = ctx.clean_prefix
        lb_options = ['invites', 'levels', 'messages', 'votes']
        action_options = ['times_simped', 'times_thanked', 'bites', 'blushes', 'cries', 'cuddles', 'facepalms', 'feeds', 'hugs', 'kisses', 'licks', 'pats', 'slaps', 'tail_wags', 'tickles', 'winks']
        options_text = ""
        for e in lb_options:
            options_text += f"`{e}` "
        for e in action_options:
            options_text += f"`{e.replace('times_simped', 'simps').replace('times_thanked', 'thanks')}` "
        embed = discord.Embed(color=MAIN_COLOR)
        embed.title = "Leaderboard"
        if option is not None:
            embed.title = "Leaderboard" if option not in lb_options else option.title() + " Leaderboard"
        embed.set_thumbnail(url=self.client.user.display_avatar.url)
        embed.add_field(
            name=EMPTY_CHARACTER,
            value=f"[invite ryuk]({WEBSITE_LINK}/invite)  [support server]({SUPPORT_SERVER_LINK})",
            inline=False
        )
        main = ""
        if option == "thanks":
            option = "times_thanked"
        if option == "simps":
            option = "times_simped"
        if option is None or option == "":
            embed.description = f"please select an option for the leaderboard.\n\n**Options:** {options_text}"
        elif option in ['invites']:
            if guild_config['welcome']['channel_id'] is None:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} Not enabled!",
                    "please enable welcome messages to enable invite tracking."
                ))
            cursor = self.client.invites.find({})
            the_whole_fucking_db = await cursor.to_list(length=None)
            yes = {}
            for e in the_whole_fucking_db:
                if "guilds" in e:
                    if str(ctx.guild.id) in e['guilds'] and "real" in e['guilds'][str(ctx.guild.id)]:
                        yes.update({e['_id']: e['guilds'][str(ctx.guild.id)]['real']})
            yes = dict(sorted(yes.items(), key=operator.itemgetter(1), reverse=True))
            if ctx.author.id in yes:
                main += f"you are rank **#{list(yes).index(ctx.author.id) + 1}** in this server for {option}\n\n"

            i = 1
            for e in yes:
                if i > 10:
                    break
                main += f"`{i}.` <@{e}> - **{yes[e]}** invites\n"
                i += 1
            if len(yes) == 0:
                main = "All members have **0** invites in this guild."
            embed.description = main
        elif option in ['msgs', 'messages']:
            return await ctx.invoke(self.client.get_command('messages_lb'))
        elif option in ['levels', 'rank']:
            return await ctx.invoke(self.client.get_command('leveling_lb'))
        elif option in ['votes']:
            return await ctx.invoke(self.client.get_command('vote_lb'))
        elif option in action_options:
            paginator = commands.Paginator(prefix="", suffix="", max_size=500)
            actions = await self.get_actions_leaderboard(option)
            if len(actions) == 0:
                return await ctx.reply("No users found.")
            for i, e in enumerate(actions):
                amount = e.get(option, 0)
                if amount > 0:
                    paginator.add_line(f"`{i + 1}.` <@{e['_id']}> • `{amount}` {option.replace('times_thanked', 'thanks').replace('times_simped', 'simps')}")
            embeds = [success_embed(f"{EMOJIS['tick_yes']} {option.replace('times_thanked', 'thanks').replace('times_simped', 'simps').title()} Leaderboard", page) for page in paginator.pages]
            if len(embeds) == 0:
                return await ctx.reply("No users found.")
            if len(embeds) == 1:
                return await ctx.reply(embed=embeds[0])
            view = Paginator(ctx, embeds=embeds)
            return await ctx.reply(embed=embeds[0], view=view)
        else:
            embed.description = f"Invalid option! please use `{prefix}leaderboard` to see the available options."

        await ctx.reply(embed=embed)

    @commands.command(help="Check your rank!")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def rank(self, ctx, user_: discord.Member = None, template=None):
        if user_ is None:
            user_ = ctx.author
        await ctx.invoke(self.client.get_command('rank_'), user=user_)

    @commands.command(help="Check your number of messages!", aliases=['msgs'])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def messages(self, ctx, user_: discord.Member = None):
        if user_ is None:
            user_ = ctx.author
        await ctx.invoke(self.client.get_command('messages_'), user=user_)

    @commands.command(help="Configure your rank cards!")
    @commands.cooldown(3, 20, commands.BucketType.user)
    async def rankcard(self, ctx: commands.Context, configuration=None, card=None, *, description=None):
        prefix = ctx.clean_prefix
        if configuration is None:
            return await ctx.reply(embed=success_embed(
                f"{EMOJIS['leveling']} Rank card settings",
                f"""
**you can configure your rank card using the following commands:**

- `{prefix}rankcard discover` - Discover new rank cards!
- `{prefix}rankcard set <card>` - Set your current rank card.
- `{prefix}rankcard preview <card>` - Preview a rank card.
- `{prefix}rankcard submit <card>` - Submit a rank card for review.
                """
            ))
        if configuration.lower() in ['set']:
            if card is None:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} please enter a card",
                    f"please enter a card next time.\nExample: `{prefix}rankcard set awish`"
                ))
            if card.lower() not in rank_card_templates:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} Invalid card template.",
                    f"please use `{prefix}rankcard discover` to find valid templates!"
                ))
            await self.client.update_user_profile_(ctx.author.id, rank_card_template=card.lower())
            return await ctx.reply(embed=success_embed(
                f"{EMOJIS['tick_yes']} Card template updated!",
                f"your rank card template has now been set to: `{card}`"
            ))
        if configuration.lower() in ['preview']:
            if card is None:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} please enter a card",
                    f"please enter a card next time.\nExample: `{prefix}rankcard preview awish`"
                ))
            if card.lower() not in rank_card_templates:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} Not found!",
                    f"Rank card named `{card}` doesn't exist."
                ))
            return await ctx.invoke(
                self.client.get_command('rank_from_template'),
                member=ctx.author,
                template=card.lower()
            )
        if configuration.lower() in ['discover']:
            nice = ""
            i = 1
            for e in rank_card_templates:
                nice += f"`{i}. ` • `{e}` • {rank_card_templates[e]['description']} • By <@{rank_card_templates[e]['owner']}>\n"
                i += 1
            nice += f"\nyou can use `{prefix}rankcard preview <card>` to preview a card!"
            embed = success_embed(
                "🧭  Rank cards!",
                nice
            )
            return await ctx.reply(embed=embed)
        if configuration.lower() in ['submit']:
            example = f"`{prefix}rankcard submit beauty A beautiful rankcard by Nirlep!`"
            if card is None:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} invalid usage",
                    f"""
please give a name to your submission.
Example: {example}
Make sure to upload image as an attachment.
                    """
                ))
            if card.lower() in rank_card_templates:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} Already exists!",
                    f"A rank card named `{card}` already exists."
                ))
            if description is None:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} invalid usage",
                    f"""
please give a description to your submission.
Example: {example}
Make sure to upload image as an attachment.
                    """
                ))
            if len(ctx.message.attachments) == 0:
                return await ctx.reply(embed=error_embed(
                    f"{EMOJIS['tick_no']} No rank card found!",
                    "Make sure to upload your rank card in the message!"
                ))
            await self.client.get_channel(RANK_CARD_SUBMIT_CHANNEL).send(
                "<@558861606063308822>",
                embed=success_embed(
                    "📨  New rank card submitted!",
                    f"""
**Name:** `{card.lower()}`
**Description:** `{description}`
                    """
                ),
                file=await ctx.message.attachments[0].to_file()
            )
            return await ctx.reply(embed=success_embed(
                f"{EMOJIS['tick_yes']} Rank card submitted!",
                "your rank card has successfully been submitted!"
            ))

        return await ctx.reply(embed=error_embed(
            f"{EMOJIS['tick_no']} Invalid option!",
            f"please use `{prefix}rankcard` to see all the available options!"
        ))

    @commands.command(help="Thank someone!")
    @commands.cooldown(2, 120, commands.BucketType.user)
    async def thank(self, ctx: commands.Context, user_: discord.Member = None, *, reason=None):
        prefix = ctx.clean_prefix
        if user_ is None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} please mention a user to thank!",
                f"Correct usage: `{prefix}thank @user`"
            ))
        if user_ == ctx.author:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} error",
                "you cannot thank yourself! Idiot!"
            ))
        if user_.bot:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} you can't thank bots!",
                f"Thank real people! {EMOJIS['vay']}"
            ))

        if reason is None:
            reason = "being an amazing person!"
        if reason.lower().startswith("for "):
            reason = reason[4:]

        user_profile = await self.client.get_user_profile_(user_.id)
        await self.client.update_user_profile_(user_.id, times_thanked=user_profile.times_thanked + 1)

        return await ctx.reply(embed=success_embed(
            f"{EMOJIS['heawt']} Thank you!",
            f"Thank you {user_.mention} for {reason}"
        ).set_footer(text=f"They have been thanked {user_profile.times_thanked + 1} times!"
        ).set_thumbnail(url="https://cdn.discordapp.com/emojis/856078862852161567.png?v=1"))

    async def get_badges(self, user_id: int, user_profile: Profile) -> list:
        guild = self.client.get_guild(ryuk_GUILD_ID)
        if not guild:
            return []
        member = guild.get_member(user_id)
        wew = []
        badge_roles = {
            "owner_of_epicness": OWNER_ROLE,
            "bot_mod": BOT_MOD_ROLE,
            "staff_member": STAFF_ROLE,
            "partner": PARTNER_ROLE,
            "supporter": SUPPORTER_ROLE,
            "booster": BOOSTER_ROLE,
            "designer": DESIGN_HELPER_ROLE,
            # "cutie": VIP_ROLE,
        }

        people_badges = {
            "aw||oo||sh": 671355502399193128,
            "wendo": 478623992337530883,
            "cutevi": 679677267164921866,
            "cat": 344313283714613248,
            "best_streamer": 91090336029347840,
            "very_good_taste": 729765852030828674
        }

        for e in people_badges:
            if user_id == people_badges[e]:
                wew.append(e)

        if member:
            for e in badge_roles:
                if guild.get_role(badge_roles[e]) in member.roles:
                    wew.append(e)

            if int(member.joined_at.strftime("%Y")) < 2021:
                wew.append("early_supporter")

        if user_profile.bugs_reported >= 25:
            wew.append("bug_hunter")
        if user_profile.bugs_reported >= 50:
            wew.append("elite_bug_hunter")

        if user_profile.times_simped >= 25:
            wew.append("samsung_girl")
        if user_profile.times_simped >= 50:
            wew.append("love_magnet")

        if user_profile.times_thanked >= 25:
            wew.append("helper")
        if user_profile.times_thanked >= 50:
            wew.append("savior")
        if user_id in BIG_PP_GANG:
            wew.append("Big_PP")
        if user_id in NO_PP_GANG:
            wew.append("No_PP")

#        voted = await check_voter(user_id)
#        if voted:
#            wew.append("voter")

        return wew

    @commands.command(help="Check your profile!")
    @commands.cooldown(3, 15, commands.BucketType.user)
    async def profile(self, ctx: commands.Context, user_: discord.Member = None):
        if user_ is None:
            user_ = ctx.author

        if user_.bot:
            return await ctx.reply(f"{EMOJIS['tick_no']}Bots don't have profiles.")

        user_profile = await self.client.get_user_profile_(user_.id)

        async with ctx.typing():
            # await ctx.invoke(
            #     self.client.get_command('rank_from_template'),
            #     member=user_,
            #     template=user_profile['rank_card_template'],
            #     reply=False
            # )

            nice = f"""
    {user_profile.description}

    **{'Single 💔' if not user_profile.married_to else 'Married to <@'+str(user_profile.married_to)+'> 💞'}**
    {'**Married at:** <t:' + str(user_profile.married_at) + ':D> <t:' + str(user_profile.married_at) + ':R>' if user_profile.married_to is not None else ''}

    Commands Used: `{user_profile.cmds_used}`
    Bugs reported: `{user_profile.bugs_reported}`
    Suggestions given: `{user_profile.suggestions_submitted}`

    Thanked by **{user_profile.times_thanked}** user{'s' if user_profile.times_thanked != 1 else ''}!
    Simped by **{user_profile.times_simped}** simp{'s' if user_profile.times_simped != 1 else ''}!

    Global chat nick: `{user_profile.gc_nick}`
    Global chat avatar: [`{'Click Me' if user_profile.gc_avatar is not None else 'None'}`]({user_profile.gc_avatar if user_profile.gc_avatar is not None else ''})
                    """
            badge_text = ""
            badge_text2 = ""
            badge_text3 = ""
            badge_text4 = ""
            badge_text5 = ""

            h = await self.get_badges(user_.id, user_profile)

            for e in user_profile.badges:
                h.append(e)

            i = 1

            for e in h:
                hee = BADGE_EMOJIS[e] + f"  {e.title().replace('_', ' ')}\n"
                if e == "Big_PP" or e == "No_PP":
                    hee = BADGE_EMOJIS[e] + f"  {e.replace('_', ' ')}\n"
                pain = 5
                if i <= pain:
                    badge_text += hee
                if i > pain and i <= 2 * pain:
                    badge_text2 += hee
                if i > 2 * pain and i <= 3 * pain:
                    badge_text3 += hee
                if i > 3 * pain and i <= 4 * pain:
                    badge_text4 += hee
                if i > 4 * pain and i <= 5 * pain:
                    badge_text5 += hee
                i += 1

            # f = discord.File("assets/temp/rank.png", filename="rank.png")
            embed = discord.Embed(
                description=nice,
                color=MAIN_COLOR
            ).set_author(name=user_.name, icon_url=user_.display_avatar.url
            )  # .set_image(url="attachment://rank.png")

            embed.add_field(name="Badges:", value=badge_text, inline=True)

            if badge_text2 != "":
                embed.add_field(name=EMPTY_CHARACTER, value=badge_text2, inline=True)
            if badge_text3 != "":
                embed.add_field(name=EMPTY_CHARACTER, value=EMPTY_CHARACTER, inline=True)
                embed.add_field(name=EMPTY_CHARACTER, value=badge_text3, inline=True)
            if badge_text4 != "":
                embed.add_field(name=EMPTY_CHARACTER, value=badge_text4, inline=True)
                embed.add_field(name=EMPTY_CHARACTER, value=EMPTY_CHARACTER, inline=True)
            if badge_text5 != "":
                embed.add_field(name=EMPTY_CHARACTER, value=badge_text5, inline=True)

            embed.add_field(
                name=EMPTY_CHARACTER,
                value=f"your current rankcard template is `{user_profile.rank_card_template}`:",
                inline=False
            ).set_thumbnail(url=user_.display_avatar.url)

            await ctx.reply(embed=embed)

    @commands.command(help="Edit your profile.", aliases=['eprofile', 'editp'])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def editprofile(self, ctx: commands.Context, thing=None, *, new_thing=None):
        prefix = ctx.clean_prefix
        info_embed = success_embed(
            "📝  Edit profile",
            f"""
**To edit your profile, you can use the following commands:**

- `{prefix}editprofile bio <new bio>` - To edit your bio.
- `{prefix}editprofile nick <nickname>` - Change your nickname for global chat.
- `{prefix}editprofile avatar` - Change your avatar for global chat.

- `{prefix}editprofile resetnick` - Reset your nickname.
- `{prefix}editprofile resetavatar` - Reset your avatar.

**Note:** Any NSFW avatars/names will get you blacklisted.
            """
        )
        if thing is None:
            return await ctx.reply(embed=info_embed)

        if thing.lower() in ['nick', 'nickname']:
            if not await check_voter(ctx.author.id) and not await check_supporter(ctx):
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} Voter only!", "Global chat customization is limited to voters only, to avoid abuse."))
            if new_thing is None:
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} invalid usage", f"Correct Usage: `{prefix}editprofile nick <nickname>`"))
            if len(new_thing) > 32:
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} Too long!", "Nicknames cannot be greater than **32** characters."))
            for word in DEFAULT_BANNED_WORDS:
                if word in new_thing.lower():
                    return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} No Bad Words!", "Nicknames cannot contain bad words."))
            if "#" in new_thing:
                you_little_shit = new_thing.split('#')
                if len(you_little_shit) == 2:
                    impostor = discord.utils.get(self.client.users, name=you_little_shit[0], discriminator=you_little_shit[1])
                    if impostor is not None:
                        return await ctx.reply("Stop trying to impersonate people.")
            await self.client.update_user_profile_(ctx.author.id, gc_nick=new_thing)
            return await ctx.reply(f"you global chat nickname has been updated to `{new_thing}`")

        if thing.lower() in ['bio', 'description']:
            if new_thing is None:
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} invalid usage", f"Correct Usage: `{prefix}editprofile nick <nickname>`"))
            if len(new_thing) > 250:
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} Too long!", "your bio can't be greater than **250** characters."))
            for word in DEFAULT_BANNED_WORDS:
                if word in new_thing.lower():
                    return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} No Bad Words!", "your bio cannot contain bad words."))
            await self.client.update_user_profile_(ctx.author.id, description=new_thing)
            return await ctx.reply("your bio has been updated.")

        if thing.lower() in ['avatar', 'pfp', 'av']:
            if not await check_voter(ctx.author.id) and not await check_supporter(ctx):
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} Voter only!", "Global chat customization is limited to voters only, to avoid abuse."))
            if len(ctx.message.attachments) == 0:
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} No image found!", "you need to upload an image while using this command."))
            if len(ctx.message.attachments) > 1:
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} error", "Enter a **single** image while using this command."))
            if ctx.message.attachments[0].content_type != "image/png":
                return await ctx.reply(embed=error_embed(f"{EMOJIS['tick_no']} PNGs only!", "Only `png` format is allowed."))
            files = []
            files.append(await ctx.message.attachments[0].to_file())
            msg = await self.client.get_channel(864000707798761513).send(f"{ctx.author.mention} {ctx.author.id}", files=files)
            await self.client.update_user_profile_(ctx.author.id, gc_avatar=msg.attachments[0].url)
            return await ctx.reply("your global chat avatar has been updated.")

        if thing.lower() in ['resetnick']:
            await self.client.update_user_profile_(ctx.author.id, gc_nick=None)
            return await ctx.reply("your global chat nickname has been reset.")

        if thing.lower() in ['resetavatar', 'resetav', 'resetpfp']:
            await self.client.update_user_profile_(ctx.author.id, gc_avatar=None)
            return await ctx.reply("your global chat avatar has been reset.")

        return await ctx.reply(embed=info_embed)

    @commands.command(help="Marry someone... <:KannaBlush:868725856971927552>")
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def marry(self, ctx: commands.Context, user: discord.Member = None, *, proposal_text: str = None):
        if not user:
            return await ctx.reply(f"Correct Usage: `{ctx.clean_prefix}marry @user please marry me uwu`")
        if user.bot:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}you cannot marry bots.")
        if user == ctx.author:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply("Imagine marrying yourself... Why are you so lonely...")
        user_profile = await self.client.get_user_profile_(ctx.author.id)
        victim_profile = await self.client.get_user_profile_(user.id)
        if user_profile.married_to is not None:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}you are already married to: <@{user_profile.married_to}>\nDon't cheat on them >")
        if victim_profile.married_to:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}{user.mention} is already married to: <@{victim_profile.married_to}>")

        view = Confirm(context=ctx, user=user)
        msg = await ctx.channel.send(
            user.mention,
            embed=discord.Embed(
                title="👉👈",
                description=proposal_text or "W-W-Would you like to marry me?... *blushes*",
                color=PINK_COLOR_2
            ).set_image(url="https://media1.tenor.com/images/58bd69fb056bd54b80c92581f3cd9cf9/tenor.gif?itemid=10799169"
            ).set_author(name=f"{ctx.author.name} 💘 {user.name}", icon_url=ctx.author.display_avatar.url),
            view=view,
            allowed_mentions=discord.AllowedMentions(
                users=True,
                roles=False,
                everyone=False,
                replied_user=False
            )
        )
        await view.wait()
        if view.value is None:
            return await msg.edit(
                content=f"looks like {user.mention} didn't respond in time... ",
                embed=None,
                view=None
            )
        elif not view.value:
            return await msg.edit(
                content="you got rejected!",
                embed=discord.Embed(
                    title="<a:cute_cry:868791322574745600>",
                    description=f"**{user.name}** denied your proposal ",
                    color=RED_COLOR
                ).set_image(url="https://media1.tenor.com/images/79b965bb99fd58b94d2550b384093e75/tenor.gif?itemid=13668435"
                ).set_author(name=f"{ctx.author.name} 💔 {user.name}", icon_url=ctx.author.display_avatar.url),
                view=None
            )
        await self.client.update_user_profile_(ctx.author.id, married_to=user.id, married_at=round(time.time()))
        await self.client.update_user_profile_(user.id, married_to=ctx.author.id, married_at=round(time.time()))
        return await msg.edit(
            content="WOOOO!!!",
            embed=discord.Embed(
                title="Such a cute couple...",
                description="This is the cutest thing ever!",
                color=PINK_COLOR_2
            ).set_image(url="https://media1.tenor.com/images/d0cd64030f383d56e7edc54a484d4b8d/tenor.gif?itemid=17382422"
            ).set_author(name=f"{ctx.author.name} 💞 {user.name}", icon_url=ctx.author.display_avatar.url),
            view=None
        )

    @commands.command(help="Divorce :C", aliases=['unmarry'])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def divorce(self, ctx: commands.Context):
        user_profile = await self.client.get_user_profile_(ctx.author.id)
        if not user_profile.married_to:
            ctx.command.reset_cooldown(ctx)
            return await ctx.reply(f"{EMOJIS['tick_no']}you are not married to anyone.")
        view = Confirm(context=ctx)
        msg = await ctx.reply(embed=discord.Embed(
            title="<a:cute_cry:868791322574745600>",
            description=f"Do you really want to divorce <@{user_profile.married_to}> ",
            color=RED_COLOR
        ),
            view=view)
        await view.wait()
        if view.value is None:
            return await msg.edit(content="you didn't answer in time.", embed=None, view=None)
        if not view.value:
            return await msg.edit(content="Ok, I have cancelled the command.", embed=None, view=None)
        time_ = user_profile.married_at
        await self.client.update_user_profile_(ctx.author.id, married_to=None, married_at=None)
        await self.client.update_user_profile_(user_profile.married_to, married_to=None, married_at=None)
        return await msg.edit(
            embed=discord.Embed(
                title="<a:cute_cry:868791322574745600>",
                description=f"your marriage lasted **{format_timespan(round(time.time()) - time_)}**",
                color=RED_COLOR
            ).set_image(url="https://media1.tenor.com/images/79b965bb99fd58b94d2550b384093e75/tenor.gif?itemid=13668435"),
            view=None
        )

    @commands.command(help="Check the available badges.", aliases=['badgelist'])
    @commands.cooldown(3, 30, commands.BucketType.user)
    async def badges(self, ctx):
        nice = ""
        for e in BADGE_EMOJIS:
            nice += f"{BADGE_EMOJIS[e]} {' '.join(e.split('_')).title()}\n"
        nice += "\nSome of these badges are unobtainable, more info on the coming soon:tm:"
        embed = success_embed(
            "All the available badges!",
            nice
        )
        await ctx.reply(embed=embed)

    @commands.command(help="Report a user!")
    @commands.cooldown(2, 600, commands.BucketType.user)
    async def report(self, ctx, user: discord.User = None, *, reason=None):
        if user is None or reason is None:
            prefix = ctx.clean_prefix
            return await ctx.reply(embed=error_embed(
                f"{EMOJIS['tick_no']} invalid usage",
                f"Correct Usage: `{prefix}report @user <reason>`\nExample: `{prefix}report @egirl abusing ryuk bug`\n\n**Note:** Spam reports will get you blacklisted."
            ))
        if user == self.client.user:
            return await ctx.reply("Bruh ._.")
        if user.bot:
            return await ctx.reply("you cannot report bots.")
        if user == ctx.author:
            return await ctx.reply(f"Imagine reporting urself... {EMOJIS['bruh']}")

        files = []
        for file in ctx.message.attachments:
            files.append(await file.to_file())

        report_channel = self.client.get_channel(USER_REPORT_CHANNEL)
        await report_channel.send(
            f"<@&{BOT_MOD_ROLE}>",
            embed=discord.Embed(
                title="User Reported",
                description=reason,
                color=ORANGE_COLOR
            ).set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url
            ).add_field(name="Reported User:", value=f"`{user} ({user.id})` {user.mention}", inline=False),
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                roles=True,
                users=False,
                replied_user=False
            ),
            files=files
        )
        await ctx.reply(f"{EMOJIS['tick_yes']} your report has been sent. please be patient for mods to review it.")

    @commands.command(name="opt-out", aliases=['optout', 'nosnipe'], help="Opt out of snipe")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def opt_out(self, ctx):
        user_profile = await self.client.get_user_profile_(ctx.author.id)

        snipe = user_profile.snipe
        await self.client.update_user_profile_(ctx.author.id, snipe=not snipe)

        pain = "\n\nyou also won't be able to use the snipe commands."
        await ctx.reply(embed=success_embed(
            f"{EMOJIS['tick_yes']} Snipe toggled!",
            f"your messages will {'no longer' if snipe else 'now'} be logged!{pain if snipe else ''}"
        ))


def setup(client):
    client.add_cog(user(client))
