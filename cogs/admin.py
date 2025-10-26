import discord
from discord import app_commands
from discord.ext import commands
from utils.chat_gpt import ChatGPTHandler
from config import BOT_OWNER_ID

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Destroys all saved data. Configure which user can do this with BOT_OWNER_ID
    @app_commands.command(name="destroy", description="Deletes the data file.")
    async def destory(self, interaction: discord.Interaction):
        if (interaction.user.id == BOT_OWNER_ID):
            ChatGPTHandler.self_destruct()

            embed = discord.Embed(description="All chat logs and settings have been wiped across all servers.", color=0xffce19)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description="You lack sufficient permissions to use this command.", color=0xffce19)
            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))