import discord
from discord import app_commands
import os
from dotenv import load_dotenv
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

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.tree.command(description="Register for the upcoming Clash tournament")
async def register(inter: discord.Interaction, saturday: Response, sunday: Response):
    await inter.response.send_message(register_gamer(inter.user.display_name, saturday, sunday))

@client.tree.command(description="View registered players")
async def view(inter: discord.Interaction):
    await inter.response.send_message(build_view_message())

@client.tree.command(description="Register your roles")
async def role(inter: discord.Interaction, top: YesOrNo, jungle: YesOrNo, mid: YesOrNo, adc: YesOrNo, support: YesOrNo, fill: YesOrNo):
    await inter.response.send_message(set_roles(inter.user.display_name, top=top, jungle=jungle, mid=mid, adc=adc, support=support, fill=fill))

@client.tree.command(description="Clears the clash list")
async def clearclash(inter: discord.Interaction):
    await inter.response.send_message(clear_clash(inter))

client.run(os.environ['BOT_TOKEN'])