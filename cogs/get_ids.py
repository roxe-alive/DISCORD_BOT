import discord
from discord.ext import commands

class IDTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🧍 Get user ID
    @commands.command(aliases=["uid", "userid"] , help="Get User ID")
    async def user_id(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title="🧍 User ID",
            description=f"**{member}** → `{member.id}`",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # 💬 Get current channel ID
    @commands.command(aliases=["cid", "channelid"] , help="Get Channel ID")
    async def channel_id(self, ctx):
        channel = ctx.channel
        embed = discord.Embed(
            title="💬 Channel ID",
            description=f"**#{channel.name}** → `{channel.id}`",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    # 🏰 Get server (guild) ID
    @commands.command(aliases=["gid", "serverid"] , help="Get Server ID")
    async def server_id(self, ctx):
        guild = ctx.guild
        if not guild:
            await ctx.send("❌ This command must be used in a server.")
            return

        embed = discord.Embed(
            title="🏰 Server ID",
            description=f"**{guild.name}** → `{guild.id}`",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(IDTools(bot))
