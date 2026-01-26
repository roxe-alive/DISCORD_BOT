import discord
from discord.ext import commands

class Manage_vc(commands.Cog):
    """A simple YouTube music player for Discord."""

    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}  

    async def connect_vc(self, ctx):
        """Connect the bot to the user's current voice channel or move to it."""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            try:
                if ctx.voice_client is None:
                    await channel.connect()
                elif ctx.voice_client.channel != channel:
                    await ctx.voice_client.move_to(channel)
                await ctx.send(f"✅ Joined **{channel.name}**.")
                return True
            except discord.Forbidden:
                await ctx.send("⚠️ I don't have permission to join that voice channel. Please promote me as admin, or move me to a channel I can access.")
                return False
            except discord.HTTPException as e:
                await ctx.send(f"❌ Failed to connect to voice channel: `{e}`")
                return False
        else:
            await ctx.reply("⚠️ You must join a voice channel first.")
            return False


    
    @commands.command(name="join")
    async def join_vc(self, ctx):
        """Join the voice channel you are in."""
        await self.connect_vc(ctx)
    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stop the currently playing song."""
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.send("⏹️ Music stopped.")

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Disconnect the bot from voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Disconnected from the voice channel.")


async def setup(bot):
    await bot.add_cog(Manage_vc(bot))
