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

    #Kick member
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        print(f'Kicked {member.mention}.\n')
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention}.')

    #Ban member
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        print(f'Banned {member.mention}.\n')
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention}.')

    #Unban member
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                print(f'Unbanned {member}.\n')
                await ctx.send(f'Unbanned {user.mention}.')
                return
            else:
                print(f"Error: {user.mention} isn't banned.")
                await ctx.send(f"Error: {user.mention} isn't banned.")
                return



def setup(client):
    client.add_cog(Moderation(client))
