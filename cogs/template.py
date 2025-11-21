import discord
from discord.ext import commands

class Template(commands.Cog, name="Template"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="test", description="This is a testing command that does nothing.")
    async def test(self, context):
        """
        This is a testing command that does nothing.
        """
        await context.send("Test command executed!")

async def setup(bot):
    await bot.add_cog(Template(bot))

