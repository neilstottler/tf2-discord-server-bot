# Std Lib Imports

# 3rd Party Imports
import discord
from discord.ext.commands import Cog, slash_command

# Local Imports
from utils import load_config

global_config = load_config()

class Test(Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="test",
        description="Test command.",
        guild_ids=[global_config.bot_guild_ids]
    )
    async def test(self, ctx):
        await ctx.respond('Test')