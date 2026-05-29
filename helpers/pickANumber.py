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

NUMBER_VOTING_USERS = 5

async def startNumberPoll(channel: discord.channel, hours: int, minutes: int, real: bool):
    # prepare timings
    est_tz = zoneinfo.ZoneInfo("America/New_York")
    start_time = datetime.now(est_tz)
    pollEndTime = start_time + timedelta(hours=hours, minutes=minutes)

    # set up poll
    poll_duration = hours
    if minutes > 0:
        poll_duration += 1
    numberPoll = discord.Poll(question=f"Pick a Number (Poll only lasts {hours + minutes/60:.2f} Hours)", duration=timedelta(hours=poll_duration, minutes=1))
    for i in range(10):
        numberPoll = discord.Poll.add_answer(self=numberPoll ,text=str(i+1))

    # send poll
    pollMsg = await channel.send(content = "<@&1329614215962689643>", poll=numberPoll)
    
    # Save poll state to file for background monitoring
    poll_data = {
        "message_id": pollMsg.id,
        "channel_id": channel.id,
        "end_time": pollEndTime.timestamp(),
        "warn_1h": False,
        "warn_10m": False,
        "real": real
    }
    if hours * 60 + minutes <= 10:
        poll_data["warn_10m"] = True
    if hours * 60 + minutes <= 60:
        poll_data["warn_1h"] = True
    DiscordJson.write("active_poll", poll_data)


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
        for voter in voters:
            try:
                payload = {"user":  str(voter.id)}
                requests.post("http://localhost:8000/message", json=payload)
            except:
                print("[PAN_ERROR] Failed to send win notification to Sarver")
        await savePollState(number, pollMsgFetched)


async def monitorActivePoll(bot):
    try:
        poll_data = DiscordJson.open("active_poll")
    except Exception:
        return # No active poll saved or file does not exist

    if not poll_data or "message_id" not in poll_data:
        return
        
    channel = bot.get_channel(poll_data["channel_id"])
    if not channel:
        print("[PAN_ERROR] Channel not found")
        return
        
    try:
        pollMsg = await channel.fetch_message(poll_data["message_id"])
    except discord.NotFound:
        DiscordJson.write("active_poll", {}) # Message deleted, clear state
        print("[PAN_ERROR] Poll message not found")
        return
        
    est_tz = zoneinfo.ZoneInfo("America/New_York")
    now = datetime.now(est_tz).timestamp()
    time_left = poll_data["end_time"] - now
    
    allVotes = pollMsg.poll.total_votes >= NUMBER_VOTING_USERS
        
    if allVotes or time_left <= 0:
        if allVotes:
            await channel.send("Everyone has chosen their Number")
        await rollNumber(channel=channel, pollMsg=pollMsg, real=poll_data["real"])
        DiscordJson.write("active_poll", {}) # Clear active poll and exit
        return
        
    if time_left <= 3600 and not poll_data.get("warn_1h"):
        await channel.send(content="<@&1329614215962689643> 1 Hour Warning")
        poll_data["warn_1h"] = True
        DiscordJson.write("active_poll", poll_data)
        
    elif time_left <= 600 and not poll_data.get("warn_10m"):
        await channel.send(content="<@&1329614215962689643> 10 Minute Warning")
        poll_data["warn_10m"] = True
        DiscordJson.write("active_poll", poll_data)


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
        # await channel.send(f"Error: PAN95")
        with open("error_log.txt", "a") as f:  
            f.write(f"{e}\n")
    return False


def getCorrect(member: discord.Member):
    numberData = DiscordJson.open("numbers")
    wins = 0
    for y, year_data in numberData.items():
        for m, month_data in year_data.items():
            for d, day_data in month_data.items():
                winning_number = str(day_data["number"])
                if str(member.id) in day_data.get(winning_number, []):
                    wins += 1
    return wins


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


def modifyDayWin(member: discord.Member, year: int, month: int, day: int, add: bool) -> bool:
    numbers_data = DiscordJson.open("numbers")
    y, m, d = str(year), str(month), "{:02d}".format(day)
    
    if y in numbers_data and m in numbers_data[y] and d in numbers_data[y][m]:
        day_data = numbers_data[y][m][d]
        winning_number = str(day_data["number"])
        
        if add: 
            if str(member.id) not in day_data[winning_number]:
                day_data[winning_number].append(str(member.id))
                DiscordJson.write("numbers", numbers_data)
                
                try:
                    payload = {"user":  str(member.id)}
                    requests.post("http://localhost:8000/message", json=payload)
                except:
                    print("[PAN_ERROR] Failed to send win notification to Sarver")
                return True
        else:
            if str(member.id) in day_data[winning_number]:
                day_data[winning_number].remove(str(member.id))
                DiscordJson.write("numbers", numbers_data)
                
                return True
    return False
