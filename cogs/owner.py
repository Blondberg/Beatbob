from discord.ext import commands
from discord import app_commands
import discord
from discord.ext.commands import has_permissions


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @has_permissions(administrator=True)
    @app_commands.command(name="sync", description="Sync bot commands.")
    async def sync(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        synced = await self.bot.tree.sync()

        await interaction.response.send_message(
            f"Synced {len(synced)} commands globally"
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
