import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands

from musicplayer.songextraction import extract_youtube_track

from .baseplayer import BasePlayer

logger = logging.getLogger("beatbob")

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class YTDLPlayer(BasePlayer):
    def __init__(self, bot: commands.Bot, guild: discord.Guild) -> None:
        self.bot = bot
        self.guild = guild
        self.voice_client: Optional[discord.VoiceClient] = None
        self.volume: float = 1.0  # 1.0 = 100%
        self.next_event = asyncio.Event()  # Flag to tell when next song can be played
        self.player_loop_task = None
        self.current_song = None
        self.queue = asyncio.Queue()

    async def player_loop(self) -> None:
        """Main playback loop."""

        await self.bot.wait_until_ready()
        logger.debug(f"Player loop started for {self.guild.name}")

        while not self.bot.is_closed():
            self.next_event.clear()

            # Get next song (wait if queue is empty)
            self.current_song = await self.queue.get()

            ffmpeg_source = discord.FFmpegPCMAudio(
                self.current_song.get("url"), **FFMPEG_OPTIONS
            )  # NOTE this is not awaitable

            self.source = discord.PCMVolumeTransformer(
                ffmpeg_source, volume=self.volume
            )

            assert self.voice_client is not None

            self.voice_client.play(
                self.source,
                after=lambda e: self.bot.loop.call_soon_threadsafe(self.next_event.set),
            )

            await self.next_event.wait()  # wait until track finishes

    async def add_track(self, query: str) -> dict:
        """Add track to the queue

        Args:
            query (str): Queried track
        """
        track_info = await extract_youtube_track(query)

        if not "error" in track_info:
            await self.queue.put(track_info)
            logger.info(f"Queued track: {track_info.get('title')}")

        return track_info

    async def connect(self, channel):
        """Connect voice client to a channel.

        Args:
            channel (discord.VoiceChannel): Voice channel to connect to.
        """
        # Make sure the bot is fully ready
        await self.bot.wait_until_ready()

        # Move to channel of user if already connected
        if self.voice_client and self.voice_client.is_connected():
            return await self.voice_client.move_to(channel)

        # Disconnect if connected
        if self.voice_client:
            await self.disconnect()

        # Connect
        self.voice_client = await channel.connect(reconnect=True)
        logger.info(f"Connected to voice channel {channel.name}")

        # Start the playback loop if not running
        if self.player_loop_task is None or self.player_loop_task.done():
            self.player_loop_task = self.bot.loop.create_task(self.player_loop())

    async def disconnect(self) -> None:
        """Disconnect voice client if in a channel."""
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect(force=True)
            self.voice_client.cleanup()
            self.voice_client = None
            logger.info(f"Disconnected from voice in {self.guild.name}")

    async def skip(self):
        """Skip current track"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()

    async def set_volume(self, volume: int):
        """Set playback volume (0--200%).

        Args:
            volume (int): Volume percentage (0--100%)
        """
        self.volume = max(0.0, min(volume / 100.0, 1.0))
        if self.source:
            self.source.volume = self.volume
        logger.info(f"Volume set to {volume}% for {self.guild.name}")

    async def stop(self):
        """Stop playback and clear the queue."""
        while not self.queue.empty():
            self.queue.get_nowait()
        await self.skip()

    async def resume(self):
        """Resume song if paused.

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under
        """
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()

    async def pause(self):
        """Pause music if playing.

        Args:
            ctx (discord.ApplicationContext): Context in which the command was invoked under.
        """
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
