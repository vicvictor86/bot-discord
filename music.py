import discord
from discord.ext import commands
import youtube_dl
import asyncio

class music(commands.Cog):
	def __init__(self, client):
		self.client = client

	list_of_music = []
	informations_of_music = []
	index_actual = 0
	can_repeating = False
	FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

	@commands.command()
	async def join(self, ctx):
		if ctx.author.voice is None:
			await ctx.send("Entra numa chamada de voz seu paspalho")
		voice_channel = ctx.author.voice.channel

		if ctx.voice_client is None:
			self.clear()
			await voice_channel.connect()
		else:
			self.clear()
			await ctx.voice_client.move_to(voice_channel)

	@commands.command()
	async def disconnect(self, ctx):
		self.clear()
		await ctx.voice_client.disconnect()

	@commands.command()
	async def clear(self):
		self.list_of_music.clear()

	@commands.command()
	async def play(self, ctx, *args):
		voice_channel = ctx.author.voice.channel

		music_name = ' '.join(args)
		print(music_name)

		if ctx.voice_client is None:
			self.clear()
			await voice_channel.connect()
		else:
			await ctx.voice_client.move_to(voice_channel)
		
		YDL_OPTIONS = {'format': "bestaudio", 'default_search': 'auto'}
		vc = ctx.voice_client

		with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
			info = ydl.extract_info(music_name, download = False)

			if 'entries' in info:
				video_format = info['entries'][0]["formats"][0]
				self.informations_of_music.append(info['entries'][0]['title'])
			elif 'formats' in  info:
				video_format = info["formats"][0]
				self.informations_of_music.append(info.get('title', None))

			stream_url = video_format["url"]
			self.list_of_music.append(stream_url)
			
			source = await discord.FFmpegOpusAudio.from_probe(stream_url, **self.FFMPEG_OPTIONS)
			if not vc.is_playing():
				vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))

	@commands.command()
	async def play_next(self, ctx):
		voice_client = ctx.voice_client

		url = self.list_of_music[self.index_actual + 1]
		self.index_actual += 1

		source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)
		voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))

	@commands.command()
	async def remove(self, ctx, pos_remove):
		try:
			pos_remove = int(pos_remove)
			self.list_of_music.pop(pos_remove - 1)			
			self.informations_of_music.pop(pos_remove - 1)
		except:
			await ctx.send("Tu botou uma música que não existe meu peixe, bota direito da próxima vez.")

	@commands.command()
	async def prev(self, ctx):
		voice_client = ctx.voice_client

		try:
			if voice_client.is_playing():
				
				if self.can_repeating == True and self.index_actual - 1 < 0:
					self.index_actual = len(self.list_of_music) - 1
					stream_url = self.list_of_music[self.index_actual]
				else:
					stream_url = self.list_of_music[self.index_actual - 1]
					self.index_actual -= 1

				if self.index_actual < 0:
					self.index_actual = 0
					await ctx.send("A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a  reprodução anterior, filho da puta.")
					return

				source = await discord.FFmpegOpusAudio.from_probe(stream_url, **self.FFMPEG_OPTIONS)
				
				voice_client.stop()
				voice_client.play(source)
		except:
			await ctx.send("Tem nenhuma música tocando não seu mula, como que eu vou dar previous?")

	@commands.command()
	async def next(self, ctx):
		voice_client = ctx.voice_client

		try:
			if voice_client.is_playing():
				
				try:
					if self.can_repeating == True and self.index_actual + 1 > len(self.list_of_music) - 1:
						self.index_actual = 0
						stream_url = self.list_of_music[self.index_actual]
					else: 
						stream_url = self.list_of_music[self.index_actual + 1]
						self.index_actual += 1
						

				except:
					await ctx.send("A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a seguinte reprodução, filho da puta.")
					return

				source = await discord.FFmpegOpusAudio.from_probe(stream_url, **self.FFMPEG_OPTIONS)
				voice_client.stop()
				voice_client.play(source)
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
		elif index_jump > len(self.list_of_music):
			await ctx.send("Amigo, olhe a lista de novo, bota direito")
		voice_client = ctx.voice_client

		try:
			if voice_client.is_playing():
				
				try:
					stream_url = self.list_of_music[index_jump]
					self.index_actual = index_jump
				except:
					await ctx.send("Tu botou uma música que não existe meu peixe, bota direito da próxima vez.")
					return

				source = await discord.FFmpegOpusAudio.from_probe(stream_url, **self.FFMPEG_OPTIONS)
				voice_client.stop()
				voice_client.play(source)
		except:
			await ctx.send("Tem nenhuma música tocando não seu mula, como que eu vou dar jump?")
			
	@commands.command()
	async def q(self, ctx):
		index_in_list = 0
		list_musics = ''

		for music in self.list_of_music:
			list_musics += f"{index_in_list + 1}. {self.informations_of_music[index_in_list]}\n"
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