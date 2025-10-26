import logging

import discord
from discord.ext import commands

from config import DISCORD_TOKEN, BOT_STATUS, RUN_WATCHERS

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# dummy prefix that goes unused
bot = commands.Bot(command_prefix='?', intents=intents)

initial_cogs = [
    "cogs.admin",
    "cogs.chatbot",
    "cogs.voice"
]

async def setup_hook():
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            logging.info(f"Loaded cog: {cog}")
        except Exception as e:
            logging.error(f"Failed to load cog {cog}: {e}")

@bot.event
async def on_ready():
    activity = discord.Game(name=BOT_STATUS)
    await bot.change_presence(status=discord.Status.online, activity=activity)

    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s).")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

    logging.info(f"Logged in as {bot.user}")

if __name__ == "__main__":
    if RUN_WATCHERS:
        # See README
        pass
    
    bot.setup_hook = setup_hook
    bot.run(DISCORD_TOKEN)