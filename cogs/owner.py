from discord.ext import commands
from discord import app_commands
import discord
from discord.ext.commands import has_permissions
from discord.ext.commands import is_owner


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @is_owner()
    @app_commands.command(name="sync", description="Sync bot commands.")
    async def sync(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        synced = await self.bot.tree.sync()

        await interaction.followup.send(
            f"Synced {len(synced)} commands globally", ephemeral=True
        )

        # Sync commands
        # try:
        #     guild = discord.Object(id=GUILD_ID)

        #     self.tree.copy_global_to(guild=guild)
        #     synced = await self.tree.sync(guild=guild)

        #     print(f"Synced {len(synced)} commands")
        # except Exception as e:
        #     self.logger.exception("Failed to sync commands.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
