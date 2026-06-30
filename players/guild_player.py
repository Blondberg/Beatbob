import wavelink
from enum import Enum
import asyncio


class LoopMode(Enum):
    OFF = 0
    TRACK = 1
    QUEUE = 2


class GuildPlayer:
    """Keeps track of single player's state in a guild."""

    def __init__(self, player: wavelink.Player):
        self.player = player

        self.loop_mode = LoopMode.OFF
        self._lock = asyncio.Lock()

        self.volume = 10

    @property
    def current(self) -> wavelink.Playable | None:
        return self.player.current

    async def set_volume(self, volume: int) -> None:
        self.volume = max(0, min(volume, 100))
        await self.player.set_volume(volume)

    async def add_track(self, track: wavelink.Playable) -> None:
        """Adds a single track to the queue.

        Args:
            track (wavelink.Playable):
        """
        await self.player.queue.put_wait(track)

        # Start playing music if nothing's playing
        if not self.player.playing:
            await self.advance()

    async def add_playlist(self, playlist: wavelink.Playlist) -> int:
        """Adds a playlist to the queue, i.e. multiple tracks."""
        amount_added = await self.player.queue.put_wait(playlist)

        # Start playing music if nothing's playing
        if not self.player.playing:
            await self.advance()

        return amount_added

    async def get_progress(self) -> dict[str, int]:
        if self.player.current:
            return {
                "position": self.player.position,
                "length": self.player.current.length or 0,
            }

        return {
            "position": 0,
            "length": 0,
        }

    async def play_next(self) -> None:
        if self.player.queue.is_empty:
            return

        next_song = self.player.queue.get()

        await self.player.play(next_song, volume=self.volume)

    async def advance(self) -> None:
        async with self._lock:
            current = self.player.current

            # Loop current track
            if self.loop_mode == LoopMode.TRACK and current is not None:
                await self.player.play(current, volume=self.volume)
                return

            # Queue loop. TODO Append previous songs aswell
            if self.loop_mode == LoopMode.QUEUE and current is not None:
                await self.player.queue.put_wait(current)

            # Normal queue
            if not self.player.queue.is_empty:
                track = self.player.queue.get()

                await self.player.play(track, volume=self.volume)
                return

            # Do nothing if autoplay is enabled. LavaLink will automatically request a recommendation
            if self.player.autoplay != wavelink.AutoPlayMode.disabled:
                return

            # Stop playback completely
            await self.player.stop()

    async def skip(self) -> wavelink.Playable | None:
        return await self.player.skip(force=True)

    async def stop(self) -> None:
        self.player.queue.clear()
        await self.player.skip()

    async def pause(self) -> None:
        await self.player.pause(True)

    async def resume(self) -> None:
        await self.player.pause(False)

    async def seek(self, position_s: int) -> None:
        await self.player.seek(position_s * 1000)

    def is_playing(self) -> bool:
        return self.player.playing

    async def autoplay(self, mode: wavelink.AutoPlayMode) -> None:
        self.player.autoplay = mode

    async def nightcore(self, value: float) -> None:
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(
            pitch=1.2 if value else 1, speed=1.2 if value else 1, rate=1
        )
        await self.player.set_filters(filters)

    async def pitch(self, value: float) -> None:
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(pitch=value)
        await self.player.set_filters(filters)

    async def speed(self, value: float) -> None:
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(speed=value)
        await self.player.set_filters(filters)

    async def rate(self, value: float) -> None:
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(rate=value)
        await self.player.set_filters(filters)

    def get_queue(self) -> wavelink.Queue:
        return self.player.queue

    def get_queue_size(self) -> int:
        return self.player.queue.count

    async def cleanup(self) -> None:
        # Clear queue
        self.player.queue.clear()

        # Stop playback
        if self.player.playing:
            await self.player.stop()

        await self.player.disconnect()
