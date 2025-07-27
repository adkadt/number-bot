import os
import asyncio
import json
import sys

import datetime
import zoneinfo

from helpers import pickANumber

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot


if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file: 
        config = json.load(file)

intents = discord.Intents.default()
intents.message_content = True
intents.polls = True

NUMBER_CHANNEL_ID = 1329591419983237201

bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix_settings"]["prefix"]),
    intents=intents
    )
bot.config = config


@bot.event
async def on_ready():
    await bot.tree.sync()
    print('ALIVE!')
    # start daily number loop
    start_number.start()


@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return

    # logs (for debug)
    # log_file = open(f"{os.path.realpath(os.path.dirname(__file__))}/david.log", "a")
    # time_now = datetime.datetime.now()
    # log_file.write(f"{datetime.date.today()} {time_now.hour}:{time_now.minute}:{time_now.second} ({ctx.guild.name} #{ctx.channel}) {ctx.author.name} said: '{ctx.content}'\n")
    # log_file.close()

    await bot.process_commands(ctx)


# start number of the day everyday at 6am EST
number_hour = 6
number_minute = 0
est_tz = zoneinfo.ZoneInfo("America/New_York")
loop_time = datetime.time(hour=number_hour, minute=number_minute, tzinfo=est_tz)
@tasks.loop(time=loop_time)
async def start_number():
    # get channel for number
    channel = await bot.fetch_channel(NUMBER_CHANNEL_ID) # TODO change based on server
    await pickANumber.startNumberPoll(channel=channel, hours=6, minutes=0, real=True)


# reloads commands
@bot.hybrid_command(name='reload')
async def reload_cogs(ctx):
    state: discord.Message = await ctx.reply("Reloading Commands")
    for cog_file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if cog_file.endswith(".py"):
            extension = cog_file[:-3]
            try:
                await bot.reload_extension(f"cogs.{extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}\n{e}")
    await state.edit(content="Reloaded Commands")


# load slash commands
async def load_cogs() -> None:
    for cog_file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if cog_file.endswith(".py"):
            extension = cog_file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}\n{e}")


asyncio.run(load_cogs())
# get token
with open(f"{os.path.dirname(__file__)}/token.key") as f:
    TOKEN = f.read()
bot.run(TOKEN)
# TODO get from sys var