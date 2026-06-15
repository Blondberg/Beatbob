import asyncio
import wavelink
import logging

logger = logging.getLogger("beatbob")


class GuildPlayer:
    """Keeps track of single player's state in a guild."""

    def __init__(self, player: wavelink.Player):
        self.player = player
        self.current = None

        self.loop = False
        self.shuffle = False
        self.is_autoplay = False

        self.volume = 10

    async def set_volume(self, volume: int) -> None:
        self.volume = max(0, min(volume, 100))
        await self.player.set_volume(volume)

        logger.info(f"Volume set to {volume}% for {self.player.guild.name}")

    async def add_track(self, track: wavelink.Playable):
        await self.player.queue.put_wait(track)

    async def add_playlist(self, playlist: wavelink.Playlist) -> int:
        return await self.player.queue.put_wait(playlist)

    async def play_next(self):
        if self.player.queue.is_empty:
            self.current = None
            return

        self.current = self.player.queue.get()

        await self.player.play(self.current, volume=self.volume)

    async def skip(self) -> wavelink.Playable | None:
        return await self.player.skip(force=True)

    async def stop(self):
        self.player.queue.clear()
        self.current = None
        await self.player.skip()

    async def pause(self):
        await self.player.pause(True)

    async def resume(self):
        await self.player.pause(False)

    async def seek(self, position_s: int):
        await self.player.seek(position_s * 1000)

    async def is_playing(self) -> bool:
        return self.player.playing

    async def autoplay(self, value: wavelink.AutoPlayMode) -> None:
        self.player.autoplay = value

    async def nightcore(self, value):
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(
            pitch=1.2 if value else 1, speed=1.2 if value else 1, rate=1
        )
        await self.player.set_filters(filters)

    async def pitch(self, value):
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(pitch=value)
        await self.player.set_filters(filters)

    async def speed(self, value):
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(speed=value)
        await self.player.set_filters(filters)

    async def rate(self, value):
        filters: wavelink.Filters = self.player.filters
        filters.timescale.set(rate=value)
        await self.player.set_filters(filters)

    async def cleanup(self):
        # Clear queue
        self.player.queue.clear()

        # Stop playback
        if self.player.playing:
            await self.player.stop()

        await self.player.disconnect()
