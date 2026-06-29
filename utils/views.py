import discord
import wavelink
import math


def format_duration(ms: int) -> str:
    """Formats miliseconds into hh:mm:ss. Only shows hours if above 0.

    Args:
        ms (int): Duration in miliseconds.

    Returns:
        str: Miliseconds formatted. E.g. 01:00:00, 01:00, 00:00.
    """
    total_seconds = ms // 1000

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    return f"{minutes:02}:{seconds:02}"


def progress_bar(position_ms: int, duration_ms: int, length: int = 30) -> str:
    """Generates a progress bar based on current progress and total duration in miliseconds.

    Args:
        position_ms (int): Current progress.
        duration_ms (int): Total duration.
        length (int, optional): Amount of characters in progress bar. Defaults to 30.

    Returns:
        str: A progress bar made of characters/emojis.
    """
    if duration_ms <= 0:
        return "▱" * length

    progress = min(position_ms / duration_ms, 1.0)

    filled = int(progress * length)

    return "▰" * filled + "▱" * (length - filled)


class NowPlayingView(discord.ui.LayoutView):

    def __init__(
        self,
        now_playing: wavelink.Playable,
        progress: dict[str, int],
        *,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)

        self.now_playing: wavelink.Playable = now_playing

        self.progress = progress

        self.progress_bar = progress_bar(
            self.progress["position"], self.progress["length"]
        )

        container: discord.ui.Container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"## Current song\n"
                    f"**[{self.now_playing.title}]({self.now_playing.uri})**\n"
                    f"{self.now_playing.author}\n"
                ),
                accessory=discord.ui.Thumbnail(
                    self.now_playing.artwork
                    or f"https://img.youtube.com/vi/{self.now_playing.identifier}/hqdefault.jpg"
                ),
            ),
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                content=f"{format_duration(self.progress.get('position') or 0)}  {self.progress_bar}  {format_duration(self.progress.get('length') or 0)}"
            ),
            discord.ui.TextDisplay(
                content=f"**Requested by: **{self.now_playing.extras.requested_by}\n"
            ),
            accent_color=discord.Color.blurple(),
        )

        self.add_item(container)


class QueuedView(discord.ui.LayoutView):
    def __init__(
        self,
        queue: wavelink.Queue,
        page_number: int = 0,
        page_size: int = 5,
        *,
        timeout: float | None = None,
    ):
        self.page_size = page_size

        super().__init__(timeout=timeout)

        # Add all queued tracks within page to list
        self.tracks: list[wavelink.Playable] = [
            queue.peek(i) for i in range(queue.count)
        ]

        if not self.tracks:
            self.add_item(
                discord.ui.Container(
                    discord.ui.TextDisplay(
                        content=f"Queue is currently empty. Add more songs with `/play`!"
                    ),
                    accent_color=discord.Color.red(),
                )
            )
            return

        current_track = self.tracks[0]

        queued_tracks: list[wavelink.Playable] = []
        if len(self.tracks) > 1:
            queued_tracks = self.tracks[1:]

        total_pages = max(1, math.ceil(len(queued_tracks) / page_size))

        # Clamp page into valid range
        page_number = max(1, min(page_number, total_pages))
        self.page_number = page_number

        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size

        page_tracks = queued_tracks[start_index:end_index]

        # Format string to display queue
        queue_string = ""
        if len(self.tracks) > 1:
            queue_string = "\n".join(
                f"{start_index + index + 2}. [{song.title}]({song.uri}) [{format_duration(song.length)}] ({song.extras.requested_by})"
                for index, song in enumerate(page_tracks)
            )

        container: discord.ui.Container = discord.ui.Container(
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=f"## Coming up\n"
                    f"1. **[{current_track.title}]({current_track.uri})** [{format_duration(current_track.length)}]\n"
                    f"{self.tracks[0].author}\n"
                    f"**Requested by: **{current_track.extras.requested_by}"
                ),
                accessory=discord.ui.Thumbnail(
                    self.tracks[0].artwork
                    or f"https://img.youtube.com/vi/{current_track.identifier}/hqdefault.jpg"
                ),
            ),
            discord.ui.Separator(),
            discord.ui.TextDisplay(
                content=(
                    f"### Queue\n{queue_string}\n" f"Page {page_number}/{total_pages}"
                    if len(queue_string) > 1
                    else "No additional songs in queue."
                )
            ),
            accent_color=discord.Color.yellow(),
        )
        self.add_item(container)


class TrackSkippedView(discord.ui.LayoutView):
    def __init__(
        self,
        track_title: str = "",
        track_uri: str = "",
        by_user: str = "",
        *,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)

        container: discord.ui.Container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="## Track skipped\n"
                f"Track **[{track_title}]({track_uri})** skipped by **{by_user}**."
            ),
            accent_color=discord.Color.yellow(),
        )
        self.add_item(container)


class TrackAddedView(discord.ui.LayoutView):
    def __init__(
        self,
        track_title: str = "",
        track_uri: str = "",
        requested_by: str = "",
        *,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)

        container: discord.ui.Container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="## Track added\n"
                f"Track **[{track_title}]({track_uri})** added by **{requested_by}**."
            ),
            accent_color=discord.Color.green(),
        )
        self.add_item(container)


class PlaylistAddedView(discord.ui.LayoutView):
    def __init__(
        self,
        playlist_name: str = "",
        playlist_url: str = "",
        requested_by: str = "",
        amount_added: int = 0,
        *,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)

        container: discord.ui.Container = discord.ui.Container(
            discord.ui.TextDisplay(
                content="## Playlist added\n"
                f"Playlist **[{playlist_name}]({playlist_url})** ({amount_added} songs) added by **{requested_by}**."
            ),
            accent_color=discord.Color.green(),
        )
        self.add_item(container)
