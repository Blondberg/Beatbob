import datetime
import logging
import os
import platform

import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Fetch environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

GUILD_ID = os.getenv("GUILD_ID", "")

LAVALINK_URI = os.getenv("LAVALINK_URI", "")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")


def require_setting(name: str, value: str) -> str:
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


# Setup loggers
logger = logging.getLogger("beatbob")
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter(
    fmt="%(asctime)s :: %(levelname)-7s :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# File handler
os.makedirs(os.path.dirname("logs/"), exist_ok=True)
file_handler = logging.FileHandler(
    filename=f'logs/beatbob_{datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}.log',
    encoding="utf-8",
    mode="w",
)
file_handler.setFormatter(log_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class BeatBob(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        self.logger = logging.getLogger("beatbob")

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            description="A mediocre music bot",
        )

    async def setup_hook(self) -> None:
        # Load cogs
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), "cogs")):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            extension_name = filename[:-3]

            try:
                await self.load_extension(f"cogs.{extension_name}")
                self.logger.debug(f"Loaded extension '{extension_name}'")
            except Exception:
                self.logger.exception(f"Failed to load extension '{extension_name}'")

        # Connect Lavalink
        node = wavelink.Node(
            uri=require_setting("LAVALINK_URI", LAVALINK_URI),
            password=LAVALINK_PASSWORD,
        )
        try:
            await wavelink.Pool.connect(nodes=[node], client=self)
        except Exception:
            self.logger.exception("Failed to connect to Lavalink.")
            raise

    async def on_ready(self) -> None:
        assert self.user is not None
        self.logger.info(f"Logged in as: {self.user.name}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(f"System OS: {platform.system()} {platform.release()}")
        self.logger.info("Bot is ready!")

    async def on_disconnect(self) -> None:
        self.logger.warning("Disconnected from, or failed to connect to, Discord.")

    async def on_connect(self) -> None:
        self.logger.info("Connected to Discord.")


if __name__ == "__main__":
    bot = BeatBob()
    bot.run(require_setting("DISCORD_TOKEN", DISCORD_TOKEN))
