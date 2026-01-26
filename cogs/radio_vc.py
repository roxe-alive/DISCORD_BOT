import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio

# === STREAM URLS ===
STREAMS = {
    "Server 1": "https://stream-160.zeno.fm/wyqezxthwlfvv",
    "Server 2": "https://stream-154.zeno.fm/45o41jvammjtv",
    "Server 3": "https://stream-159.zeno.fm/h7xtz3e9reruv",
    "Server 4": "https://stream-156.zeno.fm/g8cx7tggb3quv",
    "Server 5": "https://rbx2.hnux.com/http://5984.cloudrad.io:8032/;stream.mp3",
    "Server 6": "https://radiomalayalamfm.com/radio/8000/radio.mp3",
    "Server 7": "https://icecast.octosignals.com/radio90_final"
}

server_emoji = "🎧"


class RadioSelector(discord.ui.View):
    def __init__(self, ctx, cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.cog = cog
        self.current_station = None
        self.is_paused = False
        self.message = None
        self.reconnect_task = None

    async def update_button_states(self, active_label=None):
        """Highlight active server and control buttons properly."""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.label in STREAMS:
                    child.style = (
                        discord.ButtonStyle.blurple
                        if child.label == active_label
                        else discord.ButtonStyle.secondary
                    )
                elif child.label == "Play":
                    child.style = discord.ButtonStyle.blurple if self.is_paused else discord.ButtonStyle.secondary
                elif child.label == "Pause":
                    child.style = discord.ButtonStyle.secondary if self.is_paused else discord.ButtonStyle.blurple
        if self.message:
            await self.message.edit(view=self)

    async def ensure_vc(self):
        """Ensure bot is connected to a VC."""
        vc = self.cog.voice_clients.get(self.ctx.guild.id)
        if vc and vc.is_connected():
            return vc

        if self.ctx.author.voice:
            channel = self.ctx.author.voice.channel
        else:
            # Auto-create a VC if user not in one
            category_name = "This Is 4 You! 🪻 <3"
            category = discord.utils.get(self.ctx.guild.categories, name=category_name)
            if not category:
                category = await self.ctx.guild.create_category(category_name)

            channel = discord.utils.get(self.ctx.guild.voice_channels, name="My Radio ♡")
            if not channel:
                channel = await self.ctx.guild.create_voice_channel("My Radio ♡", category=category)
            await self.ctx.send(f"✅ Joined **{channel.name}** in **{category_name}**")

        try:
            vc = await channel.connect(reconnect=True)
            self.cog.voice_clients[self.ctx.guild.id] = vc
            return vc
        except Exception as e:
            await self.ctx.send(f"❌ Failed to connect VC: `{e}`")
            return None

    async def reconnect_stream(self, stream_url, label):
        """Continuously ensure stream stays alive."""
        while True:
            await asyncio.sleep(15)
            vc = self.cog.voice_clients.get(self.ctx.guild.id)
            if not vc or not vc.is_connected():
                continue
            if not vc.is_playing() and not self.is_paused:
                try:
                    source = FFmpegPCMAudio(stream_url, **self.cog.ffmpeg_options)
                    vc.play(source)
                    await self.ctx.send(f"🔁 Auto-reconnected to **{label}** stream.")
                except Exception as e:
                    await self.ctx.send(f"⚠️ Reconnect failed: `{e}`")

    async def play_station(self, stream_url: str, label: str):
        """Play or switch to selected radio server."""
        vc = await self.ensure_vc()
        if not vc:
            return

        # Stop current playback
        if vc.is_playing() or vc.is_paused():
            vc.stop()
            await asyncio.sleep(0.5)

        try:
            source = FFmpegPCMAudio(stream_url, **self.cog.ffmpeg_options)
            vc.play(source)
            self.current_station = label
            self.is_paused = False
            await self.ctx.send(f"🎶 Now streaming **{label}**!")
            await self.update_button_states(active_label=label)

            # Restart reconnect loop
            if self.reconnect_task and not self.reconnect_task.done():
                self.reconnect_task.cancel()
            self.reconnect_task = asyncio.create_task(self.reconnect_stream(stream_url, label))
        except Exception as e:
            await self.ctx.send(f"❌ Failed to play: `{e}`")

    # --- RADIO SERVER BUTTONS ---
    @discord.ui.button(label="Server 1", emoji=server_emoji, style=discord.ButtonStyle.secondary, row=0)
    async def s1(self, interaction, button):
        await interaction.response.defer()
        await self.play_station(STREAMS["Server 1"], "Server 1")

    @discord.ui.button(label="Server 2", emoji=server_emoji, style=discord.ButtonStyle.secondary, row=0)
    async def s2(self, interaction, button):
        await interaction.response.defer()
        await self.play_station(STREAMS["Server 2"], "Server 2")

    @discord.ui.button(label="Server 3", emoji=server_emoji, style=discord.ButtonStyle.secondary, row=0)
    async def s3(self, interaction, button):
        await interaction.response.defer()
        await self.play_station(STREAMS["Server 3"], "Server 3")

    @discord.ui.button(label="Server 4", emoji=server_emoji, style=discord.ButtonStyle.secondary, row=0)
    async def s4(self, interaction, button):
        await interaction.response.defer()
        await self.play_station(STREAMS["Server 4"], "Server 4")

    @discord.ui.button(label="Server 5", emoji=server_emoji, style=discord.ButtonStyle.secondary, row=1)
    async def s5(self, interaction, button):
        await interaction.response.defer()
        await self.play_station(STREAMS["Server 5"], "Server 5")

    @discord.ui.button(label="Server 6", emoji=server_emoji, style=discord.ButtonStyle.secondary, row=1)
    async def s6(self, interaction, button):
        await interaction.response.defer()
        await self.play_station(STREAMS["Server 6"], "Server 6")

    @discord.ui.button(label="Server 7", emoji=server_emoji, style=discord.ButtonStyle.secondary, row=1)
    async def s7(self, interaction, button):
        await interaction.response.defer()
        await self.play_station(STREAMS["Server 7"], "Server 7")

    # --- CONTROL BUTTONS ---
    @discord.ui.button(label="Play", emoji="▶️", style=discord.ButtonStyle.secondary, row=2)
    async def play_btn(self, interaction, button):
        await interaction.response.defer()
        vc = self.cog.voice_clients.get(self.ctx.guild.id)
        if vc and self.is_paused:
            vc.resume()
            self.is_paused = False
            await self.ctx.send("▶️ Stream resumed.")
            await self.update_button_states(self.current_station)

    @discord.ui.button(label="Pause", emoji="⏸️", style=discord.ButtonStyle.secondary, row=2)
    async def pause_btn(self, interaction, button):
        await interaction.response.defer()
        vc = self.cog.voice_clients.get(self.ctx.guild.id)
        if vc and vc.is_playing():
            vc.pause()
            self.is_paused = True
            await self.ctx.send("⏸️ Stream paused.")
            await self.update_button_states(self.current_station)

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.secondary, row=2)
    async def stop_btn(self, interaction, button):
        await interaction.response.defer()
        vc = self.cog.voice_clients.get(self.ctx.guild.id)
        if vc:
            if vc.is_playing() or vc.is_paused():
                vc.stop()
            await vc.disconnect(force=True)
            self.cog.voice_clients.pop(self.ctx.guild.id, None)
            await self.ctx.send("⏹️ Stopped and disconnected.")
        await self.update_button_states(None)


class AudioStream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.ffmpeg_options = {
            "before_options": (
                "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -rw_timeout 15000000"
            ),
            "options": "-vn",
        }

    @commands.command(name="radio", help="🎧 Opens the radio player")
    async def radio_menu(self, ctx):
        await ctx.send("https://i.ibb.co/HDS4vDFz/x.jpg")
        embed = discord.Embed(
            title="🎧 DOT-007 RADIO PLAYER",
            description="Select a station or control playback 🎶",
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(url="https://files.catbox.moe/xz4i4q.jpg")
        embed.set_footer(text="❤️ Enjoy nonstop music | DOT-007 Radio")

        view = RadioSelector(ctx, self)
        view.message = await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(AudioStream(bot))
