[![License](https://img.shields.io/github/license/blondberg/beatbob?style=for-the-badge&label=LICENSE)](LICENSE)
[![Issues](https://img.shields.io/github/issues/blondberg/beatbob?style=for-the-badge)](https://github.com/blondberg/beatbob/issues)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.7.1-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![Wavelink](https://img.shields.io/badge/Wavelink-3.5.2-5C2D91?style=for-the-badge)

<div align="center">
  <img src="beatboblogo.png" alt="Beatbob logo" width="90" height="90">
  <h1>Beatbob</h1>
  <p><i>A mediocre Discord music bot that works 95% of the time, every time. 🎧</i></p>
  <p>
    Listen to music from
    <br />
 <img src="https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white">
<img src="https://img.shields.io/badge/Spotify-1ED760?style=for-the-badge&logo=spotify&logoColor=white">
    <br />
    <strong>together! 🎶</strong>
  </p>
</div>

## About 🎵

Beatbob is a Discord music bot built with Python, discord.py, Wavelink, and Lavalink. It can play music from sources like YouTube and Spotify, manage queues, and keep the music going in your voice channel.

The project includes Docker support, so the bot and Lavalink can run together without too much setup.

### Built with 🛠️

![Discord.py](https://img.shields.io/badge/Discord.py-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)
![Lavalink](https://img.shields.io/badge/Lavalink-2C2F33?style=for-the-badge&logo=java&logoColor=white)

## Commands 

Most commands are slash commands and need to be used in a Discord server. Music controls also require you to be in the same voice channel as Beatbob.

| Command                   | What it does                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------ |
| `/play <query>`           | Searches for a song or playlist and adds it to the queue. Starts playback if nothing is playing. |
| `/skip`                   | Skips the current song.                                                                          |
| `/stop`                   | Stops playback, clears the queue, and disconnects the bot from voice.                            |
| `/pause`                  | Pauses the current song.                                                                         |
| `/resume`                 | Resumes paused playback.                                                                         |
| `/queue [page]`           | Shows the current queue.                                                                         |
| `/current`                | Shows the song currently playing and its progress.                                               |
| `/volume <0-100>`         | Sets the playback volume. Requires administrator permissions.                                    |
| `/autoplay <mode>`        | Turns autoplay on or off.                                                                        |
| `/loop <mode>`            | Sets loop mode to off, current track, or full queue.                                             |
| `/shuffle`                | Shuffles the current queue. This cannot be reversed.                                             |
| `/nightcore <true/false>` | Turns the nightcore-style filter on or off.                                                      |
| `/pitch <0.1-5.0>`        | Changes the pitch of the audio.                                                                  |
| `/speed <0.1-5.0>`        | Changes the playback speed.                                                                      |
| `/rate <0.1-5.0>`         | Changes the playback rate.                                                                       |
| `/helloworld`             | Makes the bot say hello. Mostly useful as a simple test command.                                 |
| `/sync [guild_id]`        | Syncs slash commands globally or to a specific server. Bot owner only.                           |

## Getting started

### Prerequisites ✅

- Docker and Docker Compose, for the easiest setup
- A Discord bot token
- Spotify client credentials, if you want Spotify support

### Setup ⚙️

```bash
git clone https://github.com/blondberg/beatbob.git
cd beatbob
cp application.example.yml application.yml
cp .env.example .env
```

Fill in environment variables inside `.env`:

```env
DISCORD_TOKEN=your_discord_bot_token
COMMAND_PREFIX=!
LAVALINK_PASSWORD=youshallnotpass
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

### Run with Docker (recommended!)

```bash
docker compose up -d --build
```

### Run without Docker

1. Create and activate virtual environment (optional)
    ```bash
      python -m venv venv

      source venv/scripts/activate (Windows)
      source venv/bin/activate (Linux/MacOS)
    ```

2. Install the Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Start Lavalink separately, then run the bot:
   
   First download the lastest [Lavalink](https://github.com/lavalink-devs/Lavalink/releases).

    ```bash
    java -jar Lavalink.jar
    python bot.py
    ```

**Important!** When running without Docker, make sure `LAVALINK_URI` is set in `.env`, for example:

```env
LAVALINK_URI=http://localhost:2333
```


## Roadmap
#### Commands
- [x] `/shuffle` and `/loop` commands.
- [ ] Queue history and ability to play `/previous` tracks.
- [ ] `/remove` a song from queue.
- [ ] `/seek` through a song.
- [ ] `/move` a song in the queue.


#### Misc
- [ ] DJ-mode: playing a song from each user before repeating. 
- [x] Docker support.
- [ ] Persistent guild settings (database support).
  - [ ] Queue.
  - [ ] Autoplay, loop, and shuffle.
