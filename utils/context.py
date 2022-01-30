from discord.ext import commands
from typing import Any, Union, Optional
from uuid import uuid4
from asyncio import TimeoutError
import discord
import logging

class Context(commands.Context):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.id = uuid4()

    async def react(self, emoji: Union[discord.Emoji, discord.Reaction, discord.PartialEmoji, str],
                    *, raise_exceptions: bool = False) -> None:
        try:
            await self.message.add_reaction(emoji)
        except discord.HTTPException as e:
            logging.warning(f'Context React Error. {e.status}. {e.text}')
            if raise_exceptions:
                raise
    async def tick(self, status: Optional[bool] = True, *, raise_exceptions: bool = False) -> None:
        reactions = {
            True: '✅',
            False: '❌',
            None: '✖'
        }
        await self.react(reactions[status], raise_exceptions=raise_exceptions)
    async def confirmation_prompt(
            self, message: str, *, timeout: float = 30.0, ephemeral: bool = True
    ) -> Optional[bool]:
        confirmation_emojis = ['✅', '❌']
        prompt = await self.send(message)
        for emoji in confirmation_emojis:
            await prompt.add_reaction(emoji)
        def reaction_check(pl: discord.RawReactionActionEvent):
            return pl.message_id == prompt.id and \
                pl.member == self.author and \
                pl.event_type == 'REACTION_ADD' and \
                str(pl.emoji) in confirmation_emojis
        result = None
        try:
            payload = await self.bot.wait_for('raw_reaction_add', timeout=timeout, check=reaction_check)
        except TimeoutError:
            result = None
        else:
            result = True if str(payload.emoji) == '✅' else False
        finally:
            if ephemeral:
                await prompt.delete()
            return result