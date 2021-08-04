TOKEN = os.getenv("DISCORD_TOKEN")
import discord
from SimpleEconomy import Seco
from discord import Member
from random import choice
from asyncio import TimeoutError, sleep
from discord import Embed,File
import requests
from random import randint
from itertools import cycle
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure
import sys 
import math
from lib.util.util import convert
import os 
from data import *
import youtube_dl
from dotenv import load_dotenv
import datetime
from pretty_help import DefaultMenu, PrettyHelp
import typing
import random
import json
import aiosqlite
import time
import re
import asyncio
import logging


default_prefix = "a"
async def prefix_handler(bot,message):
    if message.guild:
        guild=await seco.get("prefixes",guild_id=message.guild.id)
        if guild==None:

            await seco.insert("prefixes",guild_id=message.guild.id,prefix=default_prefix)
            return default_prefix
        else:
            return guild["prefix"]
    else:
        return default_prefix


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=prefix_handler, intents=intents)

async def status_task():
    while True:
        await bot.change_presence(activity=discord.Streaming(name="ahelp", url="https://twitch.tv/laiptwitch"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Streaming(name="ahelp prefix", url="https://twitch.tv/laiptwitch"))
        await asyncio.sleep(10)
        await bot.change_presence(activity=discord.Streaming(name="Default Prefix is 'a'!", url="https://twitch.tv/laiptwitch"))
        await asyncio.sleep(10)
        

seco=Seco(bot,"veNQgwEJOATEeRj7TOPgpn8uCvTOUduU7kRRkjueeoNop5RpRXt3qimDpyCvEch2","myeconomydata",logs=True, def_bal=100, def_bank=400) 


@bot.command()
@has_permissions(manage_messages=True)
async def prefix(ctx,new_prefix:str):
    if ctx.guild:
        await seco.update("prefixes",{"prefix":new_prefix},guild_id=ctx.guild.id)
        ell=discord.Embed(
            title="Prefix set",
            description=f"Your new prefix is: {new_prefix}"
        )
        await ctx.send('@everyone')
        await ctx.send(embed=ell)
    else:
        ell=discord.Embed(
            title="Prefix cannot be set",
            description=f"This prefix only works in guilds"
        )
        await ctx.send(embed=ell)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    bot.loop.create_task(status_task())


@bot.event
async def on_member_join(member):
    try:
        channel = bot.get_channel('854551881803759617')
        try:
            embed2 = discord.Embed(colour=discord.Colour.green())
            embed2.set_author(name=member.name, icon_url=member.avatar_url)
            embed2.add_field(name="Welcome" , value=f"**Hey,{member.mention}! Welcome to {member.guild.name}\nI hope you enjoy your stay here!\nThanks for joining**", inline=False)
            embed2.set_thumbnail(url=member.guild.icon_url)
            await bot.channel.send(embed=embed2)
        except Exception as e:
            raise e
    except Exception as e:
        raise e

@bot.event
async def on_member_remove(member):
    try:
        channel = bot.get_channel('854556791383654421')
        guild = bot.get_guild(123123123123123123)

        for guild in bot.guilds:
            print(guild)
            print(guild.id)
        try:
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.add_field(name="Good Bye!", value=f"**{member.mention} just left\nServer - **"+guild+"**\nServer ID - **"+guild.id, inline=False)
            embed.set_thumbnail(url=member.guild.icon_url)
            await bot.channel.send(embed=embed)
        except Exception as e:
            raise e
    except Exception as e:
        raise e

async def connect_db():
    connection = await aiosqlite.connect("leveling.db")
    
    # for postgresql
    # import asyncpg # Import in the begining of the file
    # connection = await asyncpg.connect(user='username', password='password', database='database_name', host='localhost')
    
    bot.db = connection

# Setup db for leveling
# As we assinged the database connection variabled named `db` that will be used for database
# Now set environment variable named `DISLEVEL_DB_CONN` and set value to the name of the variable assigned to the bot which is `db`
# Note : Connection must be made using aiosqlite for SQLite databse and asyncpg for PostgreSQL
os.environ['DISLEVEL_DB_CONN'] = 'db'


bot.loop.run_until_complete(connect_db())

# Loading the cog/extension so we can use the functionality
bot.load_extension('dislevel')

menu = DefaultMenu('◀️', '▶️', '❌') # You can copy-paste any icons you want.
bot.help_command = PrettyHelp(navigation=menu, color=12745742) 
# The color can be whatever you want, including normal color codes, 
# I just like the discord green personally.

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Now playing',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Duration', value=self.source.duration)
                 .add_field(name='Requested by', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send('Not connected to any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100')

        ctx.voice_state.volume = volume / 100
        await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if not ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if not ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Viewing page {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('Nothing being played at the moment.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')


    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, search: str):
        """Plays a song.
        If there are songs in the queue, this will be queued until the
        other songs finished playing.
        This command automatically searches from various sites
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('An error occurred while processing this request: {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {}'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        if round(bot.latency * 1000) <= 50:
            embed=discord.Embed(title="PING", description=f":ping_pong: PingPongPingPongPingPongPingPong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=10070709)
        elif round(bot.latency * 1000) <= 100:
            embed=discord.Embed(title="PING", description=f":ping_pong: PingPongPingPongPingPong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=2895667)
        elif round(bot.latency * 1000) <= 200:
            embed=discord.Embed(title="PING", description=f":ping_pong: PingPongPingPongPingPong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=16777215)
        else:
            embed=discord.Embed(title="PING", description=f":ping_pong: PingPongPingPongPingPongPingPong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=1752220)
        print(str)
        await ctx.send(embed=embed)
        await ctx.message.add_reaction(emoji='✅')

mainshop = [{"name":"Watch","price":100,"description":"Time"},
            {"name":"Laptop","price":1000,"description":"Work"},
            {"name":"PC","price":10000,"description":"Gaming"},
            {"name":"Ferrari","price":99999,"description":"Sports Car"}]

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["bal"])
    async def balance(self, ctx):
        balance=await seco.get_balance(ctx.author.id)
    
        e=discord.Embed(
        title="Balance",
        description=f"Your balance is: {balance}",
        color=15844367)
        e.set_footer(text="Requested by Someone!")
        await ctx.send(embed=e)

    @commands.command(aliases=["bk"])
    async def bank(self, ctx):
        balance=await seco.get_bank(ctx.author.id)
    
        eb=discord.Embed(
        title="Bank",
        description=f"Your Bank balance is: {balance}",
        color=15844367)
        eb.set_footer(text="Requested by Someone!")
        await ctx.send(embed=eb)

    @commands.command(aliases=["give"])
    async def send(self, ctx, id, amount):
        userid = ctx.author.id
        to = id
        await seco.transfer_balance(userid, to, amount)
        transfer=discord.Embed(title="Transfer Successful!", description="Your transfer was successful! The amount you requested for transferring has been transferred!")
        await ctx.send(embed=transfer)

    @commands.command()
    async def beg(self, ctx):
        beg_list=["ELon Musk donated to you ","You got lucky and got ", "Alston V. Abraham (The Generous) donated to you"]
        amount=random.randint(0,100)
        text=random.choice(beg_list) + str(amount) +"€"
        await seco.add_balance(ctx.author.id,amount)
        e=discord.Embed(
        title="Begged",
        description=text
        )
        await ctx.send(embed=e)

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx):
        leaderboard=await seco.leaderboard()
        print(leaderboard)
        text=""
        for person in leaderboard:
            text+=str(leaderboard.index(person)+1) +") "+bot.get_user(int(person["userid"])).display_name+" - "+str(person["balance"])+"\n"

            e=discord.Embed(
            title="Leaderboard",
            description=text
            )
            await ctx.send(embed=e)
    
    @commands.command()
    async def shop(self, ctx):
        shop=discord.Embed(
        title="Shop - Items Can Be Bought",
        description=f"1) Cookies - 50$\n2) Blob - 10000$\n3) Cheese - 2$"
        )
        await ctx.send(embed=shop)

    @commands.command()
    async def items(self, ctx):
        user=await seco.get("shop",userid=ctx.author.id)
        if user==None:
            await seco.insert("shop",userid=ctx.author.id,cookies=0,blob=0,cheese=0)
            user=await seco.get("shop",userid=ctx.author.id)

        cookies=user["cookies"]
        blob=user["blob"]
        cheese=user["cheese"]
        await ctx.send(f"Cookies: {cookies}\nBlob: {blob}\nCheese: {cheese}")
    @commands.command()
    async def buy(self, ctx, item: str):
        prices={"cookies":50,"blob":10000, "cheese":2}
        b=await seco.get_balance(ctx.author.id)
        price=prices[item.lower()]
        #checking if item is in the dict
        if not item.lower() in prices.keys():
            await ctx.send("No such item is on sale!")
            return

            
        if b >= price:
            await seco.remove_balance(ctx.author.id,price)

            user=await seco.get("shop",userid=ctx.author.id)
            if user==None:

                user_items={"cookies":0,"blob":0, "cheese":0}
                user_items[item.lower()]=1

                await seco.insert("shop",userid=ctx.author.id,**user_items)
                await ctx.send("Purchase was succesful!")

            else:
                await seco.update("shop",{item.lower():user[item.lower()]+1})
                await ctx.send("Purchase was succesful!")

        else:
            await ctx.send("You don't have enough money!")
    @commands.command(aliases=["bet", "gamble"])
    async def slots(self, ctx, amount:int):
        pp =await seco.get_balance(ctx.author.id)                                                                     
        # Get message author's balance from online DB
        double = amount * 2                                                                                               
        # Amount of earnings to showcase from doubling
        quadwin = amount *3                                                                                               
        # Amount of earnings to add from quadrupling
        quad = amount * 4                                                                                                 
        # Amount of earnings to showcase from quadrupling
        if amount <= 0:                                                                                                   
            # You cannot gamble any amount lower than 1
            return await ctx.send("You can't gamble with less than **1** monie!")
        if pp == 0:                                                                                                  
            # You cannot gamble if you have no monies
            return await ctx.send("You can't gamble with less than **1** monie!")
        if pp < amount :                                                                                             
            # You cannot gamble over your balance
            await ctx.send("Oops, looks like you don't have enough monies to gamble this amount!") 
        else:
            choice=random.randint(1,100)                                                                                  
            # Random number from 1 to 100
            if choice == 100:                                                                                             
                # If choice is 100 you win a jackpot
                await seco.add_balance(ctx.author.id,100000)                                                             
                # Add jackpot to balance
                tt=discord.Embed(title="You won!",                                                                     
                # Send an embed announcing the win
                                description="Congratulations! You hit the jackpot of **100,000** monies!", 
                                color=discord.Color.green())
                tt.add_field(name="** **", value="🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉", inline=False)
                await ctx.send(embed=tt)                                                                               
                return
            if choice <= 95 and choice > 79:                                                                              
                # If choice is within 79      to 95 you double your input
                await seco.add_balance(ctx.author.id,amount)                                                              
                # Add equal amount as your input to balance to double your input
                ll=discord.Embed(title="You won!",                                                                     
                # Send an embed announcing the win
                                description=f"Congratulations! You won **{double}** monies!", 
                                color=discord.Color.green())
                ll.add_field(name="** **", value="🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉", inline=False)
                await ctx.send(embed=ll)
                return
            if choice < 100 and choice > 95:                                                                             
                # If choice is within 96      to 100 you quadruple your input
                await seco.add_balance(ctx.author.id,quadwin)                                                             
                # Add 3 times your input to your balance to quadruple your input
                ss=discord.Embed(title="You won!",                                                                     
                # Send an embed announcing the win
                                description=f"Congratulations! You won **{quad}** monies!", 
                                color=discord.Color.green())
                ss.add_field(name="** **", value="🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉", inline=False)
                await ctx.send(embed=ss)
                return
            if choice <= 79:                                                                                             
                 # If choice is less than      or equal to 79 you lose your input
                await seco.remove_balance(ctx.author.id,amount)                                                           
                # Remove your input from your balance
                hh=discord.Embed(title="You lost!",                                                                    
                # Send an embed announcing the loss
                                description=f"Better luck next time! You lost your **{amount}** monies!", 
                                color=discord.Color.red())
                await ctx.send(embed=hh)
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def search(self, ctx):
        user = ctx.message.author.id
        balance=await seco.get_balance(user)
        rnum1 = randint(0, 200)
        rnum2 = randint(0, 300)
        rnum3 = randint(0, 70)
        die = randint(0, 5)
        options = {
            "car": rnum1,
            "house": rnum2,
            "boat": rnum3
        }
        e = discord.Embed(
        colour=discord.Colour.green(),
        title="Where do you want to search?",
        description="`car` , `house` , `boat`"
        )
        await ctx.send(embed=e)
        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower() == "car":
            if die == 3:
                letters = "hfkjdsfjahg543t3i598382742uidjksadn"
                fthingy = ""
                for nn in range(0, 10):
                    fthingy += random.choice(letters)
                    i = True
                    await ctx.send(f"Police is chasing you type `{fthingy}`")
                while i:
                    msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
                    msgco = msg.content.lower()
                    if msgco == fthingy:
                        coinremove = round(balance / 2)
                        await ctx.send(f"You escaped! But lost `{coinremove}` from your wallet! :(")
                        await seco.remove_balance(user,coinremove)
                    else:
                        e = discord.Embed(
                        colour=discord.Colour.green(),
                        title=f"You escaped! But police warned you and took all of your money from wallet! :("
                    )
                        await ctx.send(embed=e)
                        await seco.remove_balance(user,balance)
                        i = False
            else:
                coinremove = options["car"]
                await ctx.send(f"You found `{coinremove}` coins from someones car!")
                await seco.add_balance(user,coinremove)
            if msg.content.lower() == "house":
                if die == 3:
                    letters = "hfkjdsfjahg543t3i598382742uidjksadn"
                    fthingy = ""
                    for nn in range(0, 10):
                        fthingy += random.choice(letters)
                        i = True
                        await ctx.send(f"Police is chasing you type `{fthingy}`")
                    while i:
                        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        msgco = msg.content.lower()
                        if msgco == fthingy:
                            coinremove = round(balance / 2)
                            await ctx.send(f"You escaped! But lost `{coinremove}` from your wallet! :(")
                            await seco.remove_balance(user,coinremove)
                        else:
                            await ctx.send(f"You escaped! But police warned you and took all of your money from wallet! :(")
                            await seco.remove_balance(user,balance)
                            i = False
                else:
           
                    coinremove = options["house"]
                e = discord.Embed(
                colour=discord.Colour.green(),
                title=f"You found `{coinremove}` coins from someones house! It was a close one!"
            )
                await ctx.send(embed=e)
                await seco.add_balance(user,coinremove)

            if msg.content.lower() == "boat":
                if die == 3:
                    letters = "hfkjdsfjahg543t3i598382742uidjksadn"
                    fthingy = ""
                    for nn in range(0, 10):
                        fthingy += random.choice(letters)
                        i = True
                        await ctx.send(f"Police is chasing you type `{fthingy}`")
                        while i:
                         msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
                        msgco = msg.content.lower()
                        if msgco == fthingy:
                            coinremove = round(balance / 2)
                            await ctx.send(f"You escaped! But lost `{coinremove}` from your wallet! :(")
                            await seco.remove_balance(user,coinremove)
                        else:

                            await ctx.send(f"You escaped! But police warned you and took all of your money from wallet! :(")
                            await seco.remove_balance(user,balance)
                            i = False
            else:
                coinremove = options["boat"]
                e = discord.Embed(
                colour=discord.Colour.green(),
                title=f"You found `{coinremove}` coins from a boat!"
            )
                await ctx.send(embed=e)
                await seco.add_balance(user,coinremove)
    @search.error
    async def search_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = discord.Embed(
            colour=discord.Colour.red(),
            title="You search too much! One time Elon Musk is gonna send Space X 🚀rockets to your home! Try again in {:.2f}s".format(
                error.retry_after)
        )
            await ctx.send(embed=msg)
        else:
            raise error




class Giveaway(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def giveaway(self, ctx):
        timeout = 15.0
        embedq1 = discord.Embed(title=":gift: | SETUP WIZARD",
                                description=f"Welcome to the Setup Wizard. Answer the following questions within ``{timeout}`` Seconds!")
        embedq1.add_field(name=":star: | Question 1",
                          value="Where should we host the Giveaway?\n\n **Example**: ``#General``")
        embedq2 = discord.Embed(title=":gift: | SETUP WIZARD",
                                description="Great! Let's move onto the next question.")
        embedq2.add_field(name=":star: | Question 2",
                          value="How long should it last? ``<s|m|h|d|w>``\n\n **Example**:\n ``1d``")
        embedq3 = discord.Embed(title=":gift: | SETUP WIZARD",
                                description="Awesome. You've made it to the last question!")
        embedq3.add_field(name=":star: | Question 2",
                          value="What is the prize the winner will receive?\n\n **Example**:\n ``NITRO``")

        questions = [embedq1,
                     embedq2,
                     embedq3]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i in questions:
            await ctx.send(embed=i)

            try:
                msg = await self.client.wait_for('message', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                embed = discord.Embed(title=":gift: **Giveaway Setup Wizard**",
                                      description=":x: You didn't answer in time!")
                await ctx.send(embed=embed)
                return
            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2: -1])
        except:
            embed = discord.Embed(title=":gift: **Giveaway Setup Wizard**",
                                  description=":x: You didn't specify a channel correctly!")
            await ctx.send(embed=embed)
            return

        channel = self.client.get_channel(c_id)

        t = convert(answers[1])
        if t == -1:
            embed = discord.Embed(title=":gift: **Giveaway Setup Wizard**",
                                  description=":x: You didn't set a proper time unit!")
            await ctx.send(embed=embed)
            return
        elif t == -2:
            embed = discord.Embed(title=":gift: **Giveaway Setup Wizard**",
                                  description=":x: Time unit **MUST** be an integer")
            await ctx.send(embed=embed)
            return
        prize = answers[2]

        embed = discord.Embed(title=":gift: **Giveaway Setup Wizard**",
                              description="Okay, all set. The Giveaway will now begin!")
        embed.add_field(name="Hosted Channel:", value=f"{channel.mention}")
        embed.add_field(name="Time:", value=f"{answers[1]}")
        embed.add_field(name="Prize:", value=prize)
        await ctx.send(embed=embed)
        print(
            f"New Giveaway Started! Hosted By: {ctx.author.mention} | Hosted Channel: {channel.mention} | Time: {answers[1]} | Prize: {prize}")
        print("------")
        embed = discord.Embed(title=f":gift: **GIVEAWAY FOR: {prize}**",
                              description="React With"+"🎉"+"To Participate!")
        embed.add_field(name="Lasts:", value=answers[1])
        embed.add_field(name=f"Hosted By:", value=ctx.author.mention)
        msg = await channel.send(embed=embed)

        await msg.add_reaction("🎉")
        await asyncio.sleep(t)

        new_msg = await channel.fetch_message(msg.id)
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.client.user))

        winner = random.choice(users)
        lol = True
        if lol == True:
            await channel.send(f":tada: Congratulations! {winner.mention} won: **{prize}**!")
            print(f"New Winner! User: {winner.mention} | Prize: {prize}")
            print("------")

        embed2 = discord.Embed(title=f":gift: **GIVEAWAY FOR: {prize}**",
                               description=f":trophy: **Winner:** {winner.mention}")
        embed2.set_footer(text="Giveaway Has Ended")
        await msg.edit(embed=embed2)
        mom = ctx.message.author

        win = discord.Embed(title="Giveaway Info!", color=1752220)
        win.add_field(name="Winner", value=winner)
        win.add_field(name="Prize", value={prize})
        win.set_footer(text="Winner Declared!")
        await mom.send("Your Giveaway has ended!")
        await mom.send(embed=win)
        await winner.send(embed=win)


bot.add_cog(Music(bot))
bot.add_cog(ServerCommands(bot))
bot.add_cog(Economy(bot))
bot.add_cog(Giveaway(bot))



if __name__ == "__main__":
    bot.run(TOKEN)
