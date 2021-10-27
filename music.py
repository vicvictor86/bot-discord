import discord
from discord.ext import commands
import youtube_dl

class music(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def join(self, ctx):
		if ctx.author.voice is None:
			await ctx.send("Entra numa chamada de voz seu paspalho")
		voice_channel = ctx.author.voice.channel
		if ctx.voice_client is None:
			await voice_channel.connect()
		else:
			await ctx.voice_client.move_to(voice_channel)

	@commands.command()
	async def disconnect(self, ctx):
		await ctx.voice_client.disconnect()

	
	list_of_music = []
	index_actual = 0

	@commands.command()
	async def play(self, ctx, *args):
		voice_channel = ctx.author.voice.channel

		url = ' '.join(args)
		print(url)

		if ctx.voice_client is None:
			await voice_channel.connect()
		else:
			await ctx.voice_client.move_to(voice_channel)
			
		FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
		YDL_OPTIONS = {'format': "bestaudio", 'default_search': 'auto'}
		vc = ctx.voice_client

		with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
			info = ydl.extract_info(url, download = False)

			if 'entries' in info:
				video_format = info['entries'][0]["formats"][0]
			elif 'formats' in  info:
				video_format = info["formats"][0]

			stream_url = video_format["url"]
			self.list_of_music.append(stream_url)
			print(self.list_of_music)

			source = await discord.FFmpegOpusAudio.from_probe(stream_url, **FFMPEG_OPTIONS)
			
			if not vc.is_playing():
				vc.play(source)

	@commands.command()
	async def previous(self, ctx):
		vc = ctx.voice_client

		if vc.is_playing():
			
			stream_url = self.list_of_music[self.index_actual - 1]
			self.index_actual -= 1

			if self.index_actual < 0:
				self.index_actual = 0
				await ctx.send("A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a seguinte reprodução, filho da puta.")
				return

			print(self.index_actual)
			
			FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
			source = await discord.FFmpegOpusAudio.from_probe(stream_url, **FFMPEG_OPTIONS)
			
			vc.stop()
			vc.play(source)
		else:
			await ctx.send("Tem nenhuma música tocando não seu mula, como que eu vou dar previous?")

	@commands.command()
	async def next(self, ctx):
		vc = ctx.voice_client

		if vc.is_playing():
			
			try:
				stream_url = self.list_of_music[self.index_actual + 1]
				self.index_actual += 1
			except:
				await ctx.send("A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a seguinte reprodução, filho da puta.")
				return

			FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
			source = await discord.FFmpegOpusAudio.from_probe(stream_url, **FFMPEG_OPTIONS)
			vc.stop()
			vc.play(source)
		else:
			await ctx.send("Tem nenhuma música tocando não seu mula, como que eu vou dar next?")

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

def setup(client):
	client.add_cog(music(client))