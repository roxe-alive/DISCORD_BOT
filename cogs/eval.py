# Version: 1.0 Beta
# ©️ 2025 DOTSERMODZ ALL RIGHTS RESERVED

import discord
from discord.ext import commands
import io
import sys
import traceback
import os
from contextlib import redirect_stdout
from config import Config


class EvalCog(commands.Cog):
    """Owner-only Eval Command Cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="eval")
    async def _eval(self, ctx, *, code: str = None):
        # Permission check: allow if author ID is in configured owner list
        if ctx.author.id not in getattr(Config, "OWNER_IDS", [Config.OWNER_ID]):
            return await ctx.reply("❌ You don't have permission to use this command.")

        if not code:
            return await ctx.reply("⚠️ Usage: `!eval <python code>`")

        # Prepare async eval environment
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "message": ctx.message,
            "author": ctx.author,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "discord": discord,
            "commands": commands,
            "_": None,
        }

        # Capture stdout/stderr
        stdout = io.StringIO()
        code = code.strip("` ")

        # Define async def block
        to_compile = f"async def func():\n"
        for line in code.split("\n"):
            to_compile += f"    {line}\n"

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.reply(f"❌ **Compilation Error:**\n```py\n{e.__class__.__name__}: {e}\n```")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            error = traceback.format_exc()
            result = f"⚠️ **Error:**\n```error\n{value}{error}\n```"
        else:
            value = stdout.getvalue()
            result = f"✅ **Output:**\n```success\n{value}{ret if ret is not None else ''}```"

        # Handle long outputs
        if len(result) > 1900:
            with open("eval.txt", "w", encoding="utf-8") as f:
                f.write(result)
            await ctx.reply("📄 Output too long. Sent as file:", file=discord.File("eval.txt"))
            os.remove("eval.txt")
        else:
            await ctx.reply(result)


async def setup(bot):
    await bot.add_cog(EvalCog(bot))
