import os
import discord 
from keep_alive import keep_alive
import music
import chat
import helpfun
from discord.ext import commands

cogs = [music, chat, helpfun]

client = commands.Bot(command_prefix='$', intents = discord.Intents.all(), case_insensitive = True, help_command = None)

for i in range(len(cogs)):
	cogs[i].setup(client)

keep_alive()
client.run(os.environ['TOKEN'])