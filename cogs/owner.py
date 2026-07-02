import logging
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("beatbob")


async def is_bot_owner(interaction: discord.Interaction) -> bool:
    bot = cast(commands.Bot, interaction.client)
    if await bot.is_owner(interaction.user):
        return True

    raise app_commands.CheckFailure("Only the bot owner can use this command.")


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.check(is_bot_owner)
    @app_commands.command(name="sync", description="Sync bot commands.")
    async def sync(
        self, interaction: discord.Interaction, guild_id: str | None = None
    ) -> None:
        await interaction.response.defer()

        try:
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                # self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
                await interaction.followup.send(
                    f"Synced {len(synced)} commands to guild {guild_id}", ephemeral=True
                )

            else:
                synced = await self.bot.tree.sync()

                await interaction.followup.send(
                    f"Synced {len(synced)} commands globally", ephemeral=True
                )

        except ValueError:
            await interaction.followup.send(
                f"`{guild_id}` is not a valid Discord guild id.", ephemeral=True
            )
        except Exception:
            logger.exception("Failed to sync commands.")
            await interaction.followup.send(
                "Failed to sync commands. Check the bot logs for details.",
                ephemeral=True,
            )

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            message = str(error)
        else:
            logger.error(
                "Unhandled owner command error.",
                exc_info=(type(error), error, error.__traceback__),
            )
            message = "Failed to run owner command. Check the bot logs for details."

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
