# DDOn-ArisenBot
Discord integration for Arrowgene.DragonsDogmaOnline RPC routes.

# Installation
- Clone the directory.
- Install requirements with `pip install -r requirements.txt`.

# Setup
- Set up a Discord App on the [Developer Portal](https://discord.com/developers/applications).
  - ArisenBot currently only requires the `bot` and `applications.commands` scopes.
- Set up a GameMaster level account for ArisenBot in the Arrowgene.DragonsDogmaOnline database.
- Set up ArisenBot's environmental variables:
  - `DISCORD_TOKEN`: The token provided from the Discord Developer portal.
  - `DISCORD_GID`: The guild ID of the server that ArisenBot will be servicing.
  - `DDON_USERNAME`: The username of ArisenBot's account for DDON.
  - `DDON_PASSWORD`: Similarly, its password.
  - `ARISENBOT_SERVER_CSV`: Path to a CSV of the RPC servers for the DDON server's channels.
  - `ARISENBOT_SERVER_CACHE_TIME`: Time, in minutes, that server status is cached for.
- Invite ArisenBot to your Discord server through the link in the Developer Portal.
- Run `ArisenBotLaunch.py`.
  - This process must be kept running for the bot to function.
