import discord
from discord.ext import commands
import random

class chat(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def oi(self, ctx):
		await ctx.send("Fala meu peixe")
	
	@commands.command()
	async def xlr8(self, ctx):
		await ctx.send(file=discord.File("Images/xlr8.jpg"))
	
	@commands.command()
	async def heloa(self, ctx):
		await ctx.send("Cara chato")
	
	@commands.command()
	async def av(self, ctx):
		seq = ["Cadê o cabo", "Av tixão miquinha", "GTX 1660", "Main evelyn e akali ao mesmo tempo kkk"]
		choice_made = random.choice(seq)
		await ctx.send(choice_made)

def setup(client):
	client.add_cog(chat(client))