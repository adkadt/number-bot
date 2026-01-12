import asyncio
import discord
# from discord import Poll

import inflect
import random

import os
import json
import pandas
import matplotlib.pyplot as plt
import requests

from datetime import timedelta, date, datetime
import zoneinfo
import pytz

from helpers.discordJson import DiscordJson

async def savePollState(number: int, message: discord.Message):
    fileName = "numbers"
    jsonData = DiscordJson.open(fileName)
    est = pytz.timezone('US/Eastern')

    messageDate = message.created_at.astimezone(est)

    if str(messageDate.year) not in jsonData.keys():
        jsonData[str(messageDate.year)] = {}
    if str(messageDate.month) not in jsonData[str(messageDate.year)].keys():
        jsonData[str(messageDate.year)][str(messageDate.month)] = {}
    if "{:02}".format(messageDate.day) not in jsonData[str(messageDate.year)][str(messageDate.month)].keys():
        jsonData[str(messageDate.year)][str(messageDate.month)]["{:02}".format(messageDate.day)] = {}

    jsonData[str(messageDate.year)][str(messageDate.month)]["{:02}".format(messageDate.day)]['message_id'] = message.id
    jsonData[str(messageDate.year)][str(messageDate.month)]["{:02}".format(messageDate.day)]['total_votes'] = message.poll.total_votes
    jsonData[str(messageDate.year)][str(messageDate.month)]["{:02}".format(messageDate.day)]['number'] = number

    for i in range(1, 11):
        jsonData[str(messageDate.year)][str(messageDate.month)]["{:02}".format(messageDate.day)][str(i)] = []
        voters = [voter async for voter in message.poll.get_answer(i).voters()]
        for voter in voters:
            jsonData[str(messageDate.year)][str(messageDate.month)]["{:02}".format(messageDate.day)][str(i)].append(str(voter.id))
            
    jsonData = DiscordJson.sort_json_numerically(jsonData)
    DiscordJson.write(fileName, jsonData)


async def checkIfAllVotes(channel, pollMsg, numVotes: int):
    try:
        pollMsgFetched = await channel.fetch_message(pollMsg.id)
        if pollMsgFetched.poll.total_votes >= numVotes:
            return True
    except Exception as e:
        await channel.send(f"Error: PAN95")
        with open("error_log.txt", "w") as f:  
            f.write(str(e))
    return False


# run number using msg id
async def rollNumber(channel: discord.channel, pollMsg: discord.Message, real: bool):
    pollMsg = await channel.fetch_message(pollMsg.id)    

    try:
        if not pollMsg.poll.is_finalized():
            await pollMsg.end_poll()
    except:
        print(f"Finalized: {pollMsg.poll.is_finalized()}")

    await channel.send(f"<@&1329614215962689643> Here we go for today's number")
    await asyncio.sleep(2)

    today = date.today()
    day_name = today.strftime('%A, %B %d, %Y')
    await channel.send(f"Today is {day_name}")
    await asyncio.sleep(2)

    await channel.send(f"Ten Balls")
    await asyncio.sleep(2)

    await channel.send(f"Each ball has a number")
    await asyncio.sleep(2)

    await channel.send(f"Numbers one through ten")
    await asyncio.sleep(2)

    await channel.send(f"Swirl the numbers")
    await asyncio.sleep(3)  

    await channel.send(f"Pick a number")
    await asyncio.sleep(2)

    await channel.send(f"Today's number is...")
    await asyncio.sleep(4)

    # pull random number
    number = random.randint(1, 10)
    number_words = inflect.engine().number_to_words(number).capitalize().ljust(8, ' ')
    await channel.send(f"||{number_words}||!")

    pollMsgFetched = await channel.fetch_message(pollMsg.id)
    voters = [voter async for voter in pollMsgFetched.poll.get_answer(number).voters()]

    # save data
    if real:
        serverJson = DiscordJson.open("info")
        for voter in voters:
            serverJson['users'][str(voter.id)]['wins'] += 1
            payload = {"user":  str(voter.id)}
            requests.post("http://localhost:8000/message", json=payload)
        DiscordJson.write("info", serverJson)
        await savePollState(number, pollMsgFetched)


async def startNumberPoll(channel: discord.channel, hours: int, minutes: int, real: bool):
    # prepare timings
    est_tz = zoneinfo.ZoneInfo("America/New_York")
    start_time = datetime.now(est_tz)
    pollEndTime = start_time + timedelta(hours=hours, minutes=minutes)

    # set up poll
    poll_duration = hours
    if minutes > 0:
        poll_duration += 1
    numberPoll = discord.Poll(question=f"Pick a Number (Poll only lasts {hours + minutes/60} Hours)", duration=timedelta(hours=poll_duration, minutes=1))
    for i in range(10):
        numberPoll = discord.Poll.add_answer(self=numberPoll ,text=str(i+1))

    # send poll
    pollMsg = await channel.send(content = "<@&1329614215962689643>", poll=numberPoll)
    
    allVotes = False

    # run 1 hour reminder
    if hours > 1:
        reminderTime = pollEndTime - timedelta(hours=1)
        while reminderTime > datetime.now(est_tz):
            await asyncio.sleep(5)
            allVotes = await checkIfAllVotes(channel=channel, pollMsg=pollMsg, numVotes=6)
            if allVotes:
                break
        if not allVotes:
            await channel.send(content = "<@&1329614215962689643> 1 Hour Warning")
        
    # run 10 minute reminder
    if hours > 0 or minutes > 10:
        reminderTime = pollEndTime - timedelta(minutes=10)
        while reminderTime > datetime.now(est_tz):
            await asyncio.sleep(5)
            allVotes = await checkIfAllVotes(channel=channel, pollMsg=pollMsg, numVotes=6)
            if allVotes:
                break
        if not allVotes:
            await channel.send(content = "<@&1329614215962689643> 10 Minute Warning")

    while pollEndTime > datetime.now(est_tz):
        print(f"Now: {datetime.now(est_tz)}, End: {pollEndTime}")
        await asyncio.sleep(5)
        allVotes = await checkIfAllVotes(channel=channel, pollMsg=pollMsg, numVotes=6)
        if allVotes:
            break
    
    if allVotes:
        await channel.send(f"Everyone has chosen their Number")
        
    await rollNumber(channel=channel, pollMsg=pollMsg, real=real)


def getCorrect(member: discord.Member):
    serverJson = DiscordJson.open("info")
    return serverJson['users'][str(member.id)]['wins'] 


def adjustWins(member: discord.Member, change):
    serverJson = DiscordJson.open("info")
    serverJson['users'][str(member.id)]['wins'] += change
    DiscordJson.write("info" ,serverJson)


def makeRandomCheckGraph(num):
    fileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/randomCheck.png"

    x = []
    for i in range(num):
        x.append(random.randint(1, 10))

    plt.hist(x)
    plt.title(f"Histogram of {num} Random Day Numbers")
    plt.ylabel("Frequency")
    plt.xlabel("Number of the Day")
    plt.savefig(fileName)
    plt.cla()

    return fileName
