from abc import ABC, abstractmethod

import discord


class BasePlayer(ABC):
    """Abstract base player for music players"""

    @abstractmethod
    async def connect(self, channel):
        """Connect player to voice channel.

        Args:
            channel (discord.VoiceChannel): Voice channel to connect to
        """

    @abstractmethod
    async def disconnect(self):
        """Disconnect player from voice channel."""

    @abstractmethod
    async def set_volume(self, volume: int):
        """Sets the bots volume"""

    @abstractmethod
    async def stop(self):
        """Stop playback.

        Skips the current song and pauses the next.
        """

    @abstractmethod
    async def pause(self):
        """Pause music"""

    @abstractmethod
    async def resume(self):
        """Resume paused music.

        Music has to be paused before resuming
        """
