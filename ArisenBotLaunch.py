import ArisenBotCommon
import discord, asyncio, os, logging, logging.handlers
from discord.ext import commands
from discord import app_commands

discord.utils.setup_logging()

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix = "!!!", intents = intents, help_command = None)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=ArisenBotCommon.GUILD))

async def on_application_command_error(itx: discord.Interaction, error: discord.DiscordException):
    if isinstance(error, app_commands.CommandOnCooldown):
        await itx.response.send_message("This command is currently on cooldown!", ephemeral=True)
    elif isinstance(error, app_commands.MissingAnyRole):
        await itx.response.send_message("You lack permission to use this command.", ephemeral=True)
    else:
        raise error 
bot.tree.on_error = on_application_command_error

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(ArisenBotCommon.TOKEN)

asyncio.run(main())