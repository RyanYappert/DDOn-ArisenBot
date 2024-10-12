from typing import List
import discord
import ArisenBotCommon, tabulate, requests, datetime
from discord.ext import commands
from discord import app_commands
from enum import Enum

class LobbyChatMsgType(Enum):
    # Say = 0
    # Shout = 1
    # Tell = 2
    # System = 3
    # Party = 4
    ShoutAll = 5
    # Group = 6
    # Clan = 7
    # Entryboard = 8
    ManagementGuideChat = 9
    ManagementGuideNotice = 10
    ManagementAlertChat = 11
    ManagementAlertNotice = 12
    ClanNotice = 13

class ArisenBotChat(commands.GroupCog, name = "chat"):
    def __init__(self, bot):
        self.bot = bot
        self.chatName = ["John", "Dogma"]
        self.chatType = LobbyChatMsgType.ManagementGuideChat

    @app_commands.command(name='type', description = "Set chat type. Leave blank to list.")
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_1)
    async def chat_type(self, itx : discord.Interaction, type : str = ""):
        if not type:
            s = "```"
            table = []
            for val in LobbyChatMsgType:
                # s += f"{val.name}\t{val.value}\n"
                table.append([val.name, val.value])
            s += tabulate.tabulate(table, headers = ["Type", "Value"])
            s += "```"
            s += f'\n The current chat type is `{self.chatType.name}`'
            await itx.response.send_message(s, ephemeral=True)
        else:
            try:
                vali = int(type)
                if vali in LobbyChatMsgType:
                    self.chatType = LobbyChatMsgType(vali)
                    await itx.response.send_message(f"Chat mode set to {self.chatType.name}.")
                else:
                    await itx.send_message("Invalid chat message type.", ephemeral=True)
            except ValueError:
                if type in LobbyChatMsgType.__members__.keys():
                    self.chatType = LobbyChatMsgType[type]
                    await itx.response.send_message(f"Chat mode set to {self.chatType.name}.")
                else:
                    await itx.response.send_message("Invalid chat message type.", ephemeral=True)

    @chat_type.autocomplete('type')
    async def chat_type_autocomplete(
            self,
            itx: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        types = list(LobbyChatMsgType.__members__.keys())
        return [
            app_commands.Choice(name=val, value=val)
            for val in types if current.lower() in val.lower()
        ]
    
    @app_commands.command(name='name', description = "Set active chat name.")
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_1)
    async def set_chat_name(self, itx : discord.Interaction, name : str = None):
        if name is None:
            await itx.response.send_message(f'Chat name is currently "{self.chatName[0]} {self.chatName[1]}".')
        else:
            nameSplit = name.split(' ')
            first = len(nameSplit) > 0 and nameSplit[0] or ""
            last = len(nameSplit) > 1 and nameSplit[1] or ""
            self.chatName = [first, last]
            await itx.response.send_message(f"Chat name set to {first} {last}.")

    def makeChat(self, message : str) -> dict:
        chatMessage = {
            "HandleId" : 0,
            "Type": self.chatType.value,
            "MessageFlavor" : 0,
            "PhrasesCategory" : 0,
            "PhrasesIndex": 0,
            "Message": message,
            "Deliver": True
        }

        chatEntry = {
            "DateTime" : datetime.datetime.now().isoformat(),
            "FirstName" : self.chatName[0],
            "LastName" : self.chatName[1],
            "CharacterId" : 0,
            "ChatMessage" : chatMessage
        }

        return chatEntry

    @app_commands.command(name='send', description = "Send a message to a single channel.")
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_1)
    @app_commands.autocomplete(id = ArisenBotCommon.server_autocomplete)
    async def send_chat(self, itx : discord.Interaction, id : int, message : str):
        server = ArisenBotCommon.serverById(id)
        if server is None:
            await itx.response.send_message(f"❌ Message failure for {server[0]}; invalid server id. ❌", ephemeral=True)
        chatEntry = self.makeChat(message)
        try:
            result = ArisenBotCommon.serverPOST(server, "chat", chatEntry)
            await itx.response.send_message(f"Message sent to {server[1]} ({server[0]}).\n`{message}`")
        except requests.exceptions.ConnectionError:
            await itx.response.send_message(f"❌ Message failure for {server[0]}; connection error. ❌", ephemeral=True)

    @app_commands.command(name='sendall', description = "Send a message to all channels.")
    @app_commands.checks.has_any_role(*ArisenBotCommon.AUTH_LEVEL_1)          
    async def send_all(self, itx : discord.Interaction, message : str):
        chatEntry = self.makeChat(message)
        responseLog = []
        for server in ArisenBotCommon.rpcServers:
            try:
                result = ArisenBotCommon.serverPOST(server, "chat", chatEntry)
                if result.status_code == 201:
                    responseLog.append(f"Message sent to {server[1]} ({server[0]}).")
                else:
                    responseLog.append(f"❌ Message failure for {server[1]} ({server[0]}). ❌")
            except requests.exceptions.ConnectionError:
                responseLog.append(f"❌ Message failure for {server[1]} ({server[0]}). ❌")
        responseString = "\n".join(responseLog) + f"\n`{message}`"
        await itx.response.send_message(responseString)

async def setup(bot):
    await bot.add_cog(ArisenBotChat(bot), guild = discord.Object(id=ArisenBotCommon.GUILD))