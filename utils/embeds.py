import datetime

import discord


def error_embed(title: str, text: str) -> discord.Embed:
    """Embed to display an error message"""
    embed: discord.Embed = discord.Embed(
        title=f"Error: {title}",
        description=f"{text}",
        color=discord.Colour.red(),
    )

    return embed


def success_embed(title: str, text: str) -> discord.Embed:
    """Embed to display a success message"""
    embed: discord.Embed = discord.Embed(
        title=f"{title}",
        description=f"{text}",
        color=discord.Colour.green(),
    )

    return embed
