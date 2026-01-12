import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import pickANumber

BACKEND_CHANNEL = 1186399351073935384

class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

  
    @commands.hybrid_command(name='status')
    async def status(self, ctx: Context):
        await ctx.reply('On the fun work train') # fix this


    # starts number of day manually
    @commands.hybrid_command(name='start-number')
    async def startNumber(self, ctx: Context, hours: int, minutes: int, real: bool):
        await ctx.reply("Manual Number Mode")
        await pickANumber.startNumberPoll(channel=ctx.channel, hours=hours, minutes=minutes, real=real)

    @commands.hybrid_command(name="random-check")
    async def randomCheck(self, ctx: Context, sample_size: int):
        if sample_size > 100000000:
            sample_size = 100000000

        embed = discord.Embed(title=f"Random Check for {sample_size} Picks")
        embed.add_field(
            name='Generating :arrows_counterclockwise:',
            value='',
            inline=False
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1349998544139849798/1349999462818250752/image.png?ex=67d52479&is=67d3d2f9&hm=c1cbd13ff3225d16af82882b5a0ce6be66e7dc01c6a31f2743122acfe87f2fbd&')
        msg = await ctx.reply(embed=embed)
        embed.clear_fields()

        fileName = pickANumber.makeRandomCheckGraph(sample_size)

        file = discord.File(fileName, filename="randomCheck.png")
        backEnd: discord.channel = self.bot.get_channel(BACKEND_CHANNEL)
        backEndMsg: discord.Message = await backEnd.send(file=file)
        url = backEndMsg.attachments[0].url

        embed.set_image(url=url)
        await msg.edit(embed=embed)


    # runs number if number never got chosen, but poll was sent?
    @commands.hybrid_command(name='fix-number')
    async def fixNumber(self, ctx: Context, msg_id, real: bool):
        await ctx.reply("David was on the fun work train")
        pollMsg = await ctx.channel.fetch_message(msg_id)
        await pickANumber.rollNumber(channel=ctx.channel, pollMsg=pollMsg, real=real)


async def setup(bot):
    await bot.add_cog(General(bot))
