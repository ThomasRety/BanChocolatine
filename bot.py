import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from random import randint, choice
import sqlite3
import logging

Client = discord.Client()
client = commands.Bot()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@client.event
async def on_ready():
    global VERSION
    print("Isabel Online")
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))
    print("VERSION: {}".format(VERSION))
    old = getOldVersion()
    if VERSION != old:
        for servers in client.servers:
            await client.send_message(servers, "Isabel est maintenant en version: " + VERSION)
    print("======================================")

IA = "Isabel [IA]#6016"

############################################################################################################################################
########################################################### IA #############################################################################
############################################################################################################################################

@client.event
async def on_message(message):
    if "chocolatine" in message.content.lower():
        client.delete_message(message)
        client.send_message(message.channel, "Ne prononcez pas ce mot!")
    


if __name__ == '__main__':
    import sys
    try:
        TOKEN = sys.argv[1]
    except:
        print('USAGE: python3 bot.py TOKENBOT')
        sys.exit(1)
    client.run(TOKEN)
