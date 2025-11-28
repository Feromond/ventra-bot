"""
Template cog for reference to help me remember how to nicely start a new one.
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from typing import List

class Template(commands.Cog, name="Template"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # --- Simple Command ---
    @commands.hybrid_command(
        name="test",
        description="This is a testing command that does nothing."
    )
    async def test(self, context: Context) -> None:
        """
        This is a testing command that does nothing.
        """
        await context.send("Test command executed!")

#     @commands.hybrid_command(
#         name="simple",
#         description="A simple template command."
#     )
#     async def simple(self, context: Context) -> None:
#         """
#         This is a simple command that just sends a message.
#         """
#         await context.send("Simple command executed!")

#     # --- Complex Command with Arguments & Autocomplete ---
#     @commands.hybrid_command(
#         name="complex",
#         description="A complex template command with arguments."
#     )
#     @discord.app_commands.describe(
#         user="The user to mention",
#         choice="Pick an option"
#     )
#     @commands.guild_only() 
#     async def complex(self, context: Context, user: discord.User, choice: str) -> None:
#         """
#         This command demonstrates arguments, type hinting, and autocomplete.
#         """
#         embed = discord.Embed(
#             title="Complex Command",
#             description=f"User: {user.mention}\nChoice: {choice}",
#             color=0x42F56C
#         )
#         await context.send(embed=embed)

#     @complex.autocomplete("choice")
#     async def complex_autocomplete(
#         self, interaction: discord.Interaction, current: str
#     ) -> List[discord.app_commands.Choice[str]]:
#         """
#         Autocomplete handler for the 'choice' argument.
#         """
#         options = ["Option A", "Option B", "Option C"]
#         return [
#             discord.app_commands.Choice(name=option, value=option)
#             for option in options if current.lower() in option.lower()
#         ]

#     # --- Command with Checks & Error Handling ---
#     @commands.hybrid_command(
#         name="restricted",
#         description="A command that requires specific permissions."
#     )
#     @commands.has_permissions(administrator=True)
#     async def restricted(self, context: Context) -> None:
#         """
#         This command can only be run by administrators.
#         """
#         await context.send("You are an admin!", ephemeral=True)

#     @restricted.error
#     async def restricted_error(self, context: Context, error) -> None:
#         """
#         Local error handler for the restricted command.
#         """
#         if isinstance(error, commands.MissingPermissions):
#             await context.send("You do not have permission to use this command.", ephemeral=True)

async def setup(bot) -> None:
    await bot.add_cog(Template(bot))
