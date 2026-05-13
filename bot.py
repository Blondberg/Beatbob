import logging
import datetime
import os
import traceback
from dotenv import load_dotenv
import platform
import discord
from discord.ext import commands
from discord.ext.commands import (
    ExtensionAlreadyLoaded,
    ExtensionNotFound,
    ExtensionFailed,
    NoEntryPointError,
)

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")

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
    filename=f"logs/beatbob_{datetime.datetime.now().strftime("%Y-%m-%d%T%H-%M-%S")}.log",
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


# Configure intents
intents = discord.Intents.default()
intents.message_content = True
intents.typing = True

bot = commands.Bot(description="A mediocre music bot", intents=intents)

# Load extensions / cogs.
for filename in os.listdir(os.path.join(os.path.dirname(__file__), "cogs")):
    if not filename.endswith(".py") or filename.startswith("__"):
        continue

    extension_name = filename[:-3]

    try:
        bot.load_extension(f"cogs.{extension_name}")
        logger.info(f"Loaded extension '{extension_name}'")
    except (
        ExtensionFailed,
        ExtensionAlreadyLoaded,
        ExtensionNotFound,
        NoEntryPointError,
    ) as e:
        exception = f"{type(e).__name__}: {e}"
        logger.error(f"Failed to load extension '{extension_name}'\n{exception}")


@bot.listen(once=True)
async def on_ready() -> None:
    assert bot.user is not None
    logger.info(f"Logged in as: {bot.user.name}")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"System OS: {platform.system()} {platform.release}")
    logger.info("Bot is ready!")


@bot.event
async def on_disconnect() -> None:
    logger.warning("Disconnected from, or failed to connect to, Discord.")


@bot.event
async def on_connect() -> None:
    logger.info("Connected to Discord.")


@bot.event
async def on_application_command(ctx: commands.Context) -> None:
    """Log when an application command has been completed (not when received).

    Args:
        ctx (commands.Context): Context in which the command was invoked under.
    """
    logger.info(
        f"Command '{ctx.command}' invoked in guild '{ctx.guild.name}' (ID: {ctx.guild.id}) by '{ctx.author.name}' (ID: {ctx.author.id})"
    )


@bot.event
async def on_application_command_error(
    ctx: commands.Context, error: discord.DiscordException
) -> None:
    """Log when an application command has an error.

    Args:
        ctx (commands.Context): Context in which the command was invoked under
        error (discord.DiscordException): Exception associated to the error.
    """
    tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))

    logger.warning(
        f"Command '{ctx.command}' invoked in guild '{ctx.guild}' (ID: {ctx.guild.id}) "
        f"by '{ctx.author}' (ID: {ctx.author.id}) got an error:\n{tb}"
    )


bot.run(DISCORD_TOKEN)
