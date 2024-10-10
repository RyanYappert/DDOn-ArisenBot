import ArisenBotCommon, os, tabulate, datetime, discord, requests
from discord.ext import commands
from discord import app_commands

class ArisenBotUser(commands.Cog, name = "serverstatus"):
    CACHE_TIME = float(os.getenv('ARISENBOT_SERVER_CACHE_TIME'))

    def __init__(self, bot):
        self.bot = bot
        self.serverStatusCache = {}
        self.serverCacheTime = datetime.datetime.min

    def needRefresh(self):
            currentTime = datetime.datetime.now()
            return (abs(currentTime - self.serverCacheTime)).total_seconds() / 60.0 >= self.CACHE_TIME

    @app_commands.command(name='status', description="Check server status.")
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_2)
    @app_commands.checks.cooldown(1, 30.0)
    async def server_status(self, itx : discord.Interaction):
        now = datetime.datetime.now()
        if (self.needRefresh()):
            try:
                result = ArisenBotCommon.serverGET(ArisenBotCommon.randomServer(), "status", {"serverid" : 0, "all" : True})
            except requests.ConnectionError:
                await itx.response.send_message("❌ The server did not respond. It might be down. ❌", ephemeral=True)
                return
            
            for status in result.json():
                self.serverStatusCache[status["Id"]] = status
            serverCacheTime = now

        statuslist = [[status[i] for i in ["Name", "LoginNum", "MaxLoginNum"]] for status in self.serverStatusCache.values()]
        s = "```"
        s += tabulate.tabulate(statuslist, headers=["Channel", "Players", "Max"])
        s += "```"

        minutesSinceCache = (now - serverCacheTime).total_seconds() / 60.0
        s += f"Last fetched {int(minutesSinceCache)} minute(s) ago."
        await itx.response.send_message(s)

async def setup(bot):
    await bot.add_cog(ArisenBotUser(bot), guild = discord.Object(id=ArisenBotCommon.GUILD))