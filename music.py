import discord
from discord.ext import commands
import youtube_dl
import asyncio
import random


class music(commands.Cog):
    def __init__(self, client):
        self.client = client

    # uma lista que irá conter dicionários com no formato titulo da música : url da música, "tamanho_musica" : tamanho
    # da música
    music_list = []
    index_actual = 0
    can_repeating = False
    FFMPEG_OPTIONS = {
        'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    force_change = False

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await self.embed_with_one_line(
                ctx, "Entra numa chamada de voz, seu paspalho")

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await self.clear(ctx)
            await voice_channel.connect()
        else:
            await self.clear(ctx)
            await ctx.voice_client.move_to(voice_channel)
        await self.embed_with_one_line(ctx, "FALA RAPAIZE, CHEGUEI")

    @commands.command()
    async def disconnect(self, ctx):
        await self.clear(ctx)
        await ctx.voice_client.disconnect()

    @commands.command()
    async def clear(self, ctx, coming_play=False):
        self.music_list.clear()
        if not coming_play:
            await self.embed_with_one_line(
                ctx, "Passei a limpa nessa lista de músicas aqui")

    async def embed_add_song(self, ctx, url, music_title):
        embed = discord.Embed(
            title=f"{ctx.author.display_name} adicionou uma música",
            url=f"{url}",
            description=f"A música colocada foi {music_title}",
            color=0x054f77)
        await ctx.send(embed=embed)

    async def playing_in_channel(self, ctx, url, music_title, voice_client):
        source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)
        if not voice_client.is_playing():
            voice_client.play(source,
                              after=lambda e: asyncio.run_coroutine_threadsafe(
                                  self.play_next(ctx), self.client.loop))

    def define_music_info(self, info):
        url = info.get("url", None)
        music_title = info.get('title', None)

        lenght_info = int(info.get("duration"))
        lenght_minutes = int(lenght_info / 60)
        lenght_seconds = int(lenght_info % 60)
        lenght = f"{lenght_minutes}:{lenght_seconds}"

        self.music_list.append({music_title: url, "music_lenght": lenght})
        return url, music_title

    @commands.command(aliases=["p"])
    async def play(self, ctx, *args):
        voice_channel = ctx.author.voice.channel
        is_playlist = False

        music_name = ' '.join(args)
        print(music_name)

        if "list" in music_name:
            is_playlist = True

        if ctx.voice_client is None:
            await self.clear(ctx, True)
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

        YDL_OPTIONS = {
            'format': "bestaudio",
            'default_search': 'auto',
            'noplaylist': is_playlist
        }
        voice_client = ctx.voice_client

        if is_playlist:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                ydl.cache.remove()
                info = ydl.extract_info(music_name, download=False)
                url = info.get("url", None)
                music_title = info.get("title", None)

            is_playlist = False

            await self.embed_add_song(ctx, url, music_title)
            await self.playing_in_channel(ctx, url, music_title, voice_client)

        YDL_OPTIONS = {
            'format': "bestaudio",
            'default_search': 'auto',
            'noplaylist': is_playlist
        }
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            #ydl.cache.remove()
            info = ydl.extract_info(music_name, download=False)

            music_title = ''

            if 'entries' in info:
                for music_info in info["entries"]:
                    url, music_title = self.define_music_info(music_info)
            elif 'formats' in info:
                url, music_title = self.define_music_info(info)

            await self.embed_add_song(ctx, url, music_title)
            await self.playing_in_channel(ctx, url, music_title, voice_client)

    def get_music_url(self, index):
        music_url = list(self.music_list[index].values())
        return music_url[0]

    def get_music_name(self, index):
        music_name = list(self.music_list[index].keys())
        return music_name[0]

    def jump_to_next_music(self):
        if self.can_repeating and self.index_actual + 1 > len(self.music_list) - 1:
            self.index_actual = 0
            url = self.get_music_url(self.index_actual)
        else:
            url = self.get_music_url(self.index_actual + 1)
            self.index_actual += 1

        return url

    @commands.command()
    async def play_next(self, ctx):
        voice_client = ctx.voice_client
        """Verifica se o play_next não foi disparado por uma alteração da lista forçada
        como prev, next, jump pois nesses eventos ele não deve adicionar mais 1 no índice da lista"""

        url = ""
        if not self.force_change:
            url = self.jump_to_next_music()

        self.force_change = False
        source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)
        voice_client.play(source,
                          after=lambda e: asyncio.run_coroutine_threadsafe(
                              self.play_next(ctx), self.client.loop))

        next_music_name = self.get_music_name(self.index_actual)
        embed = discord.Embed(
            title=f"A música que está tocando agora é {next_music_name}",
            url=f"{url}",
            description="SOLTA O SOM DJ",
            color=0x054f77)
        await ctx.send(embed=embed)

    async def embed_with_one_line(self, ctx, execution):
        text_embed = execution

        embed = discord.Embed(title=text_embed,
                              url="",
                              description="",
                              color=0x054f77)

        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, pos_remove):
        try:
            pos_remove = int(pos_remove)

            music_name = self.get_music_name(pos_remove - 1)
            url = self.get_music_url(pos_remove - 1)

            self.music_list.pop(pos_remove - 1)

            embed = discord.Embed(
                title=f"A música {music_name} foi removida com sucesso ",
                url=f"{url}",
                description="prende o som dj",
                color=0x054f77)
            await ctx.send(embed=embed)
        except:
            await self.embed_with_one_line(ctx, "Tu botou uma música que não existe meu peixe, bota direito da próxima vez.")

    async def playing_forced_music(self, ctx, url, voice_client):
        self.force_change = True

        source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)
        voice_client.stop()
        voice_client.play(source,
                          after=lambda e: asyncio.run_coroutine_threadsafe(
                              self.play_next(ctx), self.client.loop))

    async def embed_forced_music(self, title, url, description, ctx):
        music_name = self.get_music_name(self.index_actual)

        title = title + f" {music_name}"
        embed = discord.Embed(title=title,
                              url=f"{url}",
                              description=description,
                              color=0x054f77)
        await ctx.send(embed=embed)

    @commands.command()
    async def prev(self, ctx):
        voice_client = ctx.voice_client

        try:
            if voice_client.is_playing():
                if self.can_repeating and self.index_actual - 1 < 0:
                    self.index_actual = len(self.music_list) - 1
                    url = self.get_music_url(self.index_actual)
                else:
                    url = self.get_music_url(self.index_actual - 1)
                    self.index_actual -= 1

                if self.index_actual < 0:
                    self.index_actual = 0
                    await self.embed_with_one_line(ctx, "A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a reprodução anterior, filho da puta.")
                    return

                await self.embed_forced_music(
                    "Tou dando um passo pá trás para a música", url,
                    "VOLTA UMA MÚSICA DJ", ctx)
                await self.playing_forced_music(ctx, url, voice_client)
        except:
            await self.embed_with_one_line(ctx, "Tem nenhuma música tocando não seu mula, como que eu vou dar previous?")

    @commands.command(aliases=["n"])
    async def next(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            try:
                url = self.jump_to_next_music()
                await self.embed_forced_music("Tou dando um passo pá frente para música", url,"SEGUE UMA MÚSICA DJ", ctx)
            except:
                await self.embed_with_one_line(ctx, "A fila de músicas não contém conteúdos músicais suficientes para que eu possa pular para a seguinte reprodução, filho da puta.")
                return
            await self.playing_forced_music(ctx, url, voice_client)
        else:
            await self.embed_with_one_line(ctx, "Tem nenhuma música tocando não seu mula, como que eu vou dar next?")

    @commands.command()
    async def repeat(self, ctx):
        self.can_repeating = not self.can_repeating
        await self.embed_with_one_line(ctx, f"Tou aprendendo inglês, a pergunta é estou tocando em looping? A resposta é {self.can_repeating}")

    @commands.command()
    async def jump(self, ctx, index_jump):
        if index_jump is None:
            await self.embed_with_one_line(ctx, "Tu é jegue? Bota um número ae pra eu saber pra qual música pular bixo")
            return

        index_jump = int(index_jump) - 1
        if index_jump < 0:
            index_jump = 0
        voice_client = ctx.voice_client

        try:
            url = self.get_music_url(index_jump)
            self.index_actual = index_jump
        except:
            await self.embed_with_one_line(ctx, "Tu botou uma música que não existe, olha a lista de novo e bota direito da próxima vez.")
            return

        await self.embed_forced_music("Tou dando um pulo pá algum lugar para a música", url, "SALTA A MÚSICA DJ", ctx)
        await self.playing_forced_music(ctx, url, voice_client)
        self.stop_music = False

    @commands.command()
    async def shuffle(self, ctx):
        random.shuffle(self.music_list)
        await self.embed_with_one_line(ctx, "A playlist foi bagunçada com sucesso, meu peixe")

    @commands.command(aliases=["queue"])
    async def q(self, ctx):
        index_in_list = 0
        list_musics = ''

        # music_list colocará em music um dicionário contendo o título da música
        # e a sua url, mas na listagem só necessitamos do título, logo pegamos esse dicionário
        # coletamos o set de chave dele e transformamos em list para pegar o primeiro elemento dessa list
        for music in self.music_list:
            music_name = list(music.keys())

            list_musics += f"{index_in_list + 1}. {music_name[0]} ({music['music_lenght']})\n"
            index_in_list += 1

        if list_musics == '':
            await self.embed_with_one_line(ctx, "Tem nenhuma música na lista, adiciona uma pra esse comando deixar de ser inútil")
            return

        embed = discord.Embed(
            title=
            "Lista de músicas:\nAbaixo toda a demonstração do seu péssimo gosto",
            url="",
            description=list_musics,
            color=0x054f77)
        await ctx.send(embed=embed)

    async def embed_control_music(self, ctx, execution):
        text_embed = execution + " ESSA CARAIA"

        embed = discord.Embed(title=text_embed,
                              url="",
                              description="",
                              color=0x054f77)

        await ctx.send(embed=embed)

    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await self.embed_control_music(ctx, "PAUSEI")
        else:
            await self.embed_with_one_line(
                ctx, "Tem nenhuma música tocando não seu mula")

    stop_music = False

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.voice_client
        if not self.stop_music and not voice_client.is_playing():
            voice_client.resume()
            await self.embed_control_music(ctx, "RESUMEI")
        elif voice_client.is_playing():
            await self.embed_with_one_line(ctx, "A música já ta tocando ou por acaso você não percebeu?")
        else:
            await self.embed_with_one_line(ctx, "A música da estopada amigo não posso fazer nada")

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            self.stop_music = True
            await self.embed_control_music(ctx, "ESTOPEI")
        else:
            await self.embed_with_one_line(ctx, "Tu quer estopar o que seu mula?")


def setup(client):
    client.add_cog(music(client))
