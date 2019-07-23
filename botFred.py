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
import shutil

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
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
@commands.has_permissions(administrator=True)
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
@commands.has_any_role('Owner', 'Admin')
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
@commands.has_any_role('Owner', 'Admin')
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
                    'quiet': True,
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
                    voice.play(discord.FFmpegPCMAudio("clip.mp3"), after=lambda e: print(f"{name} has finished playing\n"))
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.7
                else:
                    print("ERROR: Bot isn't connected to a voice channel.\n")

        except PermissionError:
            print("ERROR to remove audio file: file is in use\n")
            await ctx.send("ERROR: audio clip is playing.")
            return
    else:
        return

#Command bot to find youtube video and play audio
#------------------------------------------------
@client.command(pass_context=True, aliases=['p', 'pla'])
@commands.has_any_role('Owner', 'Admin', 'Member')
async def play(ctx, *, url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more songs in queue\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "//" + first_file)
            if length != 0:
                print("Playing next song in queue\n")
                print(f"Songs still in queue: {still_q}\n")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if not file.endswith("clip.mp3") and file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                if voice.is_connected(): #Check if the bot is connected to a voice channel. If it is, play the clip with FFmpeg
                    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = 0.5
                else:
                    print("ERROR: Bot isn't connected to a voice channel.\n")

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the end of the last song\n")


    song_there = os.path.isfile("song.mp3")
    try:
        if song_there: #If song.mp3 is already present, remove it to be replaced by the next song
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file\n")
    except PermissionError:
        print("ERROR to remove audio file: file is in use\n")
        await ctx.send("ERROR: audio clip is playing.")
        return

    #Check to make sure there's no old Queue folder
    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue folder\n")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder\n")

    await ctx.send("Getting everything ready now")
    voice = get(client.voice_clients, guild=ctx.guild)#Initialize voice client

    #Sets youtube_dl options
    ydl_opts = {
        'format': 'beat audio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }

    #Check if play request is already in URL format
    if url.startswith("http://") or url.startswith("https://"):
        pass
    else: #If the requested string isn't in URL format, convert it to a usable YouTube URL
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
        voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.5
    else:
        print("ERROR: Bot isn't connected to a voice channel.\n")

    newName = name.rsplit("-", 2)
    print(f"{newName[0]} playing\n")
    await ctx.send(f"Playing: {newName[0]}")

#Command bot to pause voice output
#------------------------------------------------
@client.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music Paused\n")
        voice.pause()
        await ctx.send("Music Paused")
    else:
        print("Music not playing: Failed pause\n")
        await ctx.send("Music not playing")

#Command bot to resume voice output
#------------------------------------------------
@client.command(pass_context=True, aliases=['res'])
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_paused():
        print("Resuming Music\n")
        voice.resume()
        await ctx.send("Resuming Music")
    else:
        print("Music is not paused\n")
        await ctx.send("The Music isn't paused")

#Command bot to stop voice output
#------------------------------------------------
@client.command(pass_context=True)
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    queues.clear()

    if voice and voice.is_playing():
        print("Music Stopped\n")
        voice.stop()
        await ctx.send("Music stopped.")
    else:
        print("Music not playing: Failed to Stop\n")
        await ctx.send("Music isn't playing")

#Command bot to queue next song
#------------------------------------------------
queues = {}

@client.command(pass_context=True)
async def queue(ctx,* , url: str):
    #Create queue directory
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"/song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    #Check if play request is already in URL format
    if url.startswith("http://") or url.startswith("https://"):
        pass
    else: #If the requested string isn't in URL format, convert it to a usable YouTube URL
        query_string = urllib.parse.urlencode({"search_query" : url})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        url = "http://www.youtube.com/watch?v=" + search_results[0]

    #Download the file from  the given url using the initialized options above
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio file now\n")
        ydl.download([url])
    await ctx.send("Adding song " + str(q_num) + " to the queue\n")

    print("Song added to queue\n")

#Runs bot using token as defined above
client.run(TOKEN)
