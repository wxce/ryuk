

from discord.ext import commands
from typing import Optional


class EnhanceCmdFlags(commands.FlagConverter, prefix="--", delimiter=" ", case_insensitive=True):
    contrast: Optional[float] = 1.0
    color: Optional[float] = 1.0
    brightness: Optional[float] = 1.0
    sharpness: Optional[float] = 1.0


class StickerFlags(commands.FlagConverter, prefix="--", delimiter=" ", case_insensitive=True):
    name: Optional[str] = None
    description: Optional[str] = None
    emoji: Optional[str] = None
