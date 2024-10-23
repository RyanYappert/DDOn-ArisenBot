# bot.py
import os, base64, requests, random, csv, discord
from typing import List
from dotenv import load_dotenv
from discord import app_commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('DISCORD_GID'))

USERNAME = os.getenv('DDON_USERNAME')
PASSWORD = os.getenv('DDON_PASSWORD')
ENCODEDIDENTITY = base64.b64encode(bytes(f"{USERNAME}:{PASSWORD}", 'utf-8'))
REQUEST_HEADERS = {"Authorization" : f"Basic {ENCODEDIDENTITY.decode('utf-8')}"}

AUTH_LEVEL_0 = ['Clan Master']
AUTH_LEVEL_1 = AUTH_LEVEL_0 + ['Moderator', 'Dev']
AUTH_LEVEL_2 = AUTH_LEVEL_1 + ['Arisen']

rpcServers = []

ARISENBOT_SERVER_CSV = os.getenv('ARISENBOT_SERVER_CSV')
if (ARISENBOT_SERVER_CSV is not None and len(ARISENBOT_SERVER_CSV) > 0):
    with open(ARISENBOT_SERVER_CSV, mode = 'r') as f:
        csvFile = csv.reader(f)
        next(csvFile, None)
        for line in csvFile:
            id = int(line[0])
            name = line[1]
            addr = line[2].strip()
            port = int(line[3])
            rpcServers.append([id, name, addr, port])

def serverPrint(server):
    return f"{server[1]} ({server[0]}): {serverRoute(server, '')}"

def serverRoute(server, route):
    return f"http://{server[2]}:{server[3]}/rpc/{route}"

def serverPOST(server, route, data = {}):
    url = serverRoute(server, route)
    return requests.post(url, json = data, headers = REQUEST_HEADERS)

def serverGET(server, route, params = {}):
    url = serverRoute(server, route)
    return requests.get(url, params = params, headers = REQUEST_HEADERS)

def serverDELETE(server, route, params = {}):
    url = serverRoute(server, route)
    return requests.delete(url, params = params, headers = REQUEST_HEADERS)

def randomServer():
    return random.choice(rpcServers)

def serverById(id: int):
    for server in rpcServers:
        if server[0] == id:
            return server

async def server_autocomplete(itx : discord.Interaction, 
                              current : int) -> List[app_commands.Choice[int]]:
    values = [i[:2] for i in rpcServers]
    print(values)
    return [
        app_commands.Choice(name = i[1], value = i[0])
        for i in values
    ]