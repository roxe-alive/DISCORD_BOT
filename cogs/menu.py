import discord
from discord.ext import commands
import datetime
from config import Config

star = "⌀"
class Menu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="menu", help="Displays all commands and bot information.")
    async def menu(self, ctx):
        """Show bot info and all commands in an embed menu."""
        # Get owner info (if available)
        app_info = await self.bot.application_info()
        owner_name = app_info.owner.name if app_info and app_info.owner else "Unknown"

        # Get current date/time
        now = datetime.datetime.now().strftime("%d %b %Y | %I:%M %p")

        # Embed header
        embed = discord.Embed(
            title=f"Menu",
            description="Bot info",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow()
        )

        # 🧾 Header info block
        embed.add_field(
            name=f"**Bot Name:** {self.bot.user.name}\n",
            value=(
        
                f"**{star} Prefix:** `{Config.PREFIX}`\n"
                f"**{star} Platform:** Discord\n"
                f"**{star} Owner:** {owner_name}\n"
                f"**{star} Date:** {now}\n"
                f"**{star} Requested by:** {ctx.author}\n"
                f"**{star} Version:** {Config.BOT_VERSION}"
            ),
            inline=False
        )

        # 🖼️ Thumbnail
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # Add commands grouped by Cog
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_commands()
            filtered = [cmd for cmd in commands_list if not cmd.hidden]
            if filtered:
                cmd_text = "\n".join(
                    [f"`{ctx.prefix}{cmd.name}` – {cmd.help or 'No description'}"
                     for cmd in filtered]
                )
                embed.add_field(name=f"→ {cog_name}", value=cmd_text, inline=False)

        # Add uncategorized commands
        uncategorized = [cmd for cmd in self.bot.commands if cmd.cog is None and not cmd.hidden]
        if uncategorized:
            cmd_text = "\n".join(
                [f"`{ctx.prefix}{cmd.name}` – {cmd.help or 'No description'}"
                 for cmd in uncategorized]
            )
            embed.add_field(name="⚙️ Miscellaneous", value=cmd_text, inline=False)

        # Footer
        embed.set_footer(text=f"{self.bot.user.name} • Powered by DOT-007", icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Menu(bot))
