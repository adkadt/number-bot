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

from discord import Poll
from helpers.discordJson import DiscordJson


def getNumberData():
    numberData = DiscordJson.open(fileName='numbers')
    return numberData


def __writeNumberData(numberData):
    DiscordJson.write(fileName='numbers', jsonData=numberData)


def __getMemberData():
    memberData = DiscordJson.open(fileName='member')
    return memberData


def __writeMemberData(memberData):
    DiscordJson.write(fileName='member', jsonData=memberData)


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

    def getServerData():
        numberData = getNumberData()

        days = []
        for y, year in numberData.items():
            for m, month in year.items():
                for d, day in month.items():
                    days.append((y,m,d,day['number']))
        
        days = np.array(days)
        numbers = days[:,3]

        # print(days)
        # print(numbers)
        return days, numbers


    def getLastNumberData():
        days, numbers = NumberStats.getServerData()

        lastPickedData = []

        for i in range(1,11):
            lastTime = np.where(numbers == str(i))[0][-1]
            numData = days[lastTime]
            lastPickedData.append(f"Last Picked: {numData[1]}/{numData[2]}/{numData[0]} ({(len(numbers)-1)-lastTime} Days Ago)")

        return lastPickedData


    def getTimesPicked():
        days, numbers = NumberStats.getServerData()

        timesPicked = []

        for i in range(1,11):
            totalDays = len(numbers)
            numTimesPicked = np.count_nonzero(numbers == str(i))
            timesPicked.append(f"Times Picked: {numTimesPicked} ({(numTimesPicked/totalDays)*100:.0f}% of the time)")

        return timesPicked



class MemberStats():

    # win rate
    # near miss
    # best guess number (Most sucessful)
    
    def __init__(self, member: discord.Member):
        self.member = member


    def getLastWin(self):
        numberData = getNumberData()

        days = []
        for y, year in numberData.items():
            for m, month in year.items():
                for d, day in month.items():
                    days.append((y,m,d,day['number'],day[str(day['number'])]))

        lastWin = 'nil'

        for day in reversed(days):
            if str(self.member.id) in day[4]:
                lastWin = f"Date: {day[1]}/{day[2]}/{day[0]}\nNumber: {day[3]}"
                break

        return lastWin
    
    def getMostGuessedNumber(self):
        numberData = getNumberData()

        days = []
        for y, year in numberData.items():
            for m, month in year.items():
                for d, day in month.items():
                    days.append((y,m,d,day['number'],day))

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

        # if len(winRateOfMostGuessed) == 1:
        #     winRateOfMostGuessed = winRateOfMostGuessed[0]

        returnMsg = f"Number: {mostGuessed}\n"
        returnMsg += f"Win Rate: {winRateStr}\n"
        returnMsg += f"Times Used: {numOfMostGuessed:.0f}"

        return returnMsg


    


    def temp():
        print()