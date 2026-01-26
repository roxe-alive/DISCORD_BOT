import os
import re
import ast
import aiohttp
import asyncio
import discord
from discord.ext import commands
from database import external_plugins  # <<— YOUR REQUEST

EXTERNAL_FOLDER = "external_cogs"

class PluginManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(EXTERNAL_FOLDER, exist_ok=True)

    # --------------- HELPERS: NAME EXTRACTION ---------------
    def _sanitize_module_name(self, name: str) -> str:
        name = name.strip()
        if not name:
            return "plugin"
        # Replace invalid chars with underscores, lower-case
        name = re.sub(r"[^0-9a-zA-Z_]", "_", name).lower()
        # Must start with letter or underscore for a valid identifier
        if not re.match(r"^[a-zA-Z_]", name):
            name = f"plugin_{name}"
        # Collapse multiple underscores
        name = re.sub(r"_+", "_", name)
        return name

    def _extract_cog_class_name(self, source: str) -> str | None:
        try:
            tree = ast.parse(source)
        except Exception:
            return None

        def is_cog_base(base: ast.expr) -> bool:
            # Matches: Cog, commands.Cog, discord.ext.commands.Cog
            if isinstance(base, ast.Name):
                return base.id == "Cog"
            if isinstance(base, ast.Attribute):
                # Walk the attribute chain to a dotted string
                parts = []
                cur = base
                while isinstance(cur, ast.Attribute):
                    parts.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.append(cur.id)
                dotted = ".".join(reversed(parts))
                return dotted.endswith("commands.Cog") or dotted == "Cog"
            return False

        # Prefer first class that subclasses Cog
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                if any(is_cog_base(b) for b in node.bases):
                    return node.name

        # Fallback: try to infer from async def setup(bot): add_cog(Foo(bot))
        for node in tree.body:
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "setup":
                for n in ast.walk(node):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                        if n.func.attr == "add_cog" and n.args:
                            first_arg = n.args[0]
                            # add_cog(Foo(bot))
                            if isinstance(first_arg, ast.Call) and isinstance(first_arg.func, ast.Name):
                                return first_arg.func.name
        return None

    async def _choose_unique_plugin_name(self, base_name: str) -> str:
        base_name = self._sanitize_module_name(base_name)
        existing = await external_plugins.get_all()
        existing_names = {row['plugin_name'] for row in (existing or [])}

        candidate = base_name
        i = 1
        while True:
            file_exists = os.path.exists(os.path.join(EXTERNAL_FOLDER, candidate + ".py"))
            if candidate not in existing_names and not file_exists:
                return candidate
            i += 1
            candidate = f"{base_name}_{i}"

    # ---------------- DOWNLOAD GIST ----------------
    async def download_gist(self, gist_url: str):
        try:
            if "gist.github.com" in gist_url:
                parts = gist_url.split("/")
                file_id = parts[-1]
                user = parts[-2]
                raw_url = f"https://gist.githubusercontent.com/{user}/{file_id}/raw"
            else:
                raw_url = gist_url

            async with aiohttp.ClientSession() as session:
                async with session.get(raw_url) as resp:
                    if resp.status != 200:
                        return None
                    return await resp.text()
        except:
            return None

    # ---------------- INSTALL ----------------
    @commands.command(
        help="Install a plugin from a GitHub Gist or raw URL.",
        usage="install <gist_url_or_raw_url>"
    )
    @commands.is_owner()
    async def install(self, ctx, *, gist_url: str):
        await ctx.send("📥 Downloading plugin...")

        content = await self.download_gist(gist_url)
        if not content:
            return await ctx.send("❌ Failed to download gist.")

        # Determine plugin name from class name if possible, fallback to time-based
        deduced_class = self._extract_cog_class_name(content) or f"plugin_{int(asyncio.get_event_loop().time())}"
        plugin_name = await self._choose_unique_plugin_name(deduced_class)
        file_name = plugin_name + ".py"
        path = os.path.join(EXTERNAL_FOLDER, file_name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        try:
            await self.bot.load_extension(f"{EXTERNAL_FOLDER}.{plugin_name}")
            await external_plugins.add(plugin_name, file_name, gist_url)
            await ctx.send(f"✅ Installed plugin: **{plugin_name}**")
        except Exception as e:
            await ctx.send(f"⚠️ Load error:\n```\n{e}\n```")

    @install.error
    async def install_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) and getattr(error, 'param', None) and error.param.name == 'gist_url':
            prefix = ctx.clean_prefix if hasattr(ctx, 'clean_prefix') else '!'
            return await ctx.send(
                "❗ Missing required argument `gist_url`.\n"
                f"Usage: `{prefix}install <gist_url_or_raw_url>`\n"
                "Examples:\n"
                f"`{prefix}install https://gist.github.com/<user>/<id>`\n"
                f"`{prefix}install https://gist.githubusercontent.com/<user>/<id>/raw`")
        # Re-raise other errors for global handlers
        raise error

    # ---------------- UNINSTALL ----------------
    @commands.command(
        help="Uninstall a previously installed external plugin.",
        usage="uninstall <plugin_name>"
    )
    @commands.is_owner()
    async def uninstall(self, ctx, plugin_name: str):
        module_path = f"{EXTERNAL_FOLDER}.{plugin_name}"

        try:
            await self.bot.unload_extension(module_path)
        except:
            pass

        await external_plugins.remove(plugin_name)

        file_path = os.path.join(EXTERNAL_FOLDER, plugin_name + ".py")
        if os.path.exists(file_path):
            os.remove(file_path)

        await ctx.send(f"🗑️ Uninstalled plugin: **{plugin_name}**")

    @uninstall.error
    async def uninstall_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) and getattr(error, 'param', None) and error.param.name == 'plugin_name':
            prefix = ctx.clean_prefix if hasattr(ctx, 'clean_prefix') else '!'
            installed = await external_plugins.get_all()
            names = ", ".join(p['plugin_name'] for p in installed) if installed else "<none>"
            return await ctx.send(
                "❗ Missing required argument `plugin_name`.\n"
                f"Usage: `{prefix}uninstall <plugin_name>`\n"
                f"Installed: {names}")
        raise error

    # ---------------- LIST ----------------
    @commands.command()
    @commands.is_owner()
    async def plugins(self, ctx):
        rows = await external_plugins.get_all()
        if not rows:
            return await ctx.send("📭 No external plugins installed.")

        msg = "📦 **Plugins (from DB)**\n```\n"
        for p in rows:
            msg += f"{p['plugin_name']} -> {p['gist_url']}\n"
        msg += "```"

        await ctx.send(msg)

    # ---------------- RESTORE ON BOOT ----------------
    async def restore_plugins(self):
        rows = await external_plugins.get_all()
        for p in rows:
            try:
                await self.bot.load_extension(f"{EXTERNAL_FOLDER}.{p['plugin_name']}")
                print(f"[RESTORED] {p['plugin_name']}")
            except Exception as e:
                print(f"[FAILED] {p['plugin_name']} — {e}")

async def setup(bot):
    manager = PluginManager(bot)
    await bot.add_cog(manager)
    await manager.restore_plugins()
