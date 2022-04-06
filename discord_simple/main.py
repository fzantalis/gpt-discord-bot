#########################
# DISCORD SETTINGS
#########################
  
import os
import discord.ext
from discord.ext import commands

# Loading our discord env variables
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
client = commands.Bot(command_prefix = "!")

# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@client.event
async def on_ready():
  guild = discord.utils.get(client.guilds, name=GUILD)
  print(
    f'{client.user} is connected to the following guild:\n'
    f'{guild.name}(id: {guild.id})'
  )

# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@client.event
async def on_message(message):

  if message.author == client.user:
    return

  await message.channel.send("Hey!")

# EXECUTES THE BOT WITH THE LOADED TOKEN. 
client.run(TOKEN)
