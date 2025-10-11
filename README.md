# Beatbob - A mediocre Discord Music Bot

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![Pycord](https://img.shields.io/badge/Pycord[voice]-2.6.1-5865F2)](https://docs.pycord.dev)
[![License](https://img.shields.io/github/license/blondberg/beatbob)](LICENSE)
[![Issues](https://img.shields.io/github/issues/blondberg/beatbob)](https://github.com/blondberg/beatbob/issues)
[![Last Commit](https://img.shields.io/github/last-commit/blondberg/beatbob)]()


# Commands
### `/join`
Joins the channel you're currently in.

**Behaviour:**
* Joins the voice channel the user is currently in (if possible).
* Requires user to be in an accessible voice channel.

---
### `/leave`
Disconnect the bot from the current voice channel.

**Behaviour:**
* Stops playback and disconnects from the channel
* Requires user to be in the same voice channel.

---
### `/play <url or search term>`
Play a song from YouTube.

**Arguments**
* \<url or search term>: Optional. Song to be played/queued.

**Behaviour:**
* Queues a song and/or begins playback if paused/stopped.
* If already playing, the song is added to a queue.
* Requires the user to be in the same voice channel.

---
### `/pause`
Pauses currently played song.

**Behaviour:**
* Pauses the current song without clearing the queue.
* Requires the user to be in the same voice channel.

---
### `/resume`
Resumes paused playback.

**Behaviour:**
* Resumes paused songs (works like `/play` without argument). Does nothing if nothing is paused.
* Requires the user to be in the same voice channel.


---
### `/stop`
Stop playback and clear current queue.

**Behaviour**
* Stops the current track.
* Clears the song queue.
* Requires the user to be in the same voice channel.

---
### `/skip`
Skips the current song.

**Behaviour:**
* Skips current song and moves to next in queue (if any).
* If paused, playback resumes.
* Requires the user to be in the same voice channel.

---
### `/queue`
Displays the current queue.

**Behaviour:**
* Displays a list of upcoming songs.
* May only show the first few entries if the queue is long.
* Requires the user to be in the same voice channel.