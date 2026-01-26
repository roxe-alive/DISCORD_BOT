# Version: 1.0
# ©️ 2025 DOTSERMODZ ALL RIGHTS RESERVED
# Simple clear (purge) command for Discord Bot

import discord
from discord.ext import commands

class ClearCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear", help="Delete messages in the channel. Usage: !clear <amount or all>")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: str = None):
        """
        Clears messages from the current channel.
        - `!clear 10` deletes the last 10 messages
        - `!clear all` deletes everything (up to 1000)
        """
        await ctx.message.delete()  # Delete the command itself for cleanliness

        if amount is None:
            return await ctx.send("⚠️ Usage: `!clear <number>` or `!clear all`", delete_after=5)

        try:
            if amount.lower() == "all":
                deleted = await ctx.channel.purge(limit=1000)
                msg = await ctx.send(f"🧹 Cleared **{len(deleted)}** messages from this channel.", delete_after=5)
            else:
                num = int(amount)
                if num <= 0:
                    return await ctx.send("⚠️ Number must be greater than 0.", delete_after=5)
                deleted = await ctx.channel.purge(limit=num + 1)
                msg = await ctx.send(f"🧽 Deleted **{len(deleted) - 1}** messages.", delete_after=5)
        except ValueError:
            msg = await ctx.send("❌ Invalid number. Use `!clear 10` or `!clear all`.", delete_after=5)
        except discord.Forbidden:
            msg = await ctx.send("❌ Missing permission: `Manage Messages`.", delete_after=5)
        except Exception as e:
            msg = await ctx.send(f"⚠️ Error: `{e}`", delete_after=5)

    @clear_messages.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 You don't have permission to use this command.", delete_after=5)

async def setup(bot):
    await bot.add_cog(ClearCommand(bot))
