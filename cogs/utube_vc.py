import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  # Store active voice clients

    async def ensure_song_channel(self, ctx):

        target_category_name = "This Is 4 You! 🪻 <3"

        # Determine target category
        category = None
        if ctx.author.voice and ctx.author.voice.channel and ctx.author.voice.channel.category:
            category = ctx.author.voice.channel.category
        else:
            category = discord.utils.get(ctx.guild.categories, name=target_category_name)
            if category is None:
                try:
                    category = await ctx.guild.create_category(target_category_name)
                except discord.Forbidden:
                    # Lack permissions; bail quietly
                    return None
                except discord.HTTPException:
                    return None

        # Ensure the 'Song 4 u' voice channel exists under the category
        song_channel = discord.utils.get(ctx.guild.voice_channels, name="Song 4 u", category=category)
        if song_channel is None:
            try:
                song_channel = await ctx.guild.create_voice_channel(name="Song 4 u", category=category)
            except discord.Forbidden:
                return None
            except discord.HTTPException:
                return None

        return song_channel

    def search_yt(self, query: str):
        """Search or fetch a YouTube link using yt_dlp."""
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "cookiefile": "cookies.txt",
           
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Direct link
                info = ydl.extract_info(query, download=False)
            except Exception:
                # Text search
                info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]

        return info["url"], info.get("title", "Unknown Title")

    async def connect_vc(self, ctx):
        """Connect the bot to the user's voice channel."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await channel.connect()
            elif ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
            return True
        else:
            await ctx.reply("⚠️ You must join a voice channel first.")
            return False

    @commands.command(name="play")
    async def play(self, ctx, *, query: str):
        """Play a song from YouTube by name or link."""
        # Make sure a dedicated song channel exists under the same category as radio_vc.py
        await self.ensure_song_channel(ctx)

        if not await self.connect_vc(ctx):
            return

        url, title = self.search_yt(query)
        await ctx.send(f"🎵 **Now Playing:** `{title}`")

        vc = ctx.voice_client
        ffmpeg_opts = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        try:
            vc.stop()
            vc.play(
                FFmpegPCMAudio(url, **ffmpeg_opts),
                after=lambda e: print(f"Player error: {e}") if e else None,
            )
        except Exception as e:
            await ctx.send(f"❌ Error playing audio: `{e}`")




async def setup(bot):
    await bot.add_cog(Music(bot))
