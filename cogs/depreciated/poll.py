import os
import csv
import pandas as pd
import random

from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context


class Poll(commands.Cog, name="poll"):

  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command(name='poll_start')
  async def pollStart(self, ctx: Context, poll_id):
    servers = pd.read_csv(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/helpers/servers.csv", index_col="guild_id")

    try:
      pollFile = f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}//helpers/" + servers.loc[int(ctx.guild.id), "file_name"] + "Poll" + poll_id + ".csv"
    except:
      await ctx.reply("This Server is not supported")
      return

    embed = Embed(title="Poll")
    description = ""

    try:
      with open(pollFile, "r") as f:
        csvreader = csv.reader(f)
        for index, row in enumerate(csvreader):
          if index > 0:
            optionName = row[0]
            description += f"{row[1]} {optionName}\n"
      embed.description = description
      embed.set_footer(
        text="Please react to this message with the above emojis to cast your vote."
      )
    except:
      await ctx.reply("Poll not found")
      return

    message = await ctx.reply(embed=embed)

    with open(pollFile, "r") as f:
      csvreader = csv.reader(f)
      for index, row in enumerate(csvreader):
        if index > 0:
          await message.add_reaction(row[1])

  
  @commands.hybrid_command(name='poll_add')
  async def addOption(self, ctx: Context, poll_id, option, emoji):

    servers = pd.read_csv(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/helpers/servers.csv", index_col="guild_id")

    try:
      pollFile = f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}//helpers/" + servers.loc[int(ctx.guild.id), "file_name"] + "Poll" + poll_id + ".csv"
    except:
      ctx.reply("Failed to open file (Err Code: 57)")
      return

    try:
      options= pd.read_csv(pollFile, index_col="option")
      if option in options.index:
        await ctx.reply("Option already exists")
        return
      options.set_index('emoji', inplace=True)
      if emoji in options.index:
        await ctx.reply("Emoji already exists")
        return
    except:
      f = open(pollFile, 'w')
      f.write('option,emoji\n')
      f.close()

    with open(pollFile, 'a', newline='') as f:
      row = [option, emoji]
      csvwriter = csv.writer(f, delimiter=',')
      csvwriter.writerow(row)

    try:
      await ctx.reply(f"{option} option added")
    except:
      await ctx.reply("No permission")


  @commands.hybrid_command(name='poll_remove')
  async def removeOption(self, ctx: Context, poll_id, option):
    
    servers = pd.read_csv(f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/helpers/servers.csv", index_col="guild_id")

    try:
      pollFile = f"{os.path.realpath(os.path.dirname(os.path.dirname(__file__)))}/helpers/" + servers.loc[int(ctx.guild.id), "file_name"] + "Poll" + poll_id + ".csv"
    except:
      await ctx.reply("This Server is not supported")
      return

    try:
      options = pd.read_csv(pollFile, index_col="option")
    except:
      await ctx.reply(f"Poll {poll_id} not found")
      return

    try:
      options.drop(option, axis=0, inplace=True)
      options.to_csv(pollFile, index=True)
    except:
      await ctx.reply(f"Option {option} not found")
      return

    await ctx.reply(f"Removed option {option}")

    if options.empty:
      os.remove(pollFile)



  @commands.hybrid_command(name='coin_flip')
  async def coinFlip(self, ctx):
    coin = random.randint(0, 1)

    if coin:
      await ctx.reply("Heads!")
    else:
      await ctx.reply("Tails!")


async def setup(bot):
  await bot.add_cog(Poll(bot))