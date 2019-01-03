
""
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
from random import randint, choice, SystemRandom
import sqlite3
import logging
import re
import os

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


def getListId():
    f = open("ids.txt", 'r')
    l = []
    for lines in f.readlines():
        l.append(lines)    
    f.close()
    return l
        

def safeData(text):
    str = text.replace("'", " ")
    return str

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

def getWelcomeMessage(server):
    f = "SELECT welcomeMessage FROM server WHERE idServer = '{}'".format(server.id)
    row = executeCommand(f)
    return (row[0][0])

def isWelcomeMP(server):
    f = "SELECT isWelcomeMP FROM server WHERE idServer = '{}'".format(server.id)
    row = executeCommand(f)
    return (row[0][0])

def setWelcomeMessage(server, content):
    f = "UPDATE server SET welcomeMessage = '{}' WHERE idServer = '{}'".format(content, server.id)
    executeCommand(f)

def setIsWelcomeMP(server, a):
    f = "UPDATE server SET isWelcomeMP = {} WHERE idServer = '{}'".format(str(a), server.id)
    executeCommand(f)
    
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
        
def checkIfCreate(directory):
    if not os.path.exists('./classified/{}'.format(directory)):
        os.makedirs('./classified/{}'.format(directory))
    
        
def insertCIA_FILES(idPlayer, serverID):
    f = "INSERT INTO CIA_FILES(idPlayer, idServer) VALUES('{}', '{}')".format(idPlayer, serverID)
    executeCommand(f)
    checkIfCreate(idPlayer)

def deleteCIA_FILES(idPlayer):
    f = "DELETE FROM CIA_FILES WHERE idPlayer = '{}'".format(idPlayer)
    executeCommand(f)

def getCIA_FILES(idServer):
    f = "SELECT idPlayer FROM CIA_FILES WHERE idServer = '{}'".format(idServer)
    rows = executeCommand(f)
    a = list()
    for row in rows:
        a.append(row[0])
    return (a)

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
            f = "INSERT INTO player(idPlayer, name, idServer, authorizationLevel) VALUES('{}', '{}', '{}', 0)".format(idPlayer, name, idServer)
            executeCommand(f)
        else:
            f = "UPDATE player SET name = '{}' WHERE idPlayer = '{}' AND idServer = '{}'".format(name, idPlayer, idServer)
            executeCommand(f)
    except Exception as E:
        print ("Insert Player Exception : ", E)


def insertServer(server):
    idServer = server.id
    f = "SELECT idServer FROM server WHERE idServer = '{}'".format(idServer)
    row = executeCommand(f)
    try:
        if row is False:
            return
        if len(row) == 0:
            f = "INSERT INTO server(welcomeMessage, isWelcomeMP, idServer) VALUES('', 2, '{}')".format(idServer)
            executeCommand(f)
        else:
            return
    except Exception as E:
        print ("Insert Player Exception : ", E)


def getName(idPlayer, idServer):
    f = "SELECT name FROM player WHERE idPlayer = '{}' AND idServer = '{}'".format(idPlayer, idServer)
    row = executeCommand(f)
    try:
        return (row[0][0])
    except:
        return (False)

def getBannedWords(idServer):
    f = "SELECT word FROM bannedWords WHERE idServer = '{}'".format(idServer)
    row = executeCommand(f)
    return (row)

def getEditsWords(idServer):
    f = "SELECT wordBan, wordEdit from editWords WHERE idServer = '{}'".format(idServer)
    row = executeCommand(f)
    wordBan = list()
    editWords = list()
    for truc in row:
        wordBan.append(truc[0])
        editWords.append(truc[1])
    return wordBan, editWords

def inscriptPersonn(idPlayer, idServer):
    f = "select hasWin from player where idPlayer = '{}' and idServer = '{}'".format(idPlayer, idServer)
    row = executeCommand(f)
    row = row[0][0]
    if (row == 1):
        print("Déjà gagné level inscript")
        return 0
    f = "select participating from player where idPlayer = '{}' and idServer = '{}'".format(idPlayer, idServer)
    row = executeCommand(f)
    row = row[0][0]
    print(row)
    if (row == 1):
        return 1
    f = "update player set participating = 1 where idPlayer = '{}' and idServer = '{}'".format(idPlayer, idServer)
    executeCommand(f)
    return 2

def getWinner(idServer):
    f = "select name, idPlayer from player where idServer = '{}' and hasWin = 0 and participating = 1".format(idServer)
    row = executeCommand(f)
    if (len(row) == 0):
        return ("Erreur: il n'y a plus de participants :scream:")
    secure_random = SystemRandom()
    row = secure_random.choice(row)
    f = "update player set hasWin = 1, participating = 1 where idPlayer = '{}' and idServer = '{}'".format(row[1], idServer)
    executeCommand(f)
    return (row[0])

def insertEditWords(idServer, wordBan, wordEdit):
    f = "INSERT INTO editWords(idServer, wordBan, wordEdit) VALUES('{}', '{}', '{}')".format(idServer, wordBan, wordEdit)
    executeCommand(f)

def resetInscription(idServer):
    f = "update player set hasWin = 0, participating = 0 where idServer = '{}'".format(idServer)
    executeCommand(f)
    
def insertBannedWord(idServer, bannedWord):
    f = "INSERT INTO bannedWords(idServer, word) VALUES('{}', '{}')".format(idServer, bannedWord)
    executeCommand(f)

def getListInscrit(idServer):
    f = "SELECT name FROM player WHERE participating = 1 AND hasWin = 0 AND idServer = '{}'".format(idServer)
    rows = executeCommand(f)
    a = "Les inscrit sont: \n"
    for row in rows:
        a += row[0] + '\n'
    return (a)

def lenInscrit(idServer):
    f = "select name, idPlayer from player where idServer = '{}' and hasWin = 0 and participating = 1".format(idServer)
    row = executeCommand(f)
    a = str(len(row))
    return (a)

def playerAddMessage(idPlayer, idServer):
    f =  "select nbMessages from player where idServer = '{}' and idPlayer = '{}'".format(idServer, idPlayer)
    row = executeCommand(f)
    try:
        a = row[0][0]
        a = int(a)
        a = a + 1
        f = "update player set nbMessages = {} where idServer = '{}' and idPlayer = '{}'".format(str(a), idServer, idPlayer)
    except Exception as E:
        pass

def createDirectoryIfDoesNotExist(fileName):
    if not os.path.exists('{}'.format(fileName)):
        os.makedirs('{}'.format(fileName))    

@client.event
async def on_message(message):
    insertPlayer(message)
    insertServer(message.server)
    authorizationLevel = getAuthorizationLevel(message)
    if (client.user.id == message.author.id):
        return

    playerAddMessage(message.author.id, message.server.id)
    LIST_CIA_FILES = getCIA_FILES(message.server.id)
    
    try:
        for ids in LIST_CIA_FILES:
            if (message.author.id == ids):
                createDirectoryIfDoesNotExist('./classified/')
                createDirectoryIfDoesNotExist('./classified/{}'.format(message.author.id))
                with open("./classified/{}/{}.txt".format(message.author.id, message.channel.name), 'a') as f:
                    f.write("\nNEW MESSAGE {}: {}\n".format(str(message.timestamp), message.content))
    except Exception as E:
        print(E)


    if (message.channel.id == "321219792021356549"):
        for attach in message.attachments:
            createDirectoryIfDoesNotExist("./p4x/")
            with open('./p4x/{}.jpg', 'wb') as handle:
                response = requests.get(pic_url, stream=True)
                if not response.ok:
                    pass
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
        return
    
    if (message.content.lower().startswith("!len") and message.channel.id == "423190061170032650"
        and (message.author.id == "193824642304180224" or message.author.id == "164076488294006785"
             or message.author.id == "170580458420174858")):
        await client.send_message(message.channel, "Il y a {} inscrit".format(lenInscrit(message.server.id)))
        return

    if (message.content.lower().startswith("!join")):
        try:
            if message.author.voice.voice_channel is not False:
                if (client.voice_client_in(message.server) is None):
                    await client.join_voice_channel(message.author.voice.voice_channel)
                else:
                    await client.voice_client_in(message.server).disconnect()
                    await client.join_voice_channel(message.author.voice.voice_channel)
        except Exception as E:
            await client.send_message(message.channel, E)

        
    if (message.content.lower().startswith("!reset inscription") and message.channel.id == "423190061170032650"
        and (message.author.id == "193824642304180224" or message.author.id == "164076488294006785" or message.author.id == "170580458420174858")):
        resetInscription(message.server.id)
        await client.send_message(message.channel, "Les inscriptions sont reset mon commandant!")
        return

    if ((message.author.id == "164076488294006785" or message.author.id == "193824642304180224"
         or message.author.id == "170580458420174858") and message.channel.id == "423190061170032650" and message.content.startswith("!list")):
        await client.send_message(message.channel, getListInscrit(message.server.id))
        return
    
    if (message.content.lower().startswith("!inscription") and message.channel.id == "423190061170032650"):
        row = inscriptPersonn(message.author.id, message.server.id)
        if (row == 0):
            await client.send_message(message.channel, "Erreur: tu as déjà gagné, tu ne peux pas te réinscrire!")
            return
        if (row == 1):
            await client.send_message(message.channel, "Erreur: tu es déjà inscrit {}".format(message.author.name))
            return
        await client.send_message(message.channel, "{} est maintenant inscrit!".format(message.author.name))
        return

    if ((message.author.id == "164076488294006785" or message.author.id == "193824642304180224"
         or message.author.id == "170580458420174858") and message.channel.id == "423190061170032650" and message.content.startswith("!roll")):
        name = getWinner(message.server.id)
        await client.send_message(message.channel, name)
        return
    
    if (message.content.lower().startswith("bonjour") and message.channel.id == "411438942613667844"):
        await client.send_message(message.channel, "Bonjour " + message.author.name)
        return

    if (message.content.lower().startswith("salut") and message.channel.id == "411438942613667844"):
        await client.send_message(message.channel, "Salut " + message.author.name)
        return

    if (message.content.lower().startswith("bonsoir") and message.channel.id == "411438942613667844"):
        await client.send_message(message.channel, "Bonsoir " + message.author.name)
        return

    if (message.content.lower().startswith("!me")):
        await client.send_message(message.channel, "Ton compte a été créé le " + str(message.author.created_at))
        return

    if (message.content.lower().startswith('!avatar')):
        await client.send_message(message.channel, str(message.author.avatar_url))
        return
    
    if (message.content.lower().startswith("!ancien")):
        time = message.author.joined_at
        s = "Vous avez rejoint le serveur le " + time.strftime("%Y-%m-%d %H:%M:%S")
        await client.send_message(message.channel, s)

    if (message.content.lower().startswith("!server")):
        nb_member = str(message.server.member_count)
        large = str(message.server.large)
        owner = message.server.owner
        owner = owner.name
        verification_level = str(message.server.verification_level)
        afk_timeout = str(message.server.afk_timeout)
        region = str(message.server.region)
        lroles = message.server.roles
        idServer = message.server.id
        lemojis = len(message.server.emojis)
        name = message.server.name
        created_at = message.server.created_at.strftime("%Y-%m-%d %H:%M:%S")
        s = "Le server a été crée le " + created_at
        s += "\nLe créateur du serveur se nomme: " + owner
        s += "\nCe serveur est large: " + large
        s += "\nIl possède " + nb_member + " membres"
        s += "\nLe serveur est hébergé ici: " + str(region)
        s += "\nIl possède {} roles".format(str(len(lroles)))
        s += "\nSon id est: " + str(idServer)
        s += "\nIl possède {} emojis customs".format(str(lemojis))
        s += "\nEt il possède un niveau de vérification de " + verification_level
        s += "\nIl time out si vous ne parlez pas pendant " + afk_timeout + " s"
        await client.send_message(message.channel, s)
        return
        
    if authorizationLevel < 3:
        return

    if (message.content.lower().startswith("!estimate pruned")):
        if (len(message.content.lower()) > len("!estimate pruned")):
            try:
               nb_days = int(message.content.lower()[len("!estimate pruned "):])
            except Exception as E:
                print(E)
        else:
            nb_days = 7
        try:
            s = await client.estimate_pruned_members(message.server, days=nb_days)
            d = "{} personnes ne se sont pas connectés depuis {} jours".format(str(s), str(nb_days))
        except discord.Forbidden:
            d = "ERROR: KGBot does not have the permission to run this command"
        await client.send_message(message.channel, d)
        
    if (message.content.lower().startswith("!replace ")):
        try:
            print("debut replace")
            message.content = message.content[len("!replace "):]
            tab = message.content.split('|')
            firstWord = tab[0]
            secondWord = tab[1]
            insertEditWords(message.server.id, firstWord, secondWord)
            await client.send_message(message.channel, "Effectué!")
            print("fin replace")
        except Exception as E:
            print(E)
            await client.send_message(message.channel, "usage: !replace badWord|goodWord")
    if (message.content.startswith("!ban ")):
        try:
            print("debut ban")
            tab = message.content.split(' ')
            bannedWord = tab[1]
            insertBannedWord(message.server.id, bannedWord)
            await client.send_message(message.channel, "Effectué!")
            print("fin ban")
        except Exception as E:
            print(E)
            await client.send_message(message.channel, "!usage: !ban badWord")

    if (message.content.startswith("!setLevel ")):
        try:
            print("debut setLevel")
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
            print("fin setLevel")
        except Exception as E:
            print("Exception in setAuthorizationLevel: ", E)
            await client.send_message(message.channel, "Usage: !setAuthorizationLevel idPlayer authorizationLevel")
            return

    if (message.content.lower().startswith("!delete ")):
        idMessage = message.content.lower()[len("!delete "):]
        await client.delete_message(message)
        await client.delete_message(idMessage)
                
        
    if (message.content.lower().startswith("!getname")):
        idServer = message.server.id
        s = ""
        for server in client.servers:
            if (server.id == idServer):
                for users in server.members:
                    s += users.name + "\n"
                break
        print(s)
        with open("./trigger.txt", 'w+') as f:
            f.write(s)
        await client.send_message(message.channel, s)
        return
    
    if (message.content.lower().startswith("!!!purge ")):
        try:
            nbMessage = message.content[len("!!!purge "):]
            nbMessage = int(nbMessage)
        except Exception as E:
            print(E)
            return
        LIST_ID = getListId()
        continuate = False
        for ids in LIST_ID:
            print(message.author.id)
            print(ids)
            print(ids.startswith(message.author.id))
            if (ids.startswith(message.author.id)):
                continuate = True
        if continuate == False:
            s = "La personne " + message.author.name
            s += " a tenté d'utiliser la commande !!!purge le "
            s += str(message.timestamp) + "\n\n"
            with open("traitors.txt", "a") as f:
                f.write(s)
            return
        
        await client.send_message(message.channel, "Are you really Sure?")
        def check(msg):
            if (msg.content == "yes"):
                return True
            return False

        def check2(msg):
            if (msg.content == "azerty"):
                return True
            return False
        message = await client.wait_for_message(check=check)
        await client.send_message(message.channel, "Please enter PassWord: ")
        message = await client.wait_for_message(check=check2)
        await client.purge_from(message.channel, limit=nbMessage)
        await client.send_message(message.channel, "Votre demande de purge a bien été effectuée et a été inscrite au registre des purges. Bonnes journées Commandant!")
    if authorizationLevel < 2:
        return

    if (message.content.lower().startswith("!configure welcomemessage")):
        content = message.content[len("!configure welcomemessage "):]
        setWelcomeMessage(message.server, safeData(content))
        return

    if (message.content.lower().startswith("!configure welcomemp")):
        content = message.content[len("!configure welcomemp "):]
        try:
            content = int(content)
            if (content != 0 and content != 1):
                await client.send_message(message.channel, "Error: You must set welcomeMP to 1 or 0\n")
            else:
                setIsWelcomeMP(message.server, content)
        except:
                await client.send_message(message.channel, "Error: You must set welcomeMP to 1 or 0\n")
        return

    if (message.content.startswith("!emojis")):
        listEmojis = message.server.emojis
        for emo in listEmojis:
            await client.add_reaction(message, emo)
            
    if (message.content.startswith("!cia ")):
        if (message.content.startswith("!cia activate ")):
            idPlayer = message.content[len("!cia activate "):]
            insertCIA_FILES(idPlayer, message.server.id)
        if (message.content.startswith("!cia deactivate ")):
            idPlayer = message.content[len("!cia deactivate"):]
            deleteCIA_FILES(idPlayer)
        if (message.content.startswith("!cia list")):
            s = "La liste des personnes surveillées par la CIA sur ce serveur sont: "
            for ids in LIST_CIA_FILES:
                s += ids
                s += " "
            await client.send_message(message.author, s)
            return

@client.event
async def on_member_join(member):
    mp = isWelcomeMP(member.server)
    if (mp == 2):
        return
    message = getWelcomeMessage(member.server)
    if (mp == 1):
        await client.send_message(member, message)
    else:
        await client.send_message(member.server.default_channel, message)

@client.event
async def on_message_edit(before, after):
    LIST_CIA_FILES = getCIA_FILES(before.server.id)
    for ids in LIST_CIA_FILES:
        if (before.author.id == ids):
            checkIfCreate(before.author.id)
            with open("./classified/{}/{}.txt".format(before.author.id, before.channel.name), 'a') as f:
                f.write("\n--------------------------------------------------------")
                f.write("\nEDIT {} at {}".format(before.author.name, str(before.edited_timestamp)))
                f.write("\nOLD MESSAGE\n:{}".format(before.content))
                f.write("\nNEW MESSAGE\n:{}".format(after.content))
            break
                        
@client.event
async def on_message_delete(message):
    LIST_CIA_FILES = getCIA_FILES(message.server.id)
    for ids in LIST_CIA_FILES:
        if (message.author.id == ids):
            checkIfCreate(message.author.id)
            with open("./classified/{}/{}.txt".format(message.author.id, message.channel.name), 'a') as f:
                f.write("\n--------------------------------------------------------")
                f.write("\nDELETED {} at {}".format(message.author.name, str(time.time())))
                f.write("\nMESSAGE\n:{}".format(message.content))
            break
    
if __name__ == '__main__':
    import sys
    try:
        TOKEN = sys.argv[1]
    except:
        print('USAGE: python3 bot.py TOKENBOT')
        sys.exit(1)
    discord.opus.load_opus("opus")
    if not discord.opus.is_loaded():
            # the 'opus' library here is opus.dll on windows
            # or libopus.so on linux in the current directory
            # you should replace this with the location the
            # opus library is located in and with the proper filename.
            # note that on windows this DLL is automatically provided for you
        print("OPUS NOT LOADED")
        sys.exit(42)
    client.run(TOKEN)
