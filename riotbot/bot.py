import discord
from discord import app_commands
import ast
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from helpers import *

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

apikey= os.environ['RIOT_API_KEY']

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

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.tree.command(description="Register for the upcoming Clash tournament")
async def register(inter: discord.Interaction, saturday: Response, sunday: Response):
    await inter.response.send_message(register_gamer(clashhashmap, inter.user.display_name, saturday, sunday))

@client.tree.command(description="View registered players")
async def view(inter: discord.Interaction):
    await inter.response.send_message(build_view_message(clashhashmap, roleshashmap, datestringdict))

@client.tree.command(description="Register your roles")
async def role(inter: discord.Interaction, mid: YesOrNo, top: YesOrNo, jungle: YesOrNo, adc: YesOrNo, support: YesOrNo, fill: YesOrNo):
    await inter.response.send_message(set_roles(roleshashmap, inter.user.display_name, mid, top, jungle, adc, support, fill))

@client.tree.command(description="Clears the clash list")
async def clearclash(inter: discord.Interaction):
    await inter.response.send_message(clear_clash(datestringdict, clashhashmap, inter))

client.run(os.environ['BOT_TOKEN'])