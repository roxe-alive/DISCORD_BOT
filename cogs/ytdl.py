import discord
from discord.ext import commands
from discord import ui
import yt_dlp
import asyncio
import os

COOKIES_FILE = "cookies.txt"  # optional cookies file path

# ------------------ SELECT MENUS ------------------

class FormatSelect(ui.Select):
    def __init__(self, url, ctx, title):
        self.url = url
        self.ctx = ctx
        self.title = title
        options = [
            discord.SelectOption(label="🎧 Audio Only", description="Download as MP3"),
            discord.SelectOption(label="🎥 Video", description="Choose resolution and download"),
        ]
        super().__init__(placeholder="Choose download type...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "🎧 Audio Only":
            await interaction.response.edit_message(content=f"🎵 Downloading **{self.title}** as audio...", view=None)
            await self.download_audio(interaction)
        else:
            await interaction.response.edit_message(
                content=f"📺 Choose resolution for **{self.title}**:",
                view=ResolutionView(self.url, self.ctx, self.title)
            )

    async def download_audio(self, interaction):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }
        if os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

        os.makedirs("downloads", exist_ok=True)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp3"

            await interaction.followup.send(
                content=f"✅ **{info.get('title')}** (Audio)",
                file=discord.File(filename)
            )

            await asyncio.sleep(3)
            os.remove(filename)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")


class ResolutionSelect(ui.Select):
    def __init__(self, url, ctx, title):
        self.url = url
        self.ctx = ctx
        self.title = title
        options = [
            discord.SelectOption(label="144p"),
            discord.SelectOption(label="360p"),
            discord.SelectOption(label="480p"),
            discord.SelectOption(label="720p"),
            discord.SelectOption(label="1080p"),
        ]
        super().__init__(placeholder="Select video resolution...", options=options)

    async def callback(self, interaction: discord.Interaction):
        res = self.values[0]
        await interaction.response.edit_message(
            content=f"⬇️ Downloading **{self.title}** in {res}...",
            view=None
        )
        await self.download_video(interaction, res)

    async def download_video(self, interaction, resolution):
        ydl_opts = {
            "format": f"bestvideo[height<={resolution.replace('p','')}] +bestaudio/best",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "merge_output_format": "mp4",
            "quiet": True,
        }
        if os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

        os.makedirs("downloads", exist_ok=True)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                filename = ydl.prepare_filename(info)
                if not filename.endswith(".mp4"):
                    filename = os.path.splitext(filename)[0] + ".mp4"

            await interaction.followup.send(
                content=f"✅ **{info.get('title')}** ({resolution})",
                file=discord.File(filename)
            )

            await asyncio.sleep(3)
            os.remove(filename)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")


# ------------------ VIEWS ------------------

class FormatView(ui.View):
    def __init__(self, url, ctx, title, timeout=60):
        super().__init__(timeout=timeout)
        self.add_item(FormatSelect(url, ctx, title))

class ResolutionView(ui.View):
    def __init__(self, url, ctx, title, timeout=60):
        super().__init__(timeout=timeout)
        self.add_item(ResolutionSelect(url, ctx, title))


# ------------------ MAIN COG ------------------

class YouTubeDownloader(commands.Cog):
    """YouTube downloader — supports !yt <link> and !yts <query>"""

    def __init__(self, bot):
        self.bot = bot

    def search_youtube(self, query: str):
        """Search YouTube and return first result URL + title"""
        ydl_opts = {
            "quiet": True,
            "extract_flat": "in_playlist",
            "skip_download": True,
        }
        if os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info and "entries" in info and len(info["entries"]) > 0:
                first = info["entries"][0]
                return f"https://www.youtube.com/watch?v={first['id']}", first["title"]
        return None, None

    @commands.command(name="yt")
    async def yt(self, ctx, *, url: str = None):
        """Download directly from YouTube URL"""
        if not url:
            embed = discord.Embed(
                title="🎬 YouTube Downloader Usage",
                description=(
                    "**Usage:**\n"
                    "`!yt <youtube link>`\n\n"
                    "**Example:**\n"
                    "`!yt https://youtu.be/dQw4w9WgXcQ`\n\n"
                    "🎧 Download audio or 🎥 choose video resolution.\n"
                    "Supports cookies.txt for restricted videos."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="YouTube Downloader | yt-dlp powered")
            return await ctx.send(embed=embed)

        # Extract video info
        ydl_opts = {"quiet": True, "skip_download": True}
        if os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "YouTube Video")
        except Exception as e:
            return await ctx.send(f"❌ Invalid or inaccessible link.\n```{e}```")

        embed = discord.Embed(
            title=title,
            url=url,
            description="Select a download option below:",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{info['id']}/0.jpg")
        await ctx.send(embed=embed, view=FormatView(url, ctx, title))

    @commands.command(name="yts")
    async def yts(self, ctx, *, query: str = None):
        """Search YouTube and download by name"""
        if not query:
            embed = discord.Embed(
                title="🎬 YouTube Search Downloader Usage",
                description=(
                    "**Usage:**\n"
                    "`!yts <search query>`\n\n"
                    "**Example:**\n"
                    "`!yts despacito`\n\n"
                    "The bot searches YouTube and lets you choose audio or video download."
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="YouTube Downloader | yt-dlp powered")
            return await ctx.send(embed=embed)

        await ctx.send("🔎 Searching on YouTube...")
        url, title = self.search_youtube(query)
        if not url:
            return await ctx.send("❌ No results found.")

        embed = discord.Embed(
            title=title,
            url=url,
            description="Select a download option below:",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{url.split('=')[1]}/0.jpg")
        await ctx.send(embed=embed, view=FormatView(url, ctx, title))


async def setup(bot):
    await bot.add_cog(YouTubeDownloader(bot))
