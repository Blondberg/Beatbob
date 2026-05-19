from discord.ext import commands
from discord import app_commands
import discord


class HelloWorld(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="helloworld", description="Make the bot say Hello World."
    )
    async def helloworld(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hello world!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelloWorld(bot))
