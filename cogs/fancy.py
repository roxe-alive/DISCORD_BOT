# Version: 1.0 Beta
# ©️ 2025 DOTSERMODZ ALL RIGHTS RESERVED

import discord
from discord.ext import commands
from config import Config
from lib.fancy import FANCY_FONTS

def apply_fancy(font_map, text):
    """Apply a font mapping to text."""
    return "".join(font_map.get(char, char) for char in text)

def generate_usage_examples(text: str):
    """Generate sample outputs for all fancy styles."""
    examples = f"**{Config.BOT_NAME} Fancy Text Generator** ✨\n\n" \
               f"**Usage:** `/fancy <style_number> <text>`\n\n" \
               f"**Examples:**\n"
    for style_num, font_map in FANCY_FONTS.items():
        examples += f"**{style_num}:** {apply_fancy(font_map, text)}\n"
    return examples


class FancyText(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fancy")
    async def fancy(self, ctx, style_number: int = None, *, text: str = None):
        """
        Convert text into fancy styles.
        Usage: /fancy <style_number> <text>
        """
        if style_number is None:
            example_text = "Hey You!"
            embed = discord.Embed(
                title=f"{Config.BOT_NAME} – Fancy Text Styles",
                description=generate_usage_examples(example_text),
                color=discord.Color.blurple()
            )
            await ctx.send(embed=embed)
            return

        # If no text provided, check if message was a reply
        if text is None and ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            text = replied_msg.content if replied_msg.content else None

        if not text:
            await ctx.send("⚠️ Please provide text to style or reply to a message.")
            return

        font_map = FANCY_FONTS.get(style_number)
        if not font_map:
            await ctx.send("❌ Invalid style number.")
            return

        styled_text = apply_fancy(font_map, text)
        await ctx.send(f"✨ **Fancy Style #{style_number}:**\n{styled_text}")


async def setup(bot):
    await bot.add_cog(FancyText(bot))
