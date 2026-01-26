import discord
from config import Config
import datetime

start_up = datetime.datetime.now().strftime("%d %b %Y | %I:%M %p")

Opps = \
f"""                                                                                                       
Developed by DOT-007
Bot Name: {Config.BOT_NAME}
Bot Prefix: {Config.PREFIX}
Startup Time: {start_up}
Version: {Config.BOT_VERSION}
Library: discord.py {discord.__version__}
Developer: DOT-007
Copyright ©️ 2025 DOTSERMODZ.

"""