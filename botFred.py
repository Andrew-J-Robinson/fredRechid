'''
    File name: botFred.py
    Author: Andrew Robinson
    Date Created: 6/20/2019
    Last Modified: 6/25/2019
    Python Version 3.6

    Known Issues:
        Semantic Error: .play command conflicts with voice state update event
        When one is run after the other, it plays the audio clip from the
        previous execution and must be run a second time to work properly
'''

import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import time

#Token to connect code to Discord bot
TOKEN = ''

#Command prefix. Type this character before command. Eg: '.join'
PREFIX = '.'
client = commands.Bot(command_prefix = PREFIX)

#Confirm bot is online
@client.event
async def on_ready():
    print(client.user.name + " is online.\n")

#Play Spongebob quote when a user joins the voice channel
@client.event
async def on_voice_state_update(ctx, before, after):
    clip_there = os.path.isfile("clip.mp3")
    if not before.channel and after.channel:
        try:
            if clip_there: #If clip.mp3 is already present, play it
                voice = get(client.voice_clients, guild=ctx.guild)

                time.sleep(.5)

                if voice.is_connected():
                    voice.play(discord.FFmpegPCMAudio("clip.mp3"), after=lambda e: print(f"{name} has finished playing"))
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.7
                else:
                    return
            else: #Else if it isn't, download the youtube clip and play it
                voice = get(client.voice_clients, guild=ctx.guild)
                ydl_opts = {
                    'format': 'beat audio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print("Downloading audio file now\n")
                    ydl.download(["https://www.youtube.com/watch?v=ifaoKZfQpdA"])
                for file in os.listdir('./'):
                    if file.endswith(".mp3"):
                        name = file
                        os.rename(file, "clip.mp3")
                        print(f"Renamed file: {file}\n")
                if voice.is_connected():
                    voice.play(discord.FFmpegPCMAudio("clip.mp3"), after=lambda e: print(f"{name} has finished playing"))
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.7
                else:
                    return

        except PermissionError:
            print("ERROR to remove audio file: file is in use\n")
            await ctx.send("ERROR: audio clip is playing.")
            return
    else:
        return

#Command bot to join voice channel
@client.command(pass_context=True)
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
        await ctx.send("I'm already in here, dummy.")
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")
        await ctx.send("Sup, nerds?")

#Command bot to leave voice channel
@client.command(pass_context=True)
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}\n")
        await ctx.send("I'm out this mf.")
    else:
        print("Leave command failed: Bot not in channel\n")
        await ctx.send("You tryna kick me out and I'm not even in here?")

#Command bot to find youtube video and play audio
@client.command(pass_context=True)
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file\n")
    except PermissionError:
        print("ERROR to remove audio file: file is in use\n")
        await ctx.send("ERROR: audio clip is playing.")
        return

    await ctx.send("Getting everything ready now")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'beat audio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio file now\n")
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith(".mp3"):
            name = file
            os.rename(file, "song.mp3")
            print(f"Renamed file: {file}\n")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.7

    newName = name.rsplit("-", 2)
    await ctx.send(f"Playing: {newName}")
    print("playing\n")

#Runs bot using token as defined above
client.run(TOKEN)
