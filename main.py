import os
import discord 
from keep_alive import keep_alive
import music
import chat
from discord.ext import commands

cogs = [music, chat]

#client = discord.Client()
client = commands.Bot(command_prefix='$', intents = discord.Intents.all())

for i in range(len(cogs)):
	cogs[i].setup(client)

keep_alive()
client.run(os.environ['TOKEN'])