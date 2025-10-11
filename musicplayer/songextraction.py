import asyncio

import yt_dlp

YTDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}


def _extract_info_sync(query: str) -> dict:
    """Blocking yt-dlp extraction (synchronous)."""
    with yt_dlp.YoutubeDL(YTDL_OPTS) as ytdl:
        info = ytdl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]

        return {"title": info.get("title", "Unknown title"), "url": info.get("url")}


async def extract_youtube_track(query: str) -> dict:
    """Async wrapper to run yt-dlp extraction in a separate thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _extract_info_sync, query)
