import asyncio
import logging

import requests
import yt_dlp
from spotipy.exceptions import SpotifyException

from .spotify_api import extract_spotify_data

logger = logging.getLogger("beatbob")

YTDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}


def detect_source(query: str) -> str:
    """Detects source yupe based on the query string

    Args:
        query (str): The query being made

    Returns:
        str: The name of the source
    """
    if "spotify.com" in query:
        return "spotify"
    if "youtube.com" in query or "youtu.be" in query:
        return "youtube"
    return "search"


def spotify_to_youtube_query(spotify_url: str):
    """Extracts Spotify metadata and builds a YouTube search query.

    Args:
        spotify_url (str): Spotify url
    """
    spotify_data = extract_spotify_data(spotify_url)
    title = spotify_data.get("title")
    artists = " ".join(spotify_data.get("artists", []))
    query = f"{title} {artists} official audio"

    return query, spotify_data


def _extract_info_sync(query: str) -> dict:
    """Blocking yt-dlp extraction.

    Can currently handle Spotify, YouTube or plain text.
    """

    source = detect_source(query=query)

    if source == "spotify":
        try:
            query, spotify_data = spotify_to_youtube_query(spotify_url=query)
        except SpotifyException as e:
            logger.error(f"Failed to extract match Spotify data to YouTube query: {e}")
            return {"error": "Invalid Spotify url. Double-check your query."}
    elif source == "search":
        query = f"{query}"

    with yt_dlp.YoutubeDL(YTDL_OPTS) as ytdl:

        try:
            info = ytdl.extract_info(query, download=False)

            if "entries" in info:
                info = info["entries"][0]

            return {
                "title": info.get("title", "Unknown title"),
                "url": info.get("url"),
                "webpage_url": info.get("webpage_url"),
                "source": source,
            }
        except Exception as e:
            logger.error(f"Exception when extracting info with ytdlp {e}")

    return {
        "error": "Something went wrong when fetching song. Please double-check your query."
    }


async def extract_youtube_track(query: str) -> dict:
    """Async wrapper to run yt-dlp extraction in a separate thread."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _extract_info_sync, query)
