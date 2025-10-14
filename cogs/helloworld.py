import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("beatbob")


class HelloWorld(commands.Cog):
    """A simple test cog"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="helloworld",
        description="Returns a friendly hello!",
    )
    async def helloworld(self, ctx: discord.ApplicationContext):
        await ctx.respond("Hello!")


def setup(bot):
    bot.add_cog(HelloWorld(bot))
