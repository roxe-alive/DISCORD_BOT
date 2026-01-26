import discord
from discord.ext import commands
import os
import inspect
import time
from config import Config
from ops.Opps import Opps
from keep_alive import keep_alive  # start tiny Flask server

intents = discord.Intents.default()
# Configure privileged intents via environment flags
intents.message_content = Config.INTENTS_MESSAGE_CONTENT
intents.members = Config.INTENTS_GUILD_MEMBERS
intents.presences = Config.INTENTS_PRESENCES

# Create bot instance
bot = commands.Bot(command_prefix=Config.PREFIX, intents=intents)
bot.owner_id = Config.OWNER_ID

COGS_DIR = "./cogs"
PENDING_START_FILE = ".pending_start"
PREVIOUS_NOT_STARTED = False

async def _load_cogs():
    print(Opps)
    if not os.path.isdir(COGS_DIR):
        print("ℹ️ No 'cogs' directory found. Skipping cog loading.")
        return
    # Track load errors to report to owner
    bot._load_errors = []
    for filename in os.listdir(COGS_DIR):
        if not filename.endswith(".py"):
            continue
        ext_name = f"cogs.{filename[:-3]}"
        try:
            # Call load_extension; await only if it returns an awaitable (version-safe)
            result = bot.load_extension(ext_name)
            if inspect.isawaitable(result):
                await result
            print(f"✅ Loaded extension: {ext_name}")
        except Exception as e:
            print(f"❌ Failed to load extension {ext_name}: {e}")
            bot._load_errors.append((ext_name, str(e)))

    ext_dir = "./external_cogs"
    if os.path.isdir(ext_dir):
        for file in os.listdir(ext_dir):
            if not file.endswith(".py"):
                continue
            ext_name = f"external_cogs.{file[:-3]}"
            # Skip if already loaded (e.g., restored by external_plugins manager)
            if ext_name in bot.extensions:
                continue
            try:
                result = bot.load_extension(ext_name)
                if inspect.isawaitable(result):
                    await result
                print(f"✅ Loaded extension: {ext_name}")
            except Exception as e:
                print(f"❌ Failed to load extension {ext_name}: {e}")
                bot._load_errors.append((ext_name, str(e)))

@bot.event
async def setup_hook():
    # Called before on_ready; ideal for loading extensions & syncing app commands
    await _load_cogs()
    # If using app (slash) commands later, we can sync here.
    # await bot.tree.sync()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    # Warn if message_content intent disabled but prefix commands configured
    if not intents.message_content and Config.PREFIX:
        print("⚠️ message_content intent disabled; prefix commands may not trigger. Consider enabling intent or switching to slash commands.")

    # Attempt to DM the owner with startup status
    try:
        owner = bot.get_user(Config.OWNER_ID) or await bot.fetch_user(Config.OWNER_ID)
        if owner:
            lines = [
                f"✅ Bot started",
                f"Name: {Config.BOT_NAME} ({bot.user})",
                f"Version: {getattr(Config, 'BOT_VERSION', 'unknown')}",
                f"Prefix: {' '.join(Config.PREFIX) if isinstance(Config.PREFIX, (list, tuple)) else str(Config.PREFIX)}",
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Owner: {owner} ",
            ]
            if PREVIOUS_NOT_STARTED:
                lines.append("⚠️ Previous run did not reach ready (possible crash or forced stop).")
            if getattr(bot, "_load_errors", []):
                lines.append("❌ Extensions failed to load:")
                for name, err in bot._load_errors:
                    # Keep message short to avoid DM limits
                    err_short = err if len(err) < 180 else err[:177] + "..."
                    lines.append(f"- {name}: {err_short}")
            await owner.send("\n".join(lines))
    except Exception:
        # Silently ignore DM issues (privacy settings, etc.)
        pass

    # Clear pending-start marker on successful ready
    try:
        if os.path.exists(PENDING_START_FILE):
            os.remove(PENDING_START_FILE)
    except Exception:
        pass

if __name__ == "__main__":
    # Launch keep-alive HTTP server first so external pings begin immediately.
    keep_alive()
    # Mark pending start (removed once on_ready fires). If it already exists,
    # we infer previous run didn't reach on_ready.
    PREVIOUS_NOT_STARTED = os.path.exists(PENDING_START_FILE)
    try:
        with open(PENDING_START_FILE, "w", encoding="utf-8") as f:
            f.write(str(time.time()))
    except Exception:
        pass
    bot.run(Config.BOT_TOKEN)
