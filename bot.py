import datetime
import logging
import os
import platform

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Setup environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


# Setup loggers
logger = logging.getLogger("beatbob")
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter(
    fmt="%(asctime)s :: %(levelname)-7s :: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",  # <-- custom date format
)

# File handler
os.makedirs(os.path.dirname("logs/"), exist_ok=True)  # Make sure log folder exists

file_handler = logging.FileHandler(
    filename=f"logs/beatbob_{datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}.log",
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
intents.members = True  # NOTE Member events, needed?

bot = discord.Bot(intents=intents, description="A mediocre music bot")

# Load extensions/cogs
for filename in os.listdir(os.path.join(os.path.dirname(__file__), "cogs")):
    if not filename.endswith(".py") or filename.startswith("__"):
        continue
    extension_name = filename[:-3]

    try:
        bot.load_extension(f"cogs.{extension_name}")
        logger.info(f"Loaded extension '{extension_name}")
    except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        logger.error(f"Failed to load extension '{extension_name}'\n{exception}")


@bot.listen(once=True)
async def on_ready() -> None:
    """Executed when bot is ready.

    Logs information. Only triggered once during runtime.
    """
    assert bot.user is not None
    logger.info(f"Logged in as: {bot.user.name}")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"System OS: {platform.system()} {platform.release()}")
    logger.info("Bot is ready!")


@bot.event
async def on_disconnect() -> None:
    """Executed if bot gets disconnected from Discord."""
    logger.warning(f"Disconnected from Discord.")


@bot.event
async def on_connect() -> None:
    """Executed when bot gets connected to Discord."""
    logger.info("Connected to Discord.")


@bot.event
async def on_application_command_completion(ctx: commands.Context) -> None:
    """Runs when an application command has been completed.

    Does not run when it gets received.

    Args:
        ctx: Context in which the command was invoked under.
    """
    logger.info(
        f"Command '{ctx.command}' invoked in guild '{ctx.guild.name}' (ID: {ctx.guild.id}) by '{ctx.author}' (ID: {ctx.author.id})"
    )


@bot.event
async def on_application_command_error(
    ctx: commands.Context, error: discord.DiscordException
) -> None:
    """Runs when an application command has an error.

    Args:
        ctx: Context in which the command was invoked under.
        error: Exception associated to the error.
    """
    # if isinstance(exception, commands.MissingPermissions):
    #     pass

    exception = f"{type(error).__name__}: {error}"
    logger.warning(
        f"Command '{ctx.command}' invoked in guild '{ctx.guild.name}' (ID: {ctx.guild.id}) by '{ctx.author}' (ID: {ctx.author.id}) got an error: \n{exception}"
    )


bot.run(DISCORD_TOKEN)
