# Std Lib Imports
import sys
import asyncio
import signal

# 3rd Party Imports
from discord.ext import commands
import discord

# Local Imports
from cogs import *
from utils import load_config, setup_logger

config = load_config()
setup_logger(config.log_level)

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix=config.bot_prefix, intents=intents)

    bot.change_presence(activity=discord.Game(name=f"TF2 Servers"))

    #load cogs
    bot.add_cog(Test(bot))
    bot.add_cog(Server())

    # Setup Asyncio Loop
    bot.loop.add_signal_handler(signal.SIGINT, lambda: bot.loop.stop())
    bot.loop.add_signal_handler(signal.SIGTERM, lambda: bot.loop.stop())

    future = asyncio.ensure_future(start(bot, config.bot_token), loop=bot.loop)
    future.add_done_callback(lambda f: bot.loop.stop())

    try:
        bot.loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        future.remove_done_callback(bot.loop.stop)
        discord.client._cleanup_loop(bot.loop)

async def start(bot, token):

    try:
        await bot.start(token)
    finally:
        if not bot.is_closed:
            await bot.close()

if __name__ == "__main__":
    main()