from datetime import datetime, timedelta
import requests
import enum
import discord
import ast


with open("savedhashmap.txt", "r") as file:
    readfile = file.read()
    if readfile == "":
        clashhashmap = {}
    else:
        clashhashmap = ast.literal_eval(readfile)

with open("savedrolehashmap.txt", "r") as file:
    readfile = file.read()
    if readfile == "":
        roleshashmap = {}
    else:
        roleshashmap = ast.literal_eval(readfile)

with open("datestringdict.txt", "r") as file:
    readfile = file.read()
    if readfile == "":
        datestringdict = {'datestring': "DATE NOT SET"}
    else:
        datestringdict = ast.literal_eval(readfile)

def get_clash(apikey):
    url= 'https://euw1.api.riotgames.com/lol/clash/v1/tournaments?api_key='+apikey
    response = requests.get(url)
    return response.json

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

def register_gamer(name, saturday, sunday):
    clashhashmap[name] = (Response(saturday).value, Response(sunday).value)
    with open("savedhashmap.txt", "w") as file:
        file.write(str(clashhashmap))
    return f"{name} was succesfully registered!"

class YesOrNo(str, enum.Enum):
    Yes = 0
    No = 1

def set_roles(name, top, jungle, mid, adc, support, fill):
    roles = []
    if top == YesOrNo.Yes:
        roles.append("top")
    if jungle == YesOrNo.Yes:
        roles.append("jungle")
    if mid == YesOrNo.Yes:
        roles.append("mid")
    if adc == YesOrNo.Yes:
        roles.append("adc")
    if support == YesOrNo.Yes:
        roles.append("support")
    if fill == YesOrNo.Yes:
        roles.append("fill")

    with open("savedrolehashmap.txt", "w") as file:
        rolesString = "/".join(roles)
        roleshashmap[name] = rolesString
        file.write(str(roleshashmap))
        return f"{name}'s roles were successfully set to {rolesString}!"
    return "Failed to set roles!"

def is_clash_mod(roles):
    for role in roles:
        if role.name == 'Clash Mod':
            return True
    return False

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
        with open("datestringdict.txt", "w") as file:
            file.write(str(datestringdict))
        await message.channel.send("Successfully set the date.")

async def removec(message):
    if str(message.author.name) == 'åke' or str(message.author.name) == 'tvåke':
        t = message.content
        x = t.split()
        #x[1] is removed
        if x[1] in clashhashmap and x[1] in roleshashmap:
            del clashhashmap[x[1]]
            del roleshashmap[x[1]]
            with open("savedhashmap.txt", "w") as file:
                file.write(str(clashhashmap))
            with open("savedrolehashmap.txt", "w") as file:
                file.write(str(roleshashmap))
            await message.channel.send(x[1] + ' were successfully removed from clashhashmap and rolehashmap')

        elif x[1] in clashhashmap and x[1] not in roleshashmap:
            del clashhashmap[x[1]]
            with open("savedhashmap.txt", "w") as file:
                file.write(str(clashhashmap))
            await message.channel.send(x[1] + ' were successfully removed from clashhashmap')

        elif x[1] in roleshashmap and x[1] not in clashhashmap:
            del roleshashmap[x[1]]
            with open("savedrolehashmap.txt", "w") as file:
                file.write(str(roleshashmap))
            await message.channel.send(x[1] + ' were successfully removed from rolehashmap')

        else:
            await message.channel.send("they are not in the lists.")

    else:
        await message.channel.send("you dont have the authorities for this command bitch")

def clear_clash(inter: discord.Interaction):
    if not is_clash_mod(inter.user.roles):
        return "you dont have the authorities for this command bitch"
    
    dt = datetime.now()
    weekday = dt.isoweekday()
    if weekday > 3:
        sat = dt + timedelta(days= 6 - weekday)
        sun = dt + timedelta(days= 7 - weekday)
        datestringdict['datestring'] = f"{sat.day}th of {sat.strftime('%B')} and {sun.day}th of {sun.strftime('%B')}"
        with open("datestringdict.txt", "w") as file:
            file.write(str(datestringdict))
    for key in list(clashhashmap.keys()):
        del clashhashmap[key]
    with open("savedrolehashmap.txt", "w") as file:
        file.write(str(roleshashmap))

    return "Successfully cleared the list."