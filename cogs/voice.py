import discord
from discord import app_commands
from discord.ext import commands
from utils.queue import enqueue, skip_track, stop_all, get_queue

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="join", description="Joins your current voice channel.")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            return await interaction.response.send_message(
                embed=discord.Embed(description="You aren't in a channel.", color=0xffce19)
            )

        await interaction.response.defer()
        channel = interaction.user.voice.channel
        await channel.connect()

        embed = discord.Embed(description="Joined your channel.", color=0xffce19)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="leave", description="Leaves current voice channel.")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            msg = "Left the channel."
        else:
            msg = "I'm not in a voice channel."
        await interaction.response.send_message(embed=discord.Embed(description=msg, color=0xffce19))

    @app_commands.command(name="play", description="Plays or queues a YouTube URL.")
    @app_commands.describe(url="The YouTube URL or search query to play.")
    async def play(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer(thinking=True)

        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.followup.send(
                embed=discord.Embed(description="You must be in a voice channel first.", color=0xffce19)
            )

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if not vc:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        was_playing = await enqueue(self.bot, interaction, url)
        msg = "Track queued." if was_playing else "Starting playback..."
        await interaction.followup.send(embed=discord.Embed(description=msg, color=0x00FF00))

    @app_commands.command(name="skip", description="Skips the current track.")
    async def skip(self, interaction: discord.Interaction):
        await skip_track(interaction.guild)
        await interaction.response.send_message(embed=discord.Embed(description="Skipped current track.", color=0x00FF00))

    @app_commands.command(name="stop", description="Stops playback and clears the queue.")
    async def stop(self, interaction: discord.Interaction):
        await stop_all(interaction.guild)
        await interaction.response.send_message(embed=discord.Embed(description="Stopped playback and cleared queue.", color=0x00FF00))

    @app_commands.command(name="queue", description="Shows current music queue.")
    async def queue(self, interaction: discord.Interaction):
        items = await get_queue(interaction.guild)
        if not items:
            return await interaction.response.send_message(embed=discord.Embed(description="The queue is empty.", color=0x00FF00))

        desc = "\n".join(f"**{i+1}.** {title or 'Unknown'}" for i, (_, _, _, title) in enumerate(items))
        embed = discord.Embed(title="Current Queue", description=desc, color=0x00FF00)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Voice(bot))
