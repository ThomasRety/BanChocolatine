import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from random import randint, choice
import sqlite3
import logging
import re


Client = discord.Client(command_prefix="")
client = commands.Bot(command_prefix="")

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)



IA = "Isabel [IA]#6016"
dbPath = "./database/data.db"

############################################################################################################################################
########################################################### IA #############################################################################
############################################################################################################################################

def safeData(text):
    a = ""
    b = re.compile("[^']").findall(text)
    for letter in b:
        a += letter
    return a

def executeCommand(f):
    global dbPath
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    try:
        c.execute(f)
    except sqlite3.OperationalError as E:
        print("Requete plante", f)
        print(E)
        return (False)
    row = c.fetchall()
    conn.commit()
    conn.close()
    return (row)

def setAuthorizationLevel(idServer, idPlayer, authorizationLevel):
    f = "UPDATE player SET authorizationLevel = {} WHERE idPlayer = '{}' AND idServer = '{}'".format(str(authorizationLevel), idPlayer, idServer)
    executeCommand(f)

def getAuthorizationLevel(message):
    serverId = message.server.id
    idPlayer = message.author.id
    f = "SELECT authorizationLevel FROM player WHERE idServer = '{}' AND idPlayer = '{}'".format(serverId, idPlayer)
    row = executeCommand(f)
    if (row == False) or len(row) == 0:
        return (False)
    try:
        return (row[0][0])
    except Exception as E:
        print(E)

def insertPlayer(message):
    idPlayer = message.author.id
    name = message.author.name
    name = safeData(name)
    idServer = message.server.id
    f = "SELECT name FROM player where idPlayer = '{}' AND idServer = '{}'".format(idPlayer, idServer)
    row = executeCommand(f)
    try:
        if row is False:
            return
        if len(row) == 0:
            f = "INSERT INTO player(idPlayer, name, idServer) VALUES('{}', '{}', '{}')".format(idPlayer, name, idServer)
            executeCommand(f)
        else:
            f = "UPDATE player SET name = '{}' WHERE idPlayer = '{}' AND idServer = '{}'".format(name, idPlayer, idServer)
            executeCommand(f)
    except Exception as E:
        print ("Insert Player Exception : ", E)


def getName(idPlayer, idServer):
    f = "SELECT name FROM player WHERE idPlayer = '{}' AND idServer = '{}'".format(idPlayer, idServer)
    row = executeCommand(f)
    try:
        return (row[0][0])
    except:
        return (False)

def getBannedWord(idServer):
    f = "SELECT word FROM bannedWords WHERE idServer = '{}'".format(idServer)
    row = executeCommand(f)
    return (row)

def getEditsWords(idServer):
    f = "SELECT wordBan, wordEdit from editWords WHERE idServer = '{}'".format(isServer)
    row = executeCommand(f)
    wordBan = list()
    editWords = list()
    for truc in row:
        wordBan.append(truc[0])
        editWords.append(truc[1])
    return wordBan, editWords

@client.event
async def on_message(message):
    insertPlayer(message)
    authorizationLevel = getAuthorizationLevel(message)
        
    bannedWords = getBannedWords(message.server)
    editWord1, editWord2 = getEditsWords(message.server)
    for word in bannedWords:
        if word in message.content.lower():
            client.delete_message(message)
            return
    i = 0
    while (i < len(editWord1)):
        if editWord1[i] in message.content.lower():
            position = message.content.find(word)
            message.content = message.content[0: position] + editWord2[i] + message.content[position + len(editWord1[i]):]
            client.edit_message(message, message.content)


    if authorizationLevel < 3:
        return
    if (message.content.startswith("!replace ")):
        try:
            message.content = message.content[len("!replace "):]
            tab = message.content.split('|')
            firstWord = tab[0]
            secondWord = tab[1]
            insertWordReplaced(message.server.id, firstWord, secondWord)
        except:
            client.send_message(message.channel, "usage: !replace badWord|goodWord")
    if (message.content.startswith("!ban ")):
        try:
            tab = message.content.split(' ')
            bannedWord = tab[1]
            insertBannedWord(bannedWord)
        except:
            client.send_message(message.channel, "!usage: !ban badWord")
    if (message.content.startswith("!setLevel ")):
        try:
            tab = message.content.lower().split(' ')
            idPlayer = safeData(tab[1])
            clientName = getName(idPlayer, message.server.id)
            if not clientName:
                await client.send_message(message.channel, "Erreur, l'usager n'existe pas!")                
            newAuth = int(safeData(tab[2]))
            if newAuth > 4 or newAuth < 0:
                await client.send_message(message.channel, "Erreur: le level d'autorisation doit-être compris entre 0 et 4.")
                return
            setAuthorizationLevel(message.server.id, idPlayer, newAuth)
            await client.send_message(message.channel, "L'user {} a maintenant un level d'accréditation : {}".format(clientName, str(newAuth)))
        except Exception as E:
            print("Exception in setAuthorizationLevel: ", E)
            await client.send_message(message.channel, "Usage: !setAuthorizationLevel idPlayer authorizationLevel")
            return
            
    
if __name__ == '__main__':
    import sys
    try:
        TOKEN = sys.argv[1]
    except:
        print('USAGE: python3 bot.py TOKENBOT')
        sys.exit(1)
    client.run(TOKEN)
