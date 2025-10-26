import discord
from discord import app_commands
from discord.ext import commands
from utils.chat_gpt import ChatGPTHandler
from datetime import datetime, timezone

class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Clears chat history
    @app_commands.command(name="clear", description="Clears chat history local to this channel.")
    async def clear(self, interaction: discord.Interaction):
        guild_id = "_" + str(interaction.channel_id)
        ChatGPTHandler.clear_history(guild_id)

        embed = discord.Embed(description="Cleared chat history while keeping current prompt.", color=0xffce19)
        await interaction.response.send_message(embed=embed)

    # Restores default prompt settings
    @app_commands.command(name="restore", description="Restores default settings local to this channel.")
    async def restore(self, interaction: discord.Interaction):
        guild_id = "_" + str(interaction.channel_id)
        ChatGPTHandler.restore_defaults(guild_id)

        embed = discord.Embed(description="Restored to default settings.", color=0xffce19)
        await interaction.response.send_message(embed=embed)

    # Sets prompt to new choice
    @app_commands.command(name="set-prompt", description="Sets the bot's personality prompt.")
    @app_commands.describe(value="The new prompt.")
    async def set_prompt(self, interaction: discord.Interaction, value: str):
        guild_id = "_" + str(interaction.channel_id)
        ChatGPTHandler.set_prompt(guild_id, value)

        embed = discord.Embed(description=f"Updated prompt and cleared chat history. \n\nNew prompt:\n{value}", color=0xffce19)
        await interaction.response.send_message(embed=embed)

    # Logs messages to data file and responds when prompted
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user or message.content.startswith("!ignore"):
            return
        
        username = message.author.global_name or message.author.name
        
        print(f'[{username}]: {message.content}')
        guild_id = "_" + str(message.channel.id)

        currentTime = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        ChatGPTHandler.add_chat_history(guild_id, f'[UTC_timestamp: {currentTime}][author: {username}][message: {message.content}]')
        print(f'Tokens - {ChatGPTHandler.count_tokens(guild_id)}')

        if message.content.startswith('!ping'):
            await message.channel.typing()
            reply = "pong!"
            embed = discord.Embed(description=reply, color=0xfe5835)
            await message.reply(embed=embed)

        if message.content.startswith('!chat'):
            await message.channel.typing()
            reply = ChatGPTHandler.generate_response(guild_id)

            print(f'[{self.bot.user}]: {reply} - {ChatGPTHandler.count_tokens(guild_id)}\n')

            embed = discord.Embed(description=reply, color=0xfe5835)
            await message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(ChatBot(bot))
