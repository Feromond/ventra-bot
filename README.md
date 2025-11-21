# Ventra Bot

Ventra Bot is a Discord bot built with `discord.py` that bundles general utility commands with Minecraft-specific tooling. It supports both traditional prefixed commands and slash (application) commands, and includes a background task that can keep a Minecraft status message refreshed inside channels named `server-status` or `server_status`.

## Features

- **General utilities** – `/help`, `/ping`, `/invite`, `/server` for quick server introspection.
- **Community helpers** – `/poll`, `/userinfo`, and the `/advancedpoll` slash command for multi-option emoji polls.
- **Minecraft integration** – `/status` and `/player-list` commands powered by `mcstatus`, plus an automated loop that posts live stats for `ventra.dev`.

## Requirements

- Python 3.11+ (the project has been tested with Python 3.14).
- A Discord bot application and token with the necessary privileged intents enabled in the Developer Portal.
- Access to the target Minecraft server if you plan to use the background status updates.

## Configuration

1. **Environment variables**  
   Create a `.env` file in the repository root with your bot token:

   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

2. **`config.json`**  
   Ensure the file exists at the project root with at least the following keys:
   ```
   {
     "prefix": "!!",
     "invite_link": "https://discord.com/api/oauth2/authorize?client_id=..."
   }
   ```
   - `prefix` is used for legacy commands and the activity message.
   - `invite_link` is referenced by the `/invite` command.

## Makefile-driven Setup

The refreshed `Makefile` streamlines the most common workflows:

| Command       | Description                                                                                                     |
| ------------- | --------------------------------------------------------------------------------------------------------------- |
| `make init`   | Create the `discordbotcourse` virtual environment (if needed) and install dependencies from `requirements.txt`. |
| `make run`    | Activate the environment and launch `bot.py`.                                                                   |
| `make clean`  | Remove the virtual environment and cached bytecode.                                                             |
| `make freeze` | Regenerate `requirements.txt` via `pip freeze` (after activating/locking dependencies).                         |

All targets rely on `python3` by default; override with `make PYTHON=python3.12 init` if required. The virtual environment directory and activation script are configurable via `VENV_DIR`.

## Manual Setup (without Makefile)

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Configure `.env` and `config.json` as shown above.
4. Run the bot:
   ```bash
   python bot.py
   ```

## Command Overview

- `general` cog: `/help`, `/ping`, `/invite`, `/server`
- `utility` cog: `/poll`, `/userinfo`, `/advancedpoll`
- `minecraft` cog: `/status <ip>`, `/player-list <ip>` plus the background status loop (runs every minute and edits the bot's most recent message in matching channels).
- Owner-only commands defined in `bot.py`: `sync`, `clearsync`

Hybrid commands can be invoked with the prefix from `config.json` or via slash commands once synced.

## Development Notes

- Use `make freeze` after adding new dependencies so `requirements.txt` stays in sync.
- The background Minecraft task currently targets `ventra.dev`; adjust `target_server` in `cogs/minecraft.py` if you want a different default.
- When adding new cogs, place them in `cogs/` and they will be auto-loaded on startup.

## Troubleshooting

- **Token errors**: Ensure `DISCORD_TOKEN` is available in the environment before launching.
- **Missing `config.json`**: The bot exits early if the file is absent—copy the structure above.
- **Slash commands not visible**: Run the owner-only `sync` command inside the target guild to force-refresh application commands, or wait for the global cache to propagate.
