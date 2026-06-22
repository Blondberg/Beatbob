import logging
from discord.ext import commands
from players.guild_player import GuildPlayer
from discord import app_commands
from utils.embeds import error_embed, success_embed
from discord.app_commands.checks import has_permissions
import discord
import wavelink
from typing import cast
from dotenv import load_dotenv
import os
import functools
from enum import Enum
from utils.playingview import NowPlayingView
import typing
from bot import BeatBob

load_dotenv()

GUILD_ID = os.getenv("GUILD_ID")


class AutoPlayMode(str, Enum):
    off = "off"
    related = "related"
    queue = "queue"


# def ensure_same_voice_channel(func):
#     """Decorator to make sure the user is in the same voice channel as the bot"""

#     @functools.wraps(func)
#     async def wrapped(*args, **kwargs):
#         interaction: discord.Interaction = kwargs.get("interaction")

#         if interaction is None:
#             interaction = args[1]

#         # Check if user is connected to a voice channel
#         if not interaction.user.voice:
#             return await interaction.followup.send(
#                 embed=error_embed(
#                     title="Join a channel",
#                     text="Please join a voice channel first.",
#                 ),
#                 ephemeral=True,
#             )

#         # Check if bot is connected
#         voice_client = interaction.guild.voice_client

#         if not voice_client:
#             return await interaction.followup.send(
#                 embed=error_embed(
#                     title="Not connected",
#                     text="I am not connected to a voice channel",
#                 ),
#                 ephemeral=True,
#             )

#         # Check if author and bot are in same voice channel
#         if interaction.user.voice.channel != voice_client.channel:
#             return await interaction.followup.send(
#                 embed=error_embed(
#                     title="Different channels",
#                     text="You must be in the same voice channel as the bot to use that command.",
#                 ),
#                 ephemeral=True,
#             )

#         return await func(*args, **kwargs)

#     return wrapped


class Music(commands.Cog):
    def __init__(self, bot: BeatBob) -> None:
        self.bot = bot

        self.players: dict[int, GuildPlayer] = {}

    async def ensure_voice(
        self, interaction: discord.Interaction
    ) -> wavelink.Player | None:
        if isinstance(interaction.user, discord.User):
            return None

        voice = interaction.user.voice

        if voice is None:
            return None

        if interaction.guild is None:
            return None

        if interaction.guild.voice_client:
            return typing.cast(wavelink.Player, interaction.guild.voice_client)

        return typing.cast(
            wavelink.Player, await voice.channel.connect(cls=wavelink.Player)
        )

    def get_guild_player(self, guild_id: int | None) -> GuildPlayer | None:
        if guild_id is None:
            return None

        return self.players.get(guild_id)

    def remove_guild_player(self, guild_id: int) -> bool:
        return self.players.pop(guild_id, None) is not None

    def create_guild_player(
        self, guild_id: int, player: wavelink.Player
    ) -> GuildPlayer:
        """Create a guild player for guild specified by id.

        Args:
            guild_id (int): Id of guild.
            player (wavelink.Player): Wavelink player connected to guild.

        Returns:
            GuildPlayer: The guild player that was created.
        """
        guild_player = GuildPlayer(player)

        player.inactive_timeout = 600

        self.players[guild_id] = guild_player

        return guild_player

    def get_or_create_guild_player(
        self, guild_id: int | None, player: wavelink.Player
    ) -> GuildPlayer:
        """Gets or creates a guild player if none exist for selected guild id.

        Args:
            guild_id (int | None): Id of guild.
            player (wavelink.Player): Wavelink player connected to guild.

        Raises:
            TypeError: If guild_id is None.

        Returns:
            GuildPlayer: Existing player for guild id, or new if none existed.
        """
        if guild_id is None:
            raise TypeError("Guild id cannot be None. Needs to be int.")

        guild_player = self.get_guild_player(guild_id)

        if guild_player:
            return guild_player

        return self.create_guild_player(
            guild_id,
            player,
        )

    def get_player(self, guild: discord.Guild) -> wavelink.Player | None:
        voice_client = guild.voice_client

        if voice_client is None:
            return None

        return cast(wavelink.Player, guild.voice_client)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self, payload: wavelink.NodeReadyEventPayload
    ) -> None:
        self.bot.logger.info(
            f"Wavelink Node connected: {payload.node} | Resumed: {payload.resumed}"
        )

    # -------------------------
    # TRACK END
    # -------------------------
    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, payload: wavelink.TrackEndEventPayload
    ) -> None:
        """Start next track on track end."""
        player: wavelink.Player = typing.cast(wavelink.Player, payload.player)

        if not player.guild:
            return

        guild_player = self.get_guild_player(player.guild.id)
        if not guild_player:
            return

        await guild_player.play_next()

    # -------------------------
    # TRACK EXCEPTION
    # -------------------------
    @commands.Cog.listener()
    async def on_wavelink_track_exception(
        self, payload: wavelink.TrackExceptionEventPayload
    ):
        self.bot.logger.exception(
            f"Track exception in guild "
            f"{payload.player.guild.id}: "
            f"{payload.exception}"
        )

    # -------------------------
    # TRACK STUCK
    # -------------------------
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload: wavelink.TrackStuckEventPayload):
        """Skip to next track if current is stuck."""
        self.bot.logger.warning(f"Track stuck in guild " f"{payload.player.guild.id}")

        await payload.player.skip(force=True)

    # -------------------------
    # TRACK START
    # -------------------------
    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self, payload: wavelink.TrackStartEventPayload
    ) -> None:
        """Ensure correct guild settings are set when a track start."""

        pass

    # -------------------------
    # PLAY
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="play", description="Play a song")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        await interaction.response.defer()

        player = await self.ensure_voice(interaction)
        if not player:
            return await interaction.followup.send(
                embed=error_embed("Not in voice", "Join a voice channel first."),
                ephemeral=True,
            )

        guild_player: GuildPlayer = self.get_or_create_guild_player(
            interaction.guild_id, player
        )

        tracks: wavelink.Search = await wavelink.Playable.search(query)

        if not tracks:
            return await interaction.followup.send(
                embed=error_embed(
                    title="Unable to find tracks",
                    text="Could not find any tracks with that query. Please try again.",
                ),
                ephemeral=True,
            )

        if isinstance(tracks, wavelink.Playlist):
            tracks.extras = {"requested_by": interaction.user.name}

            amount_added: int = await guild_player.add_playlist(tracks)
            await interaction.followup.send(
                embed=success_embed(
                    title="Added songs",
                    text=f"Added the playlist **`{tracks.name}`** ({amount_added} songs) to the queue.",
                )
            )
        else:
            track: wavelink.Playable = tracks[0]
            track.extras = {"requested_by": interaction.user.global_name}
            await guild_player.add_track(track)
            await interaction.followup.send(
                embed=success_embed(
                    title="Added song", text=f"Added **`{track}`** to the queue."
                )
            )

        if not await guild_player.is_playing():
            await guild_player.play_next()

    # -------------------------
    # SKIP
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="skip", description="Skip a song")
    async def skip(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer | None = self.get_guild_player(interaction.guild_id)
        if guild_player is None:
            return

        skipped_track = await guild_player.skip()
        if skipped_track:
            await interaction.followup.send(
                embed=success_embed(title="Skipped", text="Track skipped.")
            )

    # -------------------------
    # STOP
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="stop", description="Stop music and disconnect.")
    async def stop(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer | None = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.stop()
        if self.remove_guild_player(interaction.guild_id):
            await interaction.guild.voice_client.disconnect(force=False)

        await interaction.followup.send(
            embed=success_embed(title="Stopped", text="Playback stopped.")
        )

    # -------------------------
    # PAUSE / RESUME
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="pause", description="Pause playback.")
    async def pause(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.pause()

        await interaction.followup.send(
            embed=success_embed(title="Paused", text="Paused playback.")
        )

    @app_commands.guild_only()
    @app_commands.command(name="resume", description="Resume playback.")
    async def resume(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.resume()

        await interaction.followup.send(
            embed=success_embed(title="Resumed", text="Resumed playback.")
        )

    # -------------------------
    # VOLUME
    # -------------------------
    @app_commands.guild_only()
    @has_permissions(administrator=True)
    @app_commands.command(name="volume", description="Set playback volume.")
    async def volume(
        self, interaction: discord.Interaction, volume: app_commands.Range[int, 0, 100]
    ) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.set_volume(volume)

        await interaction.followup.send(
            embed=success_embed(
                title="Volume set", text=f"Volume set to {guild_player.volume}%."
            )
        )

    # -------------------------
    # AUTOPLAY
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="autoplay", description="Set autoplay.")
    async def autoplay(
        self, interaction: discord.Interaction, mode: wavelink.AutoPlayMode
    ) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.autoplay(mode)

        await interaction.followup.send(
            embed=success_embed(title="Autoplay", text=f"Autoplay set to {mode.name}.")
        )

    # -------------------------
    # NIGHTCORE
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="nightcore", description="Turn into nightcore")
    async def nightcore(self, interaction: discord.Interaction, value: bool) -> None:
        """Set the filter to a nightcore style."""
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.nightcore(value)

        await interaction.followup.send(
            embed=success_embed(title="NIGHTCORE", text=f"Nightcored is {value}")
        )

    # -------------------------
    # PITCH
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="pitch", description="Change pitch.")
    async def pitch(self, interaction: discord.Interaction, value: float) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.pitch(value)

        await interaction.followup.send(
            embed=success_embed(title="Pitch", text=f"Pitch changed to {value}.")
        )

    # -------------------------
    # SPEED
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="speed", description="Change speed.")
    async def speed(self, interaction: discord.Interaction, value: float) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.speed(value)

        await interaction.followup.send(
            embed=success_embed(title="Speed", text=f"Speed changed to {value}.")
        )

    # -------------------------
    # RATE
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="rate", description="Change rate.")
    async def rate(self, interaction: discord.Interaction, value: float) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        await guild_player.rate(value)

        await interaction.followup.send(
            embed=success_embed(title="Rate", text=f"Rate changed to {value}.")
        )

    # -------------------------
    # CURRENT
    # -------------------------
    @app_commands.guild_only()
    @app_commands.command(name="current", description="See the currently playing song.")
    async def current(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        guild_player: GuildPlayer | None = self.get_guild_player(interaction.guild_id)
        if not guild_player:
            return

        current_song = guild_player.current

        progress = await guild_player.get_progress()

        await interaction.followup.send(view=NowPlayingView(current_song, progress))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
