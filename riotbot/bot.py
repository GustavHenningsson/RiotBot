import discord
from discord import app_commands
import requests
import operator
import time
import ast
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import enum





load_dotenv()
MY_GUILD = discord.Object(os.environ['GUILD'])

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.current_voice_channel = None

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()
client = MyClient(intents=intents)


#client = discord.Client()
id = 704740604340338759
#id = 704704351268110346
listofppl =[]
datestringdict = {}
apikey= os.environ['RIOT_API_KEY']

#read file
f = open("savedhashmap.txt", "r")
readfile = f.read()
if readfile == "":
    clashhashmap = {}
else:
    clashhashmap = ast.literal_eval(readfile)
f.close()

f = open("savedrolehashmap.txt", "r")
readfile = f.read()
if readfile == "":
    roleshashmap = {}
else:
    roleshashmap = ast.literal_eval(readfile)
f.close()

f = open("datestringdict.txt", "r")
readfile = f.read()
if readfile == "":
    datestringdict = {'datestring': "DATE NOT SET"}
else:
    datestringdict = ast.literal_eval(readfile)

f.close()


def get_clash():
    url= 'https://euw1.api.riotgames.com/lol/clash/v1/tournaments?api_key='+apikey
    response = requests.get(url)
    return response.json


def get_encryptedid(name, server):
    url= 'https://'+server+'.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+name+'?api_key='+apikey
    response = requests.get(url)
    return response.json()["id"]

def get_rankedshit(name, server):
    url='https://'+server+'.api.riotgames.com/lol/league/v4/entries/by-summoner/'+get_encryptedid(name, server)+'?api_key='+apikey
    response = requests.get(url)
    return response.json()

def get_rankedrank(name, server):
    r = get_rankedshit(name, server)
    for i in range(0, len(r)):
        if r[i]["queueType"]=='RANKED_SOLO_5x5':
            info = r[i]
            tier = info["tier"]
            rank = info["rank"]
            lp = info["leaguePoints"]
            return (name, tier, rank, lp)
        else:
            pass


def sortrank(list):
    pointlist = []
    for i in range(0, len(list)):
        p = int(list[i][3])
        if list[i][1]=='BRONZE':
            p = p + 400
        if list[i][1]=='SILVER':
            p = p + 800
        if list[i][1]=='GOLD':
            p = p + 1200
        if list[i][1]=='PLATINUM':
            p = p + 1600
        if list[i][1]=='DIAMOND':
            p = p + 2000
        elif list[i][1] == 'MASTER' or list[i][1]=='GRANDMASTER' or list[i][1]=='CHALLENGER':
            p = p + 2400
        if list[i][2]=='III':
            p = p+100
        if list[i][2]=='II':
            p = p+200
        if list[i][2]=='I':
            p = p+300
        pointlist.append((list[i], p))

    pointlist.sort(key=operator.itemgetter(1), reverse=True)
    ret = []
    for i in range(0, len(pointlist)):
        ret.append(str(i+1) + '. '+pointlist[i][0][0]+ ' '+pointlist[i][0][1]+ ' ' +pointlist[i][0][2] + ' '+ str(pointlist[i][0][3])+ 'LP')

    return ret

def stringtoint(str):
    if str == "yes":
        return 3
    if str == "no":
        return 0
    if str == "maybe":
        return 1
    if str == "fill":
        return 2

def inttostring(int):
    if int == 3:
        return "yes"
    if int == 0:
        return "no"
    if int == 1:
        return "maybe"
    if int == 2:
        return "fill"
    

class Response(enum.Enum):
    Yes = 3
    No = 0
    Maybe = 1
    Fill = 2


def build_view_message():
    resultstring1 ="Gamers available on Saturday: \n"
    resultstring2 = "\nGamers available on Sunday: \n"

    gamersOnSaturday = {
        Response.Yes.value: [],
        Response.Fill.value: [],
        Response.Maybe.value: [],
        Response.No.value: [],
    }
    gamersOnSunday = {
        Response.Yes.value: [],
        Response.Fill.value: [],
        Response.Maybe.value: [],
        Response.No.value: [],
    }
    longestGamer = 0
    for gamer, available in clashhashmap.items():
        if len(gamer) > longestGamer:
            longestGamer = len(gamer)
        gamersOnSaturday.get(available[0]).append(gamer)
        gamersOnSunday.get(available[1]).append(gamer)

    def add_to_string(response, gamer):
        role = roleshashmap.get(gamer, "No role specified yet")
        spacesRole = " " * (10 - len(Response(response).name))
        spaceGamer = " " * (longestGamer - len(gamer) + 5)
        return Response(response).name + ":" + spacesRole + gamer + spaceGamer + role + '\n'

    for response, gamers in gamersOnSaturday.items():
        for gamer in gamers:
            resultstring1 += add_to_string(response, gamer)

    for response, gamers in gamersOnSunday.items():
        for gamer in gamers:
            resultstring2 += add_to_string(response, gamer)


    saturdaynumberstring = f"Saturday: {len(gamersOnSaturday[Response.Yes.value])} + ({len(gamersOnSaturday[Response.Fill.value])}) \n" 
    sundaynumberstring = f"Sunday: {len(gamersOnSunday[Response.Yes.value])} + ({len(gamersOnSunday[Response.Fill.value])}) \n"
    
    return ("Clash for " + datestringdict['datestring'] + ".\n" + "\n" + resultstring1 + saturdaynumberstring + resultstring2 + sundaynumberstring)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

def register_gamer(name, saturday, sunday):
    clashhashmap[name] = (Response(saturday).value, Response(sunday).value)
    f = open("savedhashmap.txt", "w")
    f.write(str(clashhashmap))
    f.close()
    return f"{name} was succesfully registered!"

@client.tree.command(description="Register for the upcoming Clash tournament")
async def register(inter: discord.Interaction, saturday: Response, sunday: Response):
    await inter.response.send_message(register_gamer(inter.user.display_name, saturday, sunday))

@client.tree.command(description="View registered players")
async def view(inter: discord.Interaction):
    await inter.response.send_message(build_view_message())

class YesOrNo(str, enum.Enum):
    Yes = 0
    No = 1

def set_roles(name, mid, top, jungle, adc, support, fill):
    roles = []
    if mid == YesOrNo.Yes:
        roles.append("mid")
    if top == YesOrNo.Yes:
        roles.append("top")
    if jungle == YesOrNo.Yes:
        roles.append("jungle")
    if adc == YesOrNo.Yes:
        roles.append("adc")
    if support == YesOrNo.Yes:
        roles.append("support")
    if fill == YesOrNo.Yes:
        roles.append("fill")

    with open("savedrolehashmap.txt", "w") as f:
        rolesString = "/".join(roles)
        roleshashmap[name] = rolesString
        f.write(str(roleshashmap))
        f.close()
        return f"{name}'s roles were successfully set to {rolesString}!"
    return "Failed to set roles!"

@client.tree.command(description="Register your roles")
async def role(inter: discord.Interaction, mid: YesOrNo, top: YesOrNo, jungle: YesOrNo, adc: YesOrNo, support: YesOrNo, fill: YesOrNo):
    await inter.response.send_message(set_roles(inter.user.display_name, mid, top, jungle, adc, support, fill))

def is_clash_mod(roles):
    for role in roles:
        if role.name == 'Clash Mod':
            return True
    return False

@client.tree.command(description="Clears the clash list")
async def clearclash(inter: discord.Interaction):

    if not is_clash_mod(inter.user.roles):
        await inter.response.send_message("you dont have the authorities for this command bitch")
        return
    
    dt = datetime.now()
    weekday = dt.isoweekday()
    if weekday > 3:
        sat = dt + timedelta(days= 6 - weekday)
        sun = dt + timedelta(days= 7 - weekday)
        datestringdict['datestring'] = f"{sat.day}th of {sat.strftime('%B')} and {sun.day}th of {sun.strftime('%B')}"
        f = open("datestringdict.txt", "w")
        f.write(str(datestringdict))
        f.close()
    for key in list(clashhashmap.keys()):
        del clashhashmap[key]
    f = open("savedhashmap.txt", "w")
    f.write(str(clashhashmap))
    f.close()
    await inter.response.send_message("Successfully cleared the list.")


async def register(message):
    t = message.content
    x = t.split()
    ##TODO: check if player already is in list and if player exists/has rank.
    if len(x)>1:
        x.remove(x[0])
        j = "".join(x)
        listofppl.append(j)
        await message.channel.send(" ".join(x) + ' has been successfully registered')
    else:
        await message.channel.send('Specify a name after the command')

async def participants(message):
    await message.channel.send(listofppl)

async def commands(message):
    await message.channel.send('To register, type !clash (yes, maybe, no or fill on saturday/yes, maybe, no or fill on sunday) without the parenthesis AND NO CAPITAL LETTERS. fill = I can play if we need another player. THE / IS VERY IMPORTANT AND IT DIVIDES YOUR REGISTER INTO SATURDAY AND SUNDAY IN THE PROGRAM.\n An example would be "!clash yes/no" \n This would mean that I am available on saturday but not on sunday.\n !view to view which gamers that are available.')

async def clash(message):
    t = message.content
    x = t.split()
    x = x[1].split("/")
    #x[0] = yes
    #x[1] = no
    if len(x)!= 2:
        #else do not register
        await message.channel.send(str(message.author.name) + ' was not successfully registered. Please describe your availability using yes, no, maybe or fill only with no caps. See !commands.' )
    else:

        if (x[0] == 'yes' or x[0] == 'no' or x[0] == 'maybe' or x[0] == 'fill') and (x[1] == 'yes' or x[1] == 'no' or x[1] == 'maybe' or x[1] == 'fill'):
            #adds to hashmap if the register is using the keywords
            clashhashmap[message.author.name] = (stringtoint(x[0]), stringtoint(x[1]))
            await message.channel.send(str(message.author.name) +  ' was successfully registered.')
            f = open("savedhashmap.txt", "w")
            f.write(str(clashhashmap))
            f.close()
        else:
            #else do not register
            await message.channel.send(str(message.author.name) + ' was not successfully registered. Please describe your availability using yes, no, maybe or fill only with no caps. See !commands.' )

async def standings(message):
    k = []
    for i in listofppl:
        k.append(get_rankedrank(i, 'euw1'))
    sortedk = sortrank(k)
    s = ""
    for i in range(0, len(sortedk)):
        s = s+ "\n" + sortedk[i]
    await message.channel.send(s)

async def remove(message):
    t = message.content
    x = t.split()
    if len(x)>1:
        listofppl.remove(x[1])
        await message.channel.send(x[1]+ ' has been successfully removed')
    else:
        await message.channel.send('Specify a name after the command')

async def commandsDEFUNCT(message):
    await message.channel.send('!register to register a summoner. \n!unregister to unregister a summoner. \n!standings to show the ranked solo standings. \n!participants to view participants (faster than !standings). \n!hello for !hello.')

async def view(message):
    resultstring1 ="Gamers available on saturday: \n"
    resultstring2 = "\nGamers available on sunday: \n"
    listnumberhashmapsaturday = {}
    listnumberhashmapsunday = {}

    saturdaynumberstring = "Saturday: "
    sundaynumberstring = "Sunday: "
    #adds to string in a nice order
    for j in range(3, -1, -1):
        listnumberhashmapsaturday[j] = 0
        listnumberhashmapsunday[j] = 0
        for i in clashhashmap:
            if clashhashmap[i][0] == j:
                if i in roleshashmap:
                    resultstring1 = resultstring1 + (i + ":     " + inttostring(clashhashmap[i][0]) + '      ' + str(roleshashmap[i][0])+ '\n')
                else:
                    resultstring1 = resultstring1 + (i + ":     " + inttostring(clashhashmap[i][0]) + '      No roles specified yet.' +'\n')
                listnumberhashmapsaturday[j] +=1
            if clashhashmap[i][1]==j:
                if i in roleshashmap:
                    resultstring2 = resultstring2 + (i + ":     " + inttostring(clashhashmap[i][1]) + '      ' + str(roleshashmap[i][0]) + '\n')
                else:
                    resultstring2 = resultstring2 + (i + ":     " + inttostring(clashhashmap[i][1]) + '      No roles specified yet.' +'\n')
                listnumberhashmapsunday[j] +=1
    #send out the message
    await message.channel.send("Clash for " + datestringdict['datestring'] + ".\n" + resultstring1 + saturdaynumberstring +  str(listnumberhashmapsaturday[3]) + " + ("+ str(listnumberhashmapsaturday[2]) + ")\n"+ resultstring2 + sundaynumberstring +  str(listnumberhashmapsunday[3]) + " + ("+ str(listnumberhashmapsunday[2]) + ")")


async def cya(message):
    if str(message.author.name) == 'åke' or str(message.author.name) == 'tvåke':
        await message.channel.send("cya!")
        quit()
    else:
        await message.channel.send("you dont have the authorities for this command bitch")

async def setdate(message):
    if str(message.author.name) == 'åke' or str(message.author.name) == 'tvåke' or str(message.author.name) == 'Oliver':
        t = message.content
        x = t.split()
        x = x[1:]
        datestring = ""
        for i in range(0, len(x)):
            datestring += x[i] + " "
        datestring[:-1]
        datestringdict['datestring'] = datestring
        f = open("datestringdict.txt", "w")
        f.write(str(datestringdict))
        f.close()
        await message.channel.send("Successfully set the date.")

async def removec(message):
    if str(message.author.name) == 'åke' or str(message.author.name) == 'tvåke':
        t = message.content
        x = t.split()
        #x[1] is removed
        if x[1] in clashhashmap and x[1] in roleshashmap:
            del clashhashmap[x[1]]
            del roleshashmap[x[1]]
            f = open("savedhashmap.txt", "w")
            f.write(str(clashhashmap))
            f.close()
            f = open("savedrolehashmap.txt", "w")
            f.write(str(roleshashmap))
            f.close()
            await message.channel.send(x[1] + ' were successfully removed from clashhashmap and rolehashmap')

        elif x[1] in clashhashmap and x[1] not in roleshashmap:
            del clashhashmap[x[1]]
            f = open("savedhashmap.txt", "w")
            f.write(str(clashhashmap))
            f.close()
            await message.channel.send(x[1] + ' were successfully removed from clashhashmap')

        elif x[1] in roleshashmap and x[1] not in clashhashmap:
            del roleshashmap[x[1]]
            f = open("savedrolehashmap.txt", "w")
            f.write(str(roleshashmap))
            f.close()
            await message.channel.send(x[1] + ' were successfully removed from rolehashmap')

        else:
            await message.channel.send("they are not in the lists.")

    else:
        await message.channel.send("you dont have the authorities for this command bitch")

@client.event
async def on_message(message):
    global lecon
    id=client.get_guild(704740604340338759)
    #Non-clash stuff
    if False:
        if message.content.startswith('!hello'):
            await message.channel.send('hello')

        if message.content.startswith('!register'):
            await register(message)

        if message.content == '!participants':
            await participants(message)

        if message.content =='!standings':
            await standings(message)

        if message.content.startswith('!remove'):
            await remove(message)

        if message.content == '!commands':
            await commands(message)


    if message.content == '!commands':
        await commands(message)

    #clash stuff
    if message.content.startswith('!clash'):
        await clash(message)

    if message.content.startswith('!view'):
        await view(message)

    if message.content.startswith('!role'):
        await role(message)

    if message.content == '!cya':
        await cya(message)

    if message.content.startswith('!clearclash'):
        await clearclash(message)

    if message.content.startswith("!setdate"):
        await setdate(message)

    if message.content.startswith('!removec'):
        await removec(message)




client.run(os.environ['BOT_TOKEN'])
