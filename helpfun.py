import discord
from discord.ext import commands

class helpfun(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def helpf(self, ctx, command = None):
		if command is None:
			embed = discord.Embed(title = "Lista de comandos, clique aqui para saber mais", url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ", description = "Tens o que é necessário para esmagares meu comando? Para saber sobre comandos específicos use $helpf nomedocomando", color = 0x054f77)

			embed.set_author(name= ctx.author.display_name, url = "https://www.youtube.com/watch?v=-wZl_ZhnVg4", icon_url = ctx.author.avatar_url)

			embed.set_thumbnail(url = "https://i.pinimg.com/564x/ff/8c/1b/ff8c1ba11a5fcb16835297f3b7c55d1f.jpg")

			embed.add_field(name = "Comandos musicais", value = "play, next, prev, remove, repeat, clear, jump, shuffle, q, pause, resume, stop.", inline = False)
			embed.add_field(name = "Comandos de canal de voz", value = "join, disconnect")
			embed.add_field(name = "Comandos de interação", value = "oi, heloa, av")
			embed.add_field(name = "Comandos de imagem", value = "xlr8, sonicputo", inline = False)
			
			await ctx.send(embed = embed)
		else:
			await ctx.send("Comando específico")

def setup(client):
	client.add_cog(helpfun(client))