import discord
import random
from discord import app_commands
from discord.ext import commands

class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="List all commands the bot has loaded.")
    async def help(self, context: commands.Context):
        embed = discord.Embed(
            title="Help", description="List of available commands:", color=0x9C84EF
        )
        for cog_name in self.bot.cogs:
            cog = self.bot.get_cog(cog_name)
            
            if cog is None:
                continue
                
            data = []
            
            # 1. Get Standard/Hybrid Commands
            for command in cog.get_commands():
                description = command.description.partition('\n')[0]
                data.append(f"/{command.name} - {description}")

            # 2. Get Slash-Only (App) Commands (like advancedpoll)
            for command in cog.get_app_commands():
                if command.name not in [c.name for c in cog.get_commands()]:
                    description = command.description.partition('\n')[0]
                    data.append(f"/{command.name} - {description}")
            
            if data: # Only add field if the cog has commands
                help_text = "\n".join(data)
                embed.add_field(name=cog_name, value=f'```{help_text}```', inline=False)
                
        await context.send(embed=embed)

    @commands.hybrid_command(name="ping", description="Check if the bot is alive.")
    async def ping(self, context: commands.Context):
        """
        Check if the bot is alive.
        """
        embed = discord.Embed(
            title="Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x42F56C
        )
        await context.send(embed=embed)

    @commands.hybrid_command(name="invite", description="Get the invite link of the bot.")
    async def invite(self, context: commands.Context):
        """
        Get the invite link of the bot to be able to invite it.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here]({self.bot.config['invite_link']}).",
            color=0xD75BF4
        )
        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.guild_only()
    @app_commands.guild_only()
    @commands.hybrid_command(name="server", description="Get information about the server.")
    async def server(self, context: commands.Context):
        """
        Get information about the server.
        """
        embed = discord.Embed(
            title=f"{context.guild.name} Info",
            description="Information of this Server",
            color=random.choice([0x42F56C, 0xD75BF4, 0x000000])
        )
        embed.add_field(name="🆔 Server ID", value=context.guild.id)
        embed.add_field(name="📆 Created On", value=context.guild.created_at.strftime("%b %d %Y"))
        embed.add_field(name="👑 Owner", value=context.guild.owner)
        embed.add_field(name="👥 Members", value=context.guild.member_count)
        embed.set_thumbnail(url=context.guild.icon.url if context.guild.icon else None)
        
        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
