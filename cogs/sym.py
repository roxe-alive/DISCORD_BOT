import discord
from discord.ext import commands
import os
import sys
import asyncio
from config import Config

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Check bot latency.")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! **{latency}ms**")

    @commands.command(help="Shut down the bot.")
    @commands.is_owner()  # Only bot owner can run this
    async def shutdown(self, ctx):
        await ctx.send("Bot is shutting down...")
        await self.bot.close()

    @commands.command(aliases=["reboot", "restart"], help="Restart the bot.")
    @commands.is_owner()
    async def restart_bot(self, ctx):
        await ctx.send("♻️ Restarting bot...")
        await asyncio.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)



async def setup(bot):
    await bot.add_cog(System(bot))
