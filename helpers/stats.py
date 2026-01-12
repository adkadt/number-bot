import asyncio
import discord

import inflect
import random

import os

import numpy as np
import pandas
import matplotlib.pyplot as plt

from datetime import timedelta
import datetime
import pytz
from typing import Literal

from discord import Poll
from helpers.discordJson import DiscordJson


def getNumberData(year=None):
    numberData = DiscordJson.open(fileName='numbers')

    if year is not None:
        for saved_year in list(numberData):
            if str(saved_year) != str(year):
                numberData.pop(saved_year)

    return numberData


def __writeNumberData(numberData):
    DiscordJson.write(fileName='numbers', jsonData=numberData)


def __getServerData():
    memberData = DiscordJson.open(fileName='info')
    return memberData


def __writeServerData(memberData):
    DiscordJson.write(fileName='info', jsonData=memberData)

def getYearOptions() -> list[str]:
    years = list(getNumberData())
    options = ["All Time"] + years
    return options

def makeWinChart(year=None):
    fileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/winGraph.png"
    number_data = getNumberData(year)
    server_data = __getServerData()

    dispNames = []
    user_ids = []
    wins = []
    high = 0

    for user in server_data['users']:
        sub = server_data['users'][user]
        dispNames.append(sub['display_name'])
        user_ids.append(str(user))
    wins = [0] * len(user_ids)

    for y, year_data in number_data.items():
        for m, month_data in year_data.items():
            for d, day_data in month_data.items():
                winning_num = day_data["number"]
                winning_members = day_data[str(winning_num)]
                for member in winning_members:
                    member_index = user_ids.index(member)
                    wins[member_index] += 1

    for win in wins:
        if win > high:
            high = win

    if year is None:
        year = 'All Time'

    plt.xticks(rotation=15)
    plt.bar(dispNames, wins)
    plt.title(f'{year} Correct Number Guesses')

    for i in range(len(dispNames)):
        plt.text(i, wins[i] + high*0.01, wins[i])

    plt.savefig(fileName)
    plt.cla()

    return fileName

class ServerStats():
    # Server win rate
    # Total numbers picked


    def getServerWinRateByDays():
        numberData = getNumberData()
        
        days = []
        for y, year in numberData.items():
            for m, month in year.items():
                for d, day in month.items():
                    days.append(day[str(day['number'])])
        
        print(days)



class NumberStats():

    def getServerData(year_sel=None):
        numberData = getNumberData()
        days = []

        for y, year_data in numberData.items():
            if year_sel is not None:
                if str(y) != str(year_sel):
                    continue

            for m, month_data in year_data.items():
                for d, day_data in month_data.items():
                    days.append((y,m,d,day_data['number']))
        
        if not days:
            return np.array([]), np.array([])

        days = np.array(days)
        numbers = days[:,3]

        # print(days)
        # print(numbers)
        return days, numbers


    def getLastNumberData(year=None):
        days, numbers = NumberStats.getServerData(year)

        lastPickedData = []

        for i in range(1,11):
            search_num = str(i)
            matches = np.where(numbers.astype(str) == search_num)[0]

            if matches.size > 0:
                lastTime = np.where(numbers == str(i))[0][-1]
                numData = days[lastTime]
                days_ago = (len(numbers)-1)-lastTime
                lastPickedData.append(f"Last Picked: {numData[1]}/{numData[2]}/{numData[0]} ({days_ago} Days Ago)")
            else:
                lastPickedData.append(f"Not picked in this time period")

        return lastPickedData


    def getTimesPicked(year=None):
        days, numbers = NumberStats.getServerData(year)
        timesPicked = []

        totalDays = len(numbers)
        if totalDays < 1:
            totalDays = 1

        for i in range(1,11):
            search_num = str(i)
            matches = np.where(numbers.astype(str) == search_num)[0]

            if matches.size > 0:
                numTimesPicked = np.count_nonzero(numbers == str(i))
            else:
                numTimesPicked = 0
            timesPicked.append(f"Times Picked: {numTimesPicked} ({(numTimesPicked/totalDays)*100:.0f}% of the time)")
        return timesPicked



class MemberStats():

    # win rate
    # near miss
    # best guess number (Most sucessful)
    
    def __init__(self, member: discord.Member, year=None):
        self.member = member
        self.numberData = getNumberData(year)


    def getLastWin(self, year_sel=None):
        days = []
        for y, year_data in self.numberData.items():
            for m, month_data in year_data.items():
                for d, day_data in month_data.items():
                    days.append((y,m,d,day_data['number'],day_data[str(object=day_data['number'])]))

        lastWin = 'None during this period'

        for day in reversed(days):
            if str(self.member.id) in day[4]:
                lastWin = f"Date: {day[1]}/{day[2]}/{day[0]}\nNumber: {day[3]}"
                break

        return lastWin
    
    def getMostGuessedNumber(self):
        days = []
        for y, year_data in self.numberData.items():
            for m, month_data in year_data.items():
                for d, day_data in month_data.items():
                    days.append((y,m,d,day_data['number'],day_data))

        guessed = np.zeros(10)
        numWins = np.zeros(10)

        for day in days:
            for i in range(10):
                if str(self.member.id) in day[4][str(i+1)]:
                    guessed[i] += 1
                    if i+1 == day[3]:
                        numWins[i] += 1

        numOfMostGuessed = np.max(guessed)        
        mostGuessedLst = np.where(guessed==numOfMostGuessed)[0]
        mostGuessed = mostGuessedLst + 1
        if len(mostGuessed) == 1:
            mostGuessed = mostGuessed[0]

        winRateStr = ''
        winRateOfMostGuessed = []
        for num in mostGuessedLst:
            winRateOfMostGuessed.append((numWins[num]/numOfMostGuessed)* 100)
        for i, winRate in enumerate(winRateOfMostGuessed):
            if i > 0:
                winRateStr += ', '
            winRateStr += f"{winRate:.0f}%"

        returnMsg = f"Number: {mostGuessed}\n"
        returnMsg += f"Win Rate: {winRateStr}\n"
        returnMsg += f"Times Used: {numOfMostGuessed:.0f}"

        return returnMsg
