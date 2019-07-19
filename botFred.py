'''
    File name: botFred.py
    Author: Andrew Robinson
    Date Created: 6/20/2019
    Last Modified: 7/12/2019
    Python Version 3.6
'''

import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import time
import urllib.request
import urllib.parse
import re
import logging

#Discord logging
#-------------------------------------------------------------------------------
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#-------------------------------Bot setup--------------------------------------
################################################################################

#Read and pass token from token.txt
#----------------------------------
tokenFile = open("token.txt", 'r')
TOKEN = tokenFile.read().replace('\n', '')
tokenFile.close()

#Command prefix. Type this character before command. Eg: '.join'
#---------------------------------------------------------------
PREFIX = '.'
client = commands.Bot(command_prefix = PREFIX)

#Connect to cogs folder
#----------------------
@client.command()
@commands.has_role("Admin")
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
@commands.has_role("Admin")
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

#---------------------------Basic Bot functions---------------------------------
################################################################################

#Confirm bot is online
#---------------------
@client.event
async def on_ready():
    print(client.user.name + " is online.\n")

#Command bot to join voice channel
#---------------------------------
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
        await ctx.channel.purge(limit = 1)
        await ctx.send("Sup, nerds?")

#Command bot to leave voice channel
#----------------------------------
@client.command(pass_context=True)
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await ctx.channel.purge(limit = 1)
        await voice.disconnect()
        print(f"The bot has left {channel}\n")
        await ctx.send("I'm out this mf.")
    else:
        print("Leave command failed: Bot not in channel\n")
        await ctx.send("You tryna kick me out and I'm not even in here?")

#Play Spongebob quote from specific Youtube page when a user joins the voice channel
#-------------------------------------------------------------------------------
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
                voice = get(client.voice_clients, guild=ctx.guild)#Initialize voice client

                #Sets youtube_dl options
                ydl_opts = {
                    'format': 'beat audio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }

                #Download the file from  the given url using the initialized options above
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print("Downloading audio file now\n")
                    ydl.download(["https://www.youtube.com/watch?v=ifaoKZfQpdA"])

                #Check if the downloaded file is an mp3 and isn't the 'song.mp3' file used in another command
                #If both pass, rename the downloaded file to 'clip.mp3'
                for file in os.listdir('./'):
                    if file.endswith(".mp3") and not file.endswith("song.mp3"):
                        name = file
                        os.rename(file, "clip.mp3")
                        print(f"Renamed file: {file}\n")

                if voice.is_connected(): #Check if the bot is connected to a voice channel. If it is, play the clip with FFmpeg
                    voice.play(discord.FFmpegPCMAudio("clip.mp3"), after=lambda e: print(f"{name} has finished playing"))
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.7
                else:
                    print("ERROR: Bot isn't connected to a voice channel.")

        except PermissionError:
            print("ERROR to remove audio file: file is in use\n")
            await ctx.send("ERROR: audio clip is playing.")
            return
    else:
        return

#Command bot to find youtube video and play audio
#------------------------------------------------
@client.command(pass_context=True)
@commands.has_role("Admin")
async def play(ctx, *, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there: #If song.mp3 is already present, remove it to be replaced by the next song
            os.remove("song.mp3")
            print("Removed old song file\n")
    except PermissionError:
        print("ERROR to remove audio file: file is in use\n")
        await ctx.send("ERROR: audio clip is playing.")
        return

    await ctx.send("Getting everything ready now")

    voice = get(client.voice_clients, guild=ctx.guild)#Initialize voice client

    #Sets youtube_dl options
    ydl_opts = {
        'format': 'beat audio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }


    if url.startswith("http://") or url.startswith("https://"): #Check if play request is already in URL format
        pass
    else: #If the requested string isn't in URL format, converts string to a usable YouTube URL
        query_string = urllib.parse.urlencode({"search_query" : url})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        url = "http://www.youtube.com/watch?v=" + search_results[0]

    #Download the file from  the given url using the initialized options above
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio file now\n")
        ydl.download([url])

    #Check if the downloaded file is an mp3 and isn't the 'song.mp3' file used in another command
    #If both pass, rename the downloaded file to 'clip.mp3'
    for file in os.listdir('./'):
        if not file.endswith("clip.mp3") and file.endswith(".mp3"):
            name = file
            os.rename(file, "song.mp3")
            print(f"Renamed file: {file}\n")

    if voice.is_connected(): #Check if the bot is connected to a voice channel. If it is, play the clip with FFmpeg
        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.5
    else:
        print("ERROR: Bot isn't connected to a voice channel.")

    newName = name.rsplit("-", 2)
    print(newName)
    await ctx.send(f"Playing: {newName[0]}")
    print("playing\n")

#Runs bot using token as defined above
client.run(TOKEN)
