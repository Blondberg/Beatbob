import wavelink


class GuildPlayer:
    """Keeps track of single player's state in a guild."""

    def __init__(self, player: wavelink.Player):
        self.player = player
        self.current: wavelink.Playable | None = None

        self.loop = False
        self.shuffle = False
        self.is_autoplay = False

        self.volume = 10

    async def set_volume(self, volume: int) -> None:
        self.volume = max(0, min(volume, 100))
        await self.player.set_volume(volume)

    async def add_track(self, track: wavelink.Playable) -> int:
        """Adds a single track to the queue.

        Args:
            track (wavelink.Playable):

        Returns:
            int: Number of tracks added.
        """
        return await self.player.queue.put_wait(track)

    async def add_playlist(self, playlist: wavelink.Playlist) -> int:
        """Adds a playlist to the queue, i.e. multiple tracks.

        Args:
            playlist (wavelink.Playlist):

        Returns:
            int: Number of tracks added.
        """
        return await self.player.queue.put_wait(playlist)

    async def get_progress(self) -> dict[str, int] | None:
        if self.player.current:
            return {
                "position": self.player.position,
                "length": self.player.current.length or 0,
            }

        return None

    async def play_next(self) -> None:
        self.current = await self.player.play(
            self.player.queue.get(), volume=self.volume
        )

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

    async def rate(self, value: float):
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
