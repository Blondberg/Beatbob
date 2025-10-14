from datetime import datetime

import discord
from discord.ext import commands

from .timeconverter import s_to_hhmmss


class NowPlayingView(discord.ui.View):
    def __init__(self, ctx: discord.ApplicationContext, player, track):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.player = player
        self.track = track
        self.is_paused = False
        self.message = None

    async def create_message(self, track=None):
        self.track = track if track else self.track
        embed = await self.build_embed()

        if self.message:
            try:
                await self.message.delete()
            except discord.NotFound:
                pass

        if isinstance(self.ctx.channel, discord.TextChannel):
            self.message = await self.ctx.channel.send(embed=embed, view=self)

    async def update_message(self):
        """Updates the view message with new content.

        Creates a new message if one does not exist.
        """
        if not self.message:
            await self.create_message()
        else:
            embed = await self.build_embed()
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.NotFound:
                self.message = None
                await self.create_message()

    async def build_embed(self) -> discord.Embed:
        """Builds Now Playing embed

        Returns:
            discord.Embed: Discord embed
        """
        self.track = self.player.current_song

        if not self.track:
            embed = discord.Embed(
                title=f"Nothing is currently playing", timestamp=datetime.now()
            )
            embed.set_footer(text="Last updated")
            embed.description = f"Use `/play` to request a song."
            embed.add_field(
                name="Volume", value=f"{int(self.player.volume*100)}%", inline=True
            )
            return embed

        title = self.track.get("title", "Unknown title")
        url = self.track.get("webpage_url", "")
        duration = self.track.get("duration", 0)
        requested_by = self.track.get("requested_by", "")
        thumbnail_url = self.track.get("thumbnail_url", "")

        color = (
            discord.Color.green()
            if self.player.voice_client and self.player.voice_client.is_playing()
            else discord.Color.gold()
        )

        embed = discord.Embed(
            title=f"{title}",
            url=f"{url}" if url else "",
            timestamp=datetime.now(),
            color=color,
        )

        if thumbnail_url:
            embed.set_image(url=thumbnail_url)

        state = "paused" if not self.player.voice_client.is_playing() else "playing"
        embed.set_author(name=f"Now Playing ({state})")

        embed.set_footer(text="Last updated")

        if requested_by:
            embed.description = f"Requested by <@{requested_by}>"

        duration_text = s_to_hhmmss(duration)

        embed.add_field(name="Duration", value=f"{duration_text}", inline=True)
        embed.add_field(
            name="Volume", value=f"{int(self.player.volume*100)}%", inline=True
        )
        return embed

    @discord.ui.button(label="⏯️ Pause/Resume", style=discord.ButtonStyle.blurple, row=0)
    async def pause_resume_button(self, button, interaction: discord.Interaction):
        if not self.player.voice_client:
            return
        if self.player.voice_client.is_playing():
            await self.player.pause()
        else:
            await self.player.resume()

        await self.update_message()

        await interaction.response.defer()

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.blurple, row=0)
    async def skip_button(self, button, interaction: discord.Interaction):
        await self.player.skip()
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.blurple, row=0)
    async def stop_button(self, button, interaction: discord.Interaction):
        await self.player.stop()
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(
        label="🔉 Volume down", style=discord.ButtonStyle.secondary, row=1
    )
    async def volume_down_button(self, button, interaction: discord.Interaction):
        await self.player.set_volume(max(int(self.player.volume * 100) - 10, 0))
        await self.update_message()
        await interaction.response.defer()

    @discord.ui.button(label="🔊 Volume up", style=discord.ButtonStyle.secondary, row=1)
    async def volume_up_button(self, button, interaction: discord.Interaction):
        await self.player.set_volume(min(int(self.player.volume * 100) + 10, 100))
        await self.update_message()
        await interaction.response.defer()
