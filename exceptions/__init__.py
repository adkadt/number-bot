from discord.ext import commands

class UserNotOwner(commands.CheckFailure):
    def __init__(self, message="User is not an owner of the bot!"):
        self.message = message
        super().__init__(self.message)