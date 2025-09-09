import os
import csv
import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks
from helpers import pickANumber
from datetime import datetime
import pytz
import re
from concurrent.futures import ProcessPoolExecutor

import requests

BOBSARVERID = 1186392585066004490

class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot
  
    @commands.hybrid_command(name='say',hidden=True)
    @checks.is_owner()
    async def say(self, context: Context, channel, message):
        channel = self.bot.get_channel(int(channel[2:-1]))
        await channel.send(message)
        await context.send('Sent: ' + message)


    @commands.hybrid_command(name='test',hidden=True)
    @checks.is_owner()
    async def say(self, ctx: Context, user: discord.User):
        payload = {"user":  str(user.id)}
        requests.post("http://localhost:8000/message", json=payload)
        await ctx.reply("Sent win notification to Sarver")
        



    # @commands.hybrid_command(name='write-data',hidden=True)
    # @checks.is_owner()
    # async def writeData(self, ctx: Context):
    #     state = await ctx.reply("Processing")
    
    #     units = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    #     est = pytz.timezone('US/Eastern')

    #     jsonData = {}
    #     async for message in self.bot.get_channel(1329591419983237201).history(limit=400):
    #         messageDate = message.created_at.astimezone(est)

    #         if messageDate.year not in jsonData.keys():
    #             jsonData[messageDate.year] = {}
    #         if messageDate.month not in jsonData[messageDate.year].keys():
    #             jsonData[messageDate.year][messageDate.month] = {}
    #         if messageDate.day not in jsonData[messageDate.year][messageDate.month].keys():
    #             jsonData[messageDate.year][messageDate.month][messageDate.day] = {}

    #         if message.poll is None:
    #             if '||' in message.content:
    #                 numStr = ''.join([i for i in message.content if i.isalpha()])
    #                 number = units.index(numStr.lower())
    #                 jsonData[messageDate.year][messageDate.month][messageDate.day]['number'] = number

    #         else:
    #             jsonData[messageDate.year][messageDate.month][messageDate.day]['message_id'] = message.id
    #             jsonData[messageDate.year][messageDate.month][messageDate.day]['total_votes'] = message.poll.total_votes
    #             for i in range(1, 11):
    #                 jsonData[messageDate.year][messageDate.month][messageDate.day][str(i)] = []
    #                 voters = [voter async for voter in message.poll.get_answer(i).voters()]
    #                 for voter in voters:
    #                     jsonData[messageDate.year][messageDate.month][messageDate.day][str(i)].append(str(voter.id))
        
    #     pickANumber.writeJson("numbers", jsonData)
    #     await state.edit(content="Done")
                

    @commands.hybrid_command(name='adjust-wins')
    @checks.is_owner()
    async def adjustWins(self, ctx: Context, member: discord.Member=None, change: int=None):
        if member is None:
            member = ctx.author
        if int is None:
            await ctx.reply("Must specify a change")
        
        pickANumber.adjustWins(member, change)
        await ctx.reply(f"Added {change} to <@{member.id}>'s correct number guesses!")


    # @commands.hybrid_command(name='suggestions')
    # @checks.is_owner()
    # async def suggestions(self, ctx: Context):
    #     embed = discord.Embed(
    #         title="Number of Day Suggestions",
    #         description="I am looking for suggestions of statistics we would like to view. Please suggest some in this thread and i'll see what can be done. I have outlined some categories for theses statistics below."
    #     )
    #     embed.add_field(
    #         name="Personal Statistics",
    #         value="Theses kind of statistics would be based on a specific person\n\
    #                e.g. Personal Win Rate",
    #         inline=False
    #     )
    #     embed.add_field(
    #         name="Server Statistics",
    #         value="Theses kind of statistics would be based on everyone as a whole\n\
    #                e.g. Server Win Rate",
    #         inline=False
    #     )
    #     embed.add_field(
    #         name="Number Statistics",
    #         value="Theses kind of statistics would be based on the numbers picked\n\
    #                e.g. Last the same number was picked",
    #         inline=False
    #     )
    #     embed.set_footer(text="Not all suggestions will be made")
        
    #     await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Owner(bot))