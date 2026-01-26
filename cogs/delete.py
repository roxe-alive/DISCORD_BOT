import discord
from discord.ext import commands

class DeleteRepliedMessage(commands.Cog):
    """Deletes the message you replied to when you type !delete"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="delete" , help="Deletes the message you replied to.")
    async def delete_replied(self, ctx):
        if not ctx.message.reference:
            return await ctx.reply("❌ You must reply to a message to use this command.", mention_author=False)

        try:
            # Fetch the replied message
            replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            await replied_message.delete()
            await ctx.reply("✅ Message deleted.", mention_author=False)
        except discord.Forbidden:
            await ctx.reply("I don’t have permission to delete that message.", mention_author=False)
        except discord.NotFound:
            await ctx.reply("Message not found (maybe already deleted).", mention_author=False)
        except Exception as e:
            await ctx.reply(f"Unexpected error: `{e}`", mention_author=False)

async def setup(bot):
    await bot.add_cog(DeleteRepliedMessage(bot))
