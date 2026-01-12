import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import stats

from typing import Literal

year_options = stats.getYearOptions()

class Statcoms(commands.Cog, name="statcoms"):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name='win-graph')
    async def winGraph(self, ctx:Context, year: Literal[*year_options] = year_options[-1]):
        if not year.isdigit():
            year = None
            
        fileName = stats.makeWinChart(year)
        with open(fileName, 'rb') as f:
            plot = discord.File(f)
        await ctx.reply(file=plot)


    @commands.hybrid_command(name='number-stats')
    async def NumberStats(self, ctx: Context, year: Literal[*year_options] = year_options[-1]): # type: ignore

        embed = discord.Embed(
            title=f"{year} Number Stats",
            description=""
        )
        # add stats loading
        embed.add_field(
            name='Retrieving Last Picked Data :arrows_counterclockwise:',
            value='',
            inline=False
        )
        embed.add_field(
            name='Retrieving Times Picked Data :arrows_counterclockwise:',
            value='',
            inline=False
        )
        embed.add_field(
            name='Retrieving Other :arrows_counterclockwise:',
            value='',
            inline=False
        )

        if not year.isdigit():
            year = None

        # initial reply
        msg: discord.Message = await ctx.reply(embed=embed)

        # get first stat
        lastNumberData = stats.NumberStats.getLastNumberData(year)
        
        # Change field
        embed.set_field_at(
            index=0,
            name='Retrieved Last Picked Data :white_check_mark:',
            value='',
            inline=False
        )
        await msg.edit(embed=embed)

        # Get next stat
        timesPickedData = stats.NumberStats.getTimesPicked(year)

        embed.set_field_at(
            index=1,
            name='Retrieved Times Picked Data :white_check_mark:',
            value='',
            inline=False
        )
        await msg.edit(embed=embed)






        # Change field
        embed.set_field_at(
            index=2,
            name='Retrieved Other Data :white_check_mark:',
            value='',
            inline=False
        )
        await msg.edit(embed=embed)

        # prepare to post full stats
        embed.clear_fields()

        for i in range(1,11):
            desc = f"{lastNumberData[i-1]}\n{timesPickedData[i-1]}"
            embed.add_field(
                name=f"{i}:",
                value=desc,
                inline=False
            )

        await msg.edit(embed=embed)
        
        

    @commands.hybrid_command(name='personal-stats')
    async def MemberStats(self, ctx: Context, year: Literal[*year_options] = year_options[-1]): # type: ignore
        embed = discord.Embed(title=f"{year} Personal Stats")
        embed.add_field(name='Retrieving Last Win :arrows_counterclockwise:', value='', inline=False)
        embed.add_field(name='Retrieving Favorite Number :arrows_counterclockwise:', value='', inline=False)
        embed.add_field(name='Retrieving Win Rate :arrows_counterclockwise:', value='', inline=False)
        embed.add_field(name='Retrieving Near Miss Rate :arrows_counterclockwise:', value='', inline=False)
        embed.add_field(name='Retrieving Best Number :arrows_counterclockwise:', value='', inline=False)
        msg: discord.Message = await ctx.reply(embed=embed)

        if not year.isdigit():
            year = None

        memberData = stats.MemberStats(ctx.author, year)

        # get first stat
        lastWin = memberData.getLastWin()
        embed.set_field_at(index=0, name='Retrieved Last Win :white_check_mark:', value='', inline=False)
        await msg.edit(embed=embed)

        # Get next stat
        print('enter')
        mostGuessed = memberData.getMostGuessedNumber()
        print('passed')
        embed.set_field_at(index=1, name='Retrieved Most Guessed Number :white_check_mark:', value='', inline=False)
        await msg.edit(embed=embed)

        # prepare to post full stats
        embed.clear_fields()

        embed.add_field(name='Last Win', value=lastWin, inline=False)
        embed.add_field(name='Favorite Number', value=mostGuessed, inline=False)

        await msg.edit(embed=embed)


    # Server Stats
    ## Longest Streak

async def setup(bot):
    await bot.add_cog(Statcoms(bot))