import asyncio
import discord

import inflect
import random

import os
import json
import pandas
import matplotlib.pyplot as plt

from datetime import timedelta, date, datetime
import zoneinfo
# import datetime
# from datetime import datetime
import pytz

from discord import Poll



def openJson(fileName):
    serverInfoFileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/{fileName}.json"
    with open(serverInfoFileName, 'r') as serverInfoFile:
        serverJson = json.load(serverInfoFile)
    return serverJson

def writeJson(fileName, serverJson):
    serverInfoFileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/{fileName}.json"
    with open(serverInfoFileName, 'w') as serverInfoFile:
        json.dump(serverJson, serverInfoFile, sort_keys=True, indent=4)


def makeWinChart():
    fileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/winGraph.png"
    serverJson = openJson("info")
    dispNames = []
    wins = []
    high = 0

    for user in serverJson['users']:
        sub = serverJson['users'][user]
        dispNames.append(sub['display_name'])
        wins.append(sub['wins'])
        if sub['wins'] > high:
            high = sub['wins']

    plt.xticks(rotation=15)
    plt.bar(dispNames, wins)
    plt.title('Correct Number Guesses')

    for i in range(len(dispNames)):
        plt.text(i, wins[i] + high*0.01, wins[i])

    plt.savefig(fileName)
    plt.cla()

    return fileName


async def savePollState(number: int, message: discord.Message):
    fileName = "numbers"
    jsonData = openJson(fileName)
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
    
    writeJson(fileName, jsonData)


async def startRND(channel: discord.channel, test=None):
    isTest = False
    if test is not None:
        isTest = True

    sleepMin = 10
    numberPoll = Poll(question=f"Pick a Number (Poll only lasts {sleepMin} minutes)", duration=timedelta(minutes=60))
    for i in range(10):
        numberPoll = Poll.add_answer(self=numberPoll ,text=str(i+1))

    # allowed_mentions = discord.AllowedMentions(everyone = True)
    pollMsg = await channel.send(content = "<@&1329614215962689643>", poll=numberPoll)

    for i in range(0, int(sleepMin*60), 5):
        await asyncio.sleep(5)
        try:
            pollMsgFetched = await channel.fetch_message(pollMsg.id)
        except:
            await channel.send(f"ErrCd: PAN105 (fix it adam)")
        if pollMsgFetched.poll.total_votes >= 6:
            await channel.send(f"Everyone has chosen their Number")
            break
        if i == 420:
            await channel.send(content = "<@&1329614215962689643> 3 Minute Warning")

    await pollMsg.end_poll()
    await asyncio.sleep(6)  

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

    number = random.randint(1, 10)
    number_words = inflect.engine().number_to_words(number).capitalize().ljust(8, ' ')
    await channel.send(f"||{number_words}||!")

    voters = [voter async for voter in pollMsgFetched.poll.get_answer(number).voters()]

    serverJson = openJson("info")
    for voter in voters:
        serverJson['users'][str(voter.id)]['wins'] += 1
    writeJson("info", serverJson)
    await savePollState(number, pollMsgFetched)

    makeWinChart()


async def checkIfAllVotes(channel, pollMsg, numVotes: int):
    try:
        pollMsgFetched = await channel.fetch_message(pollMsg.id)
    except:
        await channel.send(f"Error: PAN161 (ADAM FIX IT!)")

    if pollMsgFetched.poll.total_votes >= numVotes:
        return True
    return False


async def startNumberPoll(channel: discord.channel, hours: int, minutes: int, real: bool):
    # prepare timings
    est_tz = zoneinfo.ZoneInfo("America/New_York")
    start_time = datetime.now(est_tz)
    pollEndTime = start_time + timedelta(hours=hours, minutes=minutes)

    # set up poll
    poll_duration = hours
    if poll_duration < 1:
        poll_duration = 1
    numberPoll = Poll(question=f"Pick a Number (Poll only lasts {hours + minutes/60} Hours)", duration=timedelta(hours=poll_duration, minutes=1))
    for i in range(10):
        numberPoll = Poll.add_answer(self=numberPoll ,text=str(i+1))

    # send poll
    pollMsg = await channel.send(content = "<@&1329614215962689643>", poll=numberPoll)
    
    allVotes = False

    # run 1 hour reminder
    if hours > 1:
        reminderTime = pollEndTime - timedelta(hours=1)
        while reminderTime > datetime.now(est_tz):
            await asyncio.sleep(5)
            allVotes = await checkIfAllVotes(channel=channel, pollMsg=pollMsg, numVotes=1)
            if allVotes:
                break
        await channel.send(content = "<@&1329614215962689643> 1 Hour Warning")
        
    # run 10 minute reminder
    if hours > 0 or minutes > 10:
        reminderTime = pollEndTime - timedelta(minutes=10)
        while reminderTime > datetime.now(est_tz):
            await asyncio.sleep(5)
            allVotes = await checkIfAllVotes(channel=channel, pollMsg=pollMsg, numVotes=1)
            if allVotes:
                break
        await channel.send(content = "<@&1329614215962689643> 10 Minute Warning")

    while pollEndTime > datetime.now(est_tz):
        await asyncio.sleep(5)
        allVotes = await checkIfAllVotes(channel=channel, pollMsg=pollMsg, numVotes=1)
        if allVotes:
            print(allVotes)
            break

    if allVotes:
        await channel.send(f"Everyone has chosen their Number")

    await pollMsg.end_poll()

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
        serverJson = openJson("info")
        for voter in voters:
            serverJson['users'][str(voter.id)]['wins'] += 1
        writeJson("info", serverJson)
        await savePollState(number, pollMsgFetched)

        makeWinChart()

# run number using msg id
# async def tempFix(channel: discord.channel, msg_id: int):
#     pollMsg = await channel.fetch_message(msg_id)    

#     await channel.send(f"<@&1329614215962689643> Here we go for today's number")
#     await asyncio.sleep(2)

#     today = datetime.date.today()
#     day_name = today.strftime('%A, %B %d, %Y')
#     await channel.send(f"Today is {day_name}")
#     await asyncio.sleep(2)

#     await channel.send(f"Ten Balls")
#     await asyncio.sleep(2)

#     await channel.send(f"Each ball has a number")
#     await asyncio.sleep(2)

#     await channel.send(f"Numbers one through ten")
#     await asyncio.sleep(2)

#     await channel.send(f"Swirl the numbers")
#     await asyncio.sleep(3)  

#     await channel.send(f"Pick a number")
#     await asyncio.sleep(2)

#     await channel.send(f"Today's number is...")
#     await asyncio.sleep(4)

#     number = random.randint(1, 10)
#     # number = 7
#     number_words = inflect.engine().number_to_words(number).capitalize().ljust(8, ' ')
#     await channel.send(f"||{number_words}||!")

#     voters = [voter async for voter in pollMsg.poll.get_answer(number).voters()]

#     serverJson = openJson("info")
#     for voter in voters:
#         serverJson['users'][str(voter.id)]['wins'] += 1
#     writeJson("info", serverJson)
#     await savePollState(number, pollMsg)

#     makeWinChart()


def getCorrect(member: discord.Member):
    serverJson = openJson("info")
    return serverJson['users'][str(member.id)]['wins'] 


def adjustWins(member: discord.Member, change):
    serverJson = openJson("info")
    serverJson['users'][str(member.id)]['wins'] += change
    writeJson("info" ,serverJson)
    makeWinChart()


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
