import discord
from wavelink import Playable


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

    def __init__(self, now_playing: Playable, progress: dict, *, timeout=None):
        super().__init__(timeout=timeout)

        self.now_playing: Playable = now_playing

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
                    f"**Requested by: **{self.now_playing.extras.requested_by}\n"
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
            accent_color=discord.Color.blurple(),
        )

        self.add_item(container)
