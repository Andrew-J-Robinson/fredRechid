import discord
from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Clear messages
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amount=1):
        amount = amount + 1
        await ctx.channel.purge(limit = amount)

def setup(client):
    client.add_cog(Moderation(client))
