import json
import os


class DiscordJson():

    def open(fileName):
        serverInfoFileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/{fileName}.json"
        with open(serverInfoFileName, 'r') as serverInfoFile:
            jsonData = json.load(serverInfoFile)
        return jsonData

    def write(fileName, jsonData):
        serverInfoFileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/{fileName}.json"
        with open(serverInfoFileName, 'w') as serverInfoFile:
            json.dump(jsonData, serverInfoFile, sort_keys=True, indent=4)