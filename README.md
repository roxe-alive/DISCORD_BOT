
# Discord Bot

A modular, production-ready **Discord bot** built with **discord.py**, supporting dynamic cog loading, environment-based configuration, Docker deployment, and a built-in keep-alive server for cloud hosting.


![alt text](https://files.catbox.moe/f11xqf.jpg)



---

## 🚀 Features

* 🔌 **Modular architecture** using Cogs (`/cogs` & `/external_cogs`)
* 🔐 **Environment-based configuration** with early validation
* 👑 **Single or multiple bot owners** support
* ⚡ **Prefix-based commands** (multi-prefix supported)
* 🧠 **Privileged intents toggle** via environment variables
* 🐳 **Docker ready**
* 🌐 **Keep-alive Flask server** (ideal for Render / Replit / Railway)
* 📩 **Startup status DM to owner**
* 🧩 Automatic detection of failed extensions
* 🔄 Crash detection using pending start marker

---
<p align="center">
  <img src="https://img.shields.io/github/license/Dot-ser/DISCORD_BOT" />
  <img src="https://img.shields.io/github/stars/Dot-ser/DISCORD_BOT?style=social" />
  <img src="https://img.shields.io/github/forks/Dot-ser/DISCORD_BOT?style=social" />
</p>


---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Discord.py-Latest-5865F2?logo=discord&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success" />
</p>

## 📁 Project Structure

```
.
├── main.py              # Bot entry point
├── config.py            # Environment & configuration loader
├── config.env           # Environment variables (not committed)
├── Dockerfile           # Docker build configuration
├── keep_alive.py        # Lightweight Flask keep-alive server
├── cogs/                # Internal bot extensions
├── external_cogs/       # External / plugin-based extensions
└── README.md
```

---

## ⚙️ Configuration

Create a `config.env` file in the root directory:

```env
BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN

# Bot identity
BOT_NAME=Roxe
BOT_LOGO=https://files.catbox.moe/xz4i4q.jpg
PREFIX=!

# Owner (single or multiple)
OWNER_ID=123456789012345678
# OR
# OWNER_IDS=123456789012345678,987654321098765432

# Optional database
DATABASE_URL=

```

> ⚠️ `BOT_TOKEN` is **required**. The bot will not start without it.

---

## ▶️ Running Locally

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

*(Make sure you are using Python 3.9+)*

### 2️⃣ Start the bot

```bash
python main.py
```

---

---

## 🌐 Keep-Alive Server

The bot starts a lightweight **Flask server** to prevent idling on free hosting platforms.

### Available endpoints:

| Endpoint  | Response             |
| --------- | -------------------- |
| `/`       | `OK`                 |
| `/health` | `{ "status": "ok" }` |

You can use services like:

* UptimeRobot
* BetterStack
* Cron-job.org

to ping the bot every 5 minutes.

---

## 🧩 Cogs & Extensions

* Place internal extensions in `/cogs`
* Place plugin-based extensions in `/external_cogs`
* All `.py` files are auto-loaded on startup
* Load failures are:

  * Logged to console
  * Reported to the bot owner via DM

---

## 👑 Owner Permissions

* Supports **multiple owners**
* Uses `OWNER_IDS` (comma or space separated)
* Backward compatible `OWNER_ID` still available
* Ideal for eval commands, admin tools, and restricted actions

---

## 📩 Startup Notifications

On successful startup, the bot will DM the owner with:

* Bot name & ID
* Version
* Prefix
* Load status of extensions
* Warning if previous run crashed

---

## 🛠 Tech Stack

* **Python**
* **discord.py**
* **Flask** (keep-alive)
* **Docker**
* **dotenv**

---

## 📄 License

This project is open-source and free to use for personal and educational purposes.

---

## 💡 Author

**Alosious Benny**
🚀 Built for scalability and production use

---
