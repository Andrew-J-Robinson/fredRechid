import discord
from discord.ext import commands
import random
import time

class Games(commands.Cog):

    def __init__(self, client):
        self.client = client

    #8ball game
    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        await ctx.channel.purge(limit = 1)
        responses = ['It is certain',
                    'It is decidedly so.',
                    'Without a doubt.'
                    'Yes - definitely.',
                    'You may rely on it.',
                    'As I see it, yes.',
                    'Most likely.',
                    'Outlook good.',
                    'Yes.',
                    'Signs point to yes.',
                    'Ask again later.',
                    'Better not tell you now.',
                    'Cannot predict now.',
                    'Concentrate and ask again.',
                    "Don't count on it.",
                    'My reply is no.',
                    'My sources say no.',
                    'Outlook not so good',
                    'Very doubtful.']
        await ctx.send(f'8-Ball: {question}')
        time.sleep(3)
        await ctx.send(f'Answer: {random.choice(responses)}\n')


def setup(client):
    client.add_cog(Games(client))
