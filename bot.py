import json
import os
import platform
import sys
import random
import certifi

# Fix SSL context for macOS - MUST be done before importing discord/aiohttp
os.environ["SSL_CERT_FILE"] = certifi.where()

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json") as file:
        config = json.load(file)

# Load environment variables from .env file
load_dotenv()

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None,
        )
        self.config = config

    async def setup_hook(self) -> None:
        """
        This will be executed when the bot starts, before the cache is ready.
        """
        print(f"Logged in as {self.user.name}")
        print(f"discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
        print("-------------------")
        
        await self.load_extensions()

    async def load_extensions(self) -> None:
        """
        Loads all extensions from the cogs directory.
        """
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                extension_name = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(extension_name)
                    print(f"Loaded extension: {extension_name}")
                except Exception as e:
                    print(f"Failed to load extension {extension_name}.")
                    print(f"{type(e).__name__}: {e}")

    async def on_ready(self) -> None:
        """
        This code runs when the bot is fully ready and the cache is populated.
        """
        print(f"Bot is ready! Logged in as {self.user}")
        print("-------------------")
        
        await self.change_presence(activity=discord.Game(name=f"Type {self.config['prefix']}help"))

    async def on_message(self, message: discord.Message) -> None:
        """
        This event triggers on every message. 
        We need to process commands manually here if we overwrite on_message.
        """
        if message.author == self.user or message.author.bot:
            return
            
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        """
        The code in this event is executed every time a normal command has been *successfully* executed.
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        print(f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")

    async def on_command_error(self, context: Context, error) -> None:
        """
        The code in this event is executed every time a valid command catches an error.
        """
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="You are not the owner of the bot!",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            print(f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot.")
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `" + ", ".join(error.missing_permissions) + "` to execute this command!",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `" + ", ".join(error.missing_permissions) + "` to fully perform this command!",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
             embed = discord.Embed(
                title="Error!",
                description=str(error).capitalize(),
                color=0xE02B2B
            )
             await context.send(embed=embed)
        else:
            raise error


if __name__ == "__main__":
    bot = DiscordBot()
    
    # Add a sync command to register slash commands
    @bot.command()
    @commands.is_owner()
    async def sync(ctx):
        """Syncs slash commands globally. Use carefully."""
        # Sync to the current guild (immediate update for testing)
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} command(s) to this guild immediately!")
        
        # Sync globally (takes up to an hour)
        # await bot.tree.sync() 

    # Helper to clear commands if things get stuck
    @bot.command()
    @commands.is_owner()
    async def clearsync(ctx):
        bot.tree.clear_commands(guild=ctx.guild)
        await bot.tree.sync(guild=ctx.guild)
        await ctx.send("Cleared guild commands.")

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        print("Please create a .env file with DISCORD_TOKEN=your_token_here")
    else:
        bot.run(token)
