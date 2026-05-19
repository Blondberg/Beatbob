import logging
import datetime
import os
from discord import app_commands
from typing import Union
from dotenv import load_dotenv
import platform
import discord
import traceback
import wavelink
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")

GUILD_ID = os.getenv("GUILD_ID")

LAVALINK_URI = os.getenv("LAVALINK_URI")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

# Setup loggers
logger = logging.getLogger("beatbob")
logger.setLevel(logging.INFO)
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
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class BeatBob(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            description="A mediocre music bot",
        )

    async def setup_hook(self):
        # load cogs
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), "cogs")):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            extension_name = filename[:-3]

            try:
                await self.load_extension(f"cogs.{extension_name}")
                logger.info(f"Loaded extension '{extension_name}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                logger.error(
                    f"Failed to load extension '{extension_name}'\n{exception}"
                )

        # Connect Lavalink
        node = wavelink.Node(uri=LAVALINK_URI, password=LAVALINK_PASSWORD)
        await wavelink.Pool.connect(nodes=[node], client=self)

        # Sync commands
        try:
            guild = discord.Object(id=GUILD_ID)

            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)

            print(f"Synced {len(synced)} commands")
        except Exception as e:
            logger.exception("Failed to sync commands.")

    async def on_ready(self):
        assert self.user is not None
        logger.info(f"Logged in as: {self.user.name}")
        logger.info(f"Python version: {platform.python_version()}")
        logger.info(f"System OS: {platform.system()} {platform.release()}")
        logger.info("Bot is ready!")

    async def on_disconnect(self) -> None:
        logger.warning("Disconnected from, or failed to connect to, Discord.")

    async def on_connect(self) -> None:
        logger.info("Connected to Discord.")


bot = BeatBob()
bot.run(DISCORD_TOKEN)
