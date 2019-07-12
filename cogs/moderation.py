import discord
from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = voice_clients

    #Commands

    #Clear messages
    @client.command()
    @commands.has_permissions(manage_messages)
    async def clear(self, ctx, amount=1):
        amount = amount + 1
        await ctx.channel.purge(limit = amount)
    
