import discord
import datetime


def error_embed(title: str, text: str) -> discord.Embed:
    embed: discord.Embed = discord.Embed(
        title=f"Error: {title}",
        description=f"{text}",
        color=discord.Colour.red(),
    )

    return embed


def success_embed(title: str, text: str) -> discord.Embed:
    embed: discord.Embed = discord.Embed(
        title=f"{title}",
        description=f"{text}",
        color=discord.Colour.green(),
    )

    return embed
