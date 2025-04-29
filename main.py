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

utc = datetime.timezone.utc

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file: 
        config = json.load(file)

intents = discord.Intents.default()
intents.message_content = True
intents.polls = True
# intents.members = True


bot = Bot(
    command_prefix=commands.when_mentioned_or(config["prefix_settings"]["prefix"]),
    intents=intents
    )

bot.config = config

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('ALIVE!')
    send_message.start() 


@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return

    #logs
    f = open(f"{os.path.realpath(os.path.dirname(__file__))}/david.log", "a")
    timeNow = datetime.datetime.now()
    f.write(f"{datetime.date.today()} {timeNow.hour}:{timeNow.minute}:{timeNow.second} ({ctx.guild.name} #{ctx.channel}) {ctx.author.name} said: '{ctx.content}'\n")

    f.close()
    await bot.process_commands(ctx)


number_hour = 12
number_minute = 0
est_tz = zoneinfo.ZoneInfo("America/New_York")
loop_time = datetime.time(hour=number_hour, minute=number_minute, tzinfo=est_tz)
@tasks.loop(time=loop_time)
async def send_message():
    NUMBER_ID = 1329591419983237201
    channel = await bot.fetch_channel(NUMBER_ID)
    await pickANumber.startRND(channel=channel)


@bot.hybrid_command(name='reload')
async def reload_cogs(ctx):
    state: discord.Message = await ctx.reply("Reloading Commands")
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.reload_extension(f"cogs.{extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}\n{e}")
    await state.edit(content="Reloaded Commands")


async def load_cogs() -> None:
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
            except Exception as e:
                print(f"Failed to load extension {extension}\n{e}")


asyncio.run(load_cogs())
with open(f"{os.path.dirname(__file__)}/token.key") as f:
    TOKEN = f.read()
bot.run(TOKEN)