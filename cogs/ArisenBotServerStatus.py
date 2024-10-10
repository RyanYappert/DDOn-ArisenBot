import ArisenBotCommon, os, tabulate, datetime, discord, requests
from discord.ext import commands
from discord import app_commands

class ArisenBotServerStatus(commands.GroupCog, name = "server"):
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

    @app_commands.command(name='add', description = 'Add a server.')
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_0)
    async def add_server(self, itx : discord.Interaction, id : int, name : str, address : str, port : int):
        ArisenBotCommon.rpcServers.append([id, name, address, port])
        await itx.response.send_message("New server added:\n`{0}`".format(ArisenBotCommon.serverPrint(ArisenBotCommon.rpcServers[-1])))

    @app_commands.command(name='remove', description = 'Remove a server.')
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_0)
    @app_commands.autocomplete(id = ArisenBotCommon.server_autocomplete)
    async def remove_server(self, itx : discord.Interaction, id : int):
        remove = False
        for i in range(len(ArisenBotCommon.rpcServers)):
            if ArisenBotCommon.rpcServers[0] == id:
                remove = True
                break
        if remove:
            server = ArisenBotCommon.rpcServers.pop(i)
            await itx.response.send_message("Server removed:\n`{0}`".format(ArisenBotCommon.serverPrint(server)))
        else:
            await itx.response.send_message('Invalid id for server removal.', ephemeral=True)            

    @app_commands.command(name='list', description = 'List all servers.')
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_1)
    async def list_servers(self, itx : discord.Interaction):
        if len(ArisenBotCommon.rpcServers) > 0:
            s = "```"
            s += tabulate.tabulate(ArisenBotCommon.rpcServers, headers=["ID", "Name", "Address", "Port"])
            s += "```"
            await itx.response.send_message(s)
        else:
            await itx.response.send_message("No servers have been added yet.")

    @app_commands.command(name='kick', description="Kick an account from the game server.")
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_1)
    async def server_kick_account(self, itx : discord.Interaction, accountname : str):
        try:
            findResult = ArisenBotCommon.serverGET(ArisenBotCommon.randomServer(), "discord/findplayer", {"AccountName" : accountname})
        except requests.ConnectionError:
            await itx.response.send_message("❌ The server did not respond. It might be down. ❌", ephemeral=True)
            return

        if findResult.status_code == 400:
            await itx.response.send_message(findResult.text)
            return
        
        foundServer = findResult.json()["ServerId"]
        selectedServer = ArisenBotCommon.serverById(foundServer)
        if selectedServer is None:
            await itx.response.send_message("An ArisenBot error has occured.")
            return
        try:
            kickResult = ArisenBotCommon.serverPOST(selectedServer, "discord/kick", {"AccountName" : accountname})
        except requests.ConnectionError:
            await itx.response.send_message("❌ The server did not respond. It might be down. ❌", ephemeral=True)
            return
        
        if kickResult.status_code == 200:
            await itx.response.send_message(f"{accountname} has been kicked from the server.")
        else:
            await itx.response.send_message("An ArisenBot error has occured.")


async def setup(bot):
    await bot.add_cog(ArisenBotServerStatus(bot), guild = discord.Object(id=ArisenBotCommon.GUILD))