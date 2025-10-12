import os
from typing import Any

import requests
import spotipy
import yt_dlp
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
    )
)


def extract_spotify_data(spotify_url: str) -> dict:
    # Get a single track
    try:
        result = sp.track(spotify_url)
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError
    if result is None:
        return {}

    track: dict[str, Any] = {}

    track["title"] = result["name"]
    track["artists"] = [artist["name"] for artist in result["artists"]]
    track["primary_artist"] = track["artists"][0]
    track["album"] = result["album"]["name"]
    track["album_release"] = result["album"]["release_date"]
    track["duration_ms"] = result["duration_ms"]
    track["is_explicit"] = result["explicit"]

    return track
