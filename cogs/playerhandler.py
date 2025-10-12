import functools
import logging
import os

import discord
from discord import Embed
from discord.ext import commands
from dotenv import load_dotenv

from musicplayer.ytdlplayer import YTDLPlayer

load_dotenv()

logger = logging.getLogger("beatbob")

TEST_GUILDS = [int(os.getenv("TESTGUILDID", 0))]


def ensure_same_voice_channel(func):
    """Decorator to make sure that the user is in the same voice channel as the music bot.

    Used to ensure that external users can't use the bot as a griefing tool.
    """

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        ctx: discord.ApplicationContext = kwargs.get("ctx")
        if ctx is None:
            if len(args) >= 1:
                ctx = args[0]  # first positional argument after self
            else:
                raise ValueError("No context found in decorator wrapper.")
        assert isinstance(ctx.author, discord.Member)

        # Check if the author is in a voice channel
        if not ctx.author.voice:
            return await ctx.respond("You must be in a voice channel.", ephemeral=True)

        # Get bot's voice client for this guild
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client or not voice_client.channel:
            return await ctx.respond(
                "I am not connected to a voice channel", ephemeral=True
            )

        # Compare the channels
        if ctx.author.voice.channel != voice_client.channel:
            return await ctx.respond(
                "You must be in the same voice channel as the bot to use that command",
                ephemeral=True,
            )

        # All good if in the same voice channel
        return await func(self, *args, **kwargs)

    return wrapper


class PlayerHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.players: dict[int, YTDLPlayer] = {}

    def get_player(self, guild: discord.Guild) -> YTDLPlayer:
        """Get player associated with guild.

        If player is not found for guild, a new one is created.

        Args:
            guild (discord.Guild): Guild for which player is looked for.

        Returns:
            YTDLPlayer: The player associated with guild.
        """
        if guild.id not in self.players:
            self.players[guild.id] = YTDLPlayer(self.bot, guild)
            logger.info(f"Created new player for guild {guild} (ID: {guild.id})")
        return self.players[guild.id]

    @commands.slash_command(
        description="You want Beatbob in your life <3", guilds=TEST_GUILDS
    )
    async def join(self, ctx: discord.ApplicationContext):
        """Joins a voice channel.

        Requires author to be in an accessible voice channel.

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        assert isinstance(
            ctx.author, discord.Member
        )  # NOTE Required to suppress pylance warning

        if not ctx.author.voice:
            return await ctx.respond("You must be in a voice channel.", ephemeral=True)
        channel = ctx.author.voice.channel
        assert ctx.guild is not None

        player = self.get_player(ctx.guild)

        # Make sure it's not a stage channel
        if not isinstance(channel, discord.VoiceChannel):
            return await ctx.respond(
                "I can only join a regular voice channel.", ephemeral=True
            )
        await player.connect(channel)
        await ctx.respond(f"Joined '{channel.name}'")

    @commands.slash_command(
        guilds=TEST_GUILDS, description="You no longer want Beatbob in your life </3"
    )
    @ensure_same_voice_channel
    async def leave(self, ctx: discord.ApplicationContext):
        """Leave the current voice channel

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        assert ctx.guild is not None
        player = self.get_player(ctx.guild)
        await ctx.respond("Goodbye o7")
        await player.disconnect()

    @commands.slash_command(guilds=TEST_GUILDS, description="Play a song from YouTube.")
    @ensure_same_voice_channel
    async def play(self, ctx: discord.ApplicationContext, query: str):
        """Play music.

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        assert ctx.guild is not None
        await ctx.defer()
        player = self.get_player(ctx.guild)
        track_info = await player.add_track(query)  # TODO Return info and Display it

        if "error" in track_info:
            await ctx.respond(track_info.get("error", ""), ephemeral=True)
        else:
            await ctx.respond(f"🎵 Added to queue: `{query}`")

    @commands.slash_command(guilds=TEST_GUILDS, description="Pause music.")
    @ensure_same_voice_channel
    async def pause(self, ctx: discord.ApplicationContext):
        """Pause music

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under
        """
        assert ctx.guild is not None

        player = self.get_player(ctx.guild)
        await player.pause()
        await ctx.respond("Paused.", ephemeral=True)

    @commands.slash_command(guilds=TEST_GUILDS, description="Resume paused music.")
    @ensure_same_voice_channel
    async def resume(self, ctx: discord.ApplicationContext):
        """Resume paused music.

        Music has to be paused before resuming

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        assert ctx.guild is not None

        player = self.get_player(ctx.guild)
        await player.resume()
        await ctx.respond("Resumed.", ephemeral=True)

    @commands.slash_command(
        guilds=TEST_GUILDS, description="Stop playback. Skips current song and pauses."
    )
    @ensure_same_voice_channel
    async def stop(self, ctx: discord.ApplicationContext):
        """Stop playback.

        Skips the current song and pauses the next.

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        assert ctx.guild is not None

        player = self.get_player(ctx.guild)
        await player.stop()
        await ctx.respond("Stopped.", ephemeral=True)

    @commands.slash_command(guilds=TEST_GUILDS, description="Skips the current song.")
    @ensure_same_voice_channel
    async def skip(self, ctx: discord.ApplicationContext):
        """Skips the current song.

        If paused, it will start playing the next song.

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        assert ctx.guild is not None

        player = self.get_player(ctx.guild)
        await player.skip()
        await ctx.respond("Skipped song.")

    @commands.slash_command(guilds=TEST_GUILDS, description="Change volume.")
    async def volume(self, ctx: discord.ApplicationContext, volume: int):
        """Sets volume for the bot (a percentage).

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
            volume (int): Percentage to set volume to.
        """
        assert ctx.guild is not None

        player = self.get_player(ctx.guild)
        await player.set_volume(volume)
        await ctx.respond(f"Volume set to {volume}%")

    @commands.slash_command(guilds=TEST_GUILDS, description="Display the current queue")
    async def queue(self, ctx: discord.ApplicationContext):
        """Display the current music queue.

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        assert ctx.guild is not None
        player = self.get_player(ctx.guild)

        if not player.current_song and player.queue.empty():
            return await ctx.respond("The queue is currently empty.", ephemeral=True)

        embed = Embed(title="Music queue")

        # Currently playing track
        if player.current_song:
            title = player.current_song.get("title", "Unknown title")
            player.current_song.get("url")
            duration = player.current_song.get("duration", "Unknown")
            embed.add_field(
                name="Now Playing", value=f"[{title}]) — {duration}", inline=False
            )

        if not player.queue.empty():
            upcoming = list(player.queue._queue)[:1]  # peek
            queue_text = ""
            for i, track in enumerate(upcoming, start=1):
                track_title = track.get("title", "Unknown title")
                # track_url = track.get("url")
                track_duration = track.get("duration", "Unknown")
                queue_text += f"{i}. [{track_title}] — {track_duration}\n"

            logger.info(queue_text)
            embed.add_field(
                name=f"Up Next ({len(upcoming)} tracks)", value=queue_text, inline=False
            )

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(PlayerHandler(bot))
