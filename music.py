import discord
from discord.ext import commands
import youtube_dl
import asyncio
import random

class music(commands.Cog):
	def __init__(self, client):
		self.client = client

	#uma lista que irá conter dicionários com no formato titulo da música : url da música
	music_list = []
	index_actual = 0
	can_repeating = False
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
	force_change = False
	
	@commands.command()
	async def join(self, ctx):
		if ctx.author.voice is None:
			await ctx.send("Entra numa chamada de voz, seu paspalho")
		
		voice_channel = ctx.author.voice.channel
		if ctx.voice_client is None:
			await self.clear(ctx)
			await voice_channel.connect()
		else:
			await self.clear(ctx)
			await ctx.voice_client.move_to(voice_channel)

	@commands.command()
	async def disconnect(self, ctx):
		await self.clear(ctx)
		await ctx.voice_client.disconnect()

	@commands.command()
	async def clear(self, ctx):
		self.music_list.clear()
		await ctx.send("Passei a limpa nessa lista de músicas aqui")

	@commands.command()
	async def play(self, ctx, *args):
		voice_channel = ctx.author.voice.channel

		music_name = ' '.join(args)
		print(music_name)

		if ctx.voice_client is None:
			await self.clear(ctx)
			await voice_channel.connect()
		else:
			await ctx.voice_client.move_to(voice_channel)
		
		YDL_OPTIONS = {'format': "bestaudio", 'default_search': 'auto'}
		voice_client = ctx.voice_client

		with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
			info = ydl.extract_info(music_name, download = False)
			music_title = ''

			if 'entries' in info:
				video_format = info['entries'][0]["formats"][0]
				music_title = info['entries'][0]['title']
			elif 'formats' in  info:
				video_format = info["formats"][0]
				music_title = info.get('title', None)

			stream_url = video_format["url"]
			self.music_list.append({music_title : stream_url})
			
			source = await discord.FFmpegOpusAudio.from_probe(stream_url, **self.FFMPEG_OPTIONS)
			if not voice_client.is_playing():
				voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))

	def get_music_url(self, index):
		music_url = list(self.music_list[index].values())
		return music_url[0]

	@commands.command()
	async def play_next(self, ctx):
		voice_client = ctx.voice_client
		
		"""Verifica se o play_next não foi disparado por uma alteração da lista forçada
		como prev, next, jump pois nesses eventos ele não deve adicionar mais 1 no índice da lista"""

		if not self.force_change:
			if self.can_repeating == True and self.index_actual + 1 > len(self.music_list) - 1:
				self.index_actual = 0
				url = self.get_music_url(self.index_actual)
			else:	
				url = self.get_music_url(self.index_actual + 1)
				self.index_actual += 1

		self.force_change = False

		source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)
		voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))

	@commands.command()
	async def remove(self, ctx, pos_remove):
		try:
			pos_remove = int(pos_remove)
			self.music_list.pop(pos_remove - 1)
		except:
			await ctx.send("Tu botou uma música que não existe meu peixe, bota direito da próxima vez.")
	
	async def playing_forced_music(self, ctx, stream_url, voice_client):
		self.force_change = True

		source = await discord.FFmpegOpusAudio.from_probe(stream_url, **self.FFMPEG_OPTIONS)
		voice_client.stop()
		voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))

	@commands.command()
	async def prev(self, ctx):
		voice_client = ctx.voice_client

		try:
			if voice_client.is_playing():
				
				if self.can_repeating == True and self.index_actual - 1 < 0:
					self.index_actual = len(self.music_list) - 1
					stream_url = self.get_music_url(self.index_actual)
				else:
					stream_url = self.get_music_url(self.index_actual - 1)
					self.index_actual -= 1

				if self.index_actual < 0:
					self.index_actual = 0
					await ctx.send("A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a  reprodução anterior, filho da puta.")
					return
				
				await self.playing_forced_music(ctx, stream_url, voice_client)
		except:
			await ctx.send("Tem nenhuma música tocando não seu mula, como que eu vou dar previous?")

	@commands.command()
	async def next(self, ctx):
		voice_client = ctx.voice_client

		try:
			if voice_client.is_playing():
				
				try:
					if self.can_repeating == True and self.index_actual + 1 > len(self.music_list) - 1:
						self.index_actual = 0
						stream_url = self.get_music_url(self.index_actual)
					else: 
						stream_url = self.get_music_url(self.index_actual + 1)
						self.index_actual += 1
				except:
					await ctx.send("A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a seguinte reprodução, filho da puta.")
					return

				await self.playing_forced_music(ctx, stream_url, voice_client)
		except:
			await ctx.send("Tem nenhuma música tocando não seu mula, como que eu vou dar next?")

	@commands.command()
	async def repeat(self, ctx):
		self.can_repeating = not self.can_repeating
		await ctx.send(f"Tou aprendendo inglês, a pergunta é estou tocando em looping? A resposta é {self.can_repeating}")

	@commands.command()
	async def jump(self, ctx, index_jump):
		if index_jump is None:
			ctx.send("Tu é jegue? Bota um número ae pra eu saber pra qual música pular bixo")
			return

		index_jump = int(index_jump) - 1
		if index_jump < 0:
			index_jump = 0 
		voice_client = ctx.voice_client

		try:
			stream_url = self.get_music_url(index_jump)
			self.index_actual = index_jump
		except:
			await ctx.send("Tu botou uma música que não existe, olha a lista de novo e bota direito da próxima vez.")
			return
		await self.playing_forced_music(ctx, stream_url, voice_client)
		
	@commands.command()
	async def shuffle(self, ctx):
		random.shuffle(self.music_list)
		await ctx.send("A playlist foi bagunçada com sucesso, meu peixe")

	@commands.command()
	async def q(self, ctx):
		index_in_list = 0
		list_musics = ''

		#music_list colocará em music um dicionário contendo o título da música
		#e a sua url, mas na listagem só necessitamos do título, logo pegamos esse dicionário
		#coletamos o set de chave dele e transformamos em list para pegar o primeiro elemento dessa list
		for music in self.music_list:
			music_name = list(music.keys())

			list_musics += f"{index_in_list + 1}. {music_name[0]}\n"
			index_in_list += 1

		if list_musics == '':
			await ctx.send("Tem nenhuma música na lista, adiciona uma pra esse comando deixar de ser inútil")
			return

		await ctx.send(list_musics)

	@commands.command()
	async def pause(self, ctx):
		try:
			ctx.voice_client.pause()
			await ctx.send("PAUSEI ESSA CARAIA")
		except:
			await ctx.send("Tem nenhuma música tocando não seu mula")
	
	@commands.command()
	async def resume(self, ctx):
		try:
			ctx.voice_client.resume()
			await ctx.send("RESUMEI ESSA CARAIA")
		except:
			await ctx.send("Tem nenhuma música tocando não seu mula")

	@commands.command()
	async def stop(self, ctx):		
		try:
			ctx.voice_client.stop()
			await ctx.send("ESTOPEI ESSA CARAIA")
		except:
			await ctx.send("Tu quer estopar o que seu mula?")

def setup(client):
	client.add_cog(music(client))