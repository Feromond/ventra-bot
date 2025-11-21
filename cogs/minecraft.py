import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
from typing import List

def parse_motd(description) -> str:
    """
    Parses Minecraft MOTD (string or dict) into Discord-compatible ANSI escape codes.
    """
    if isinstance(description, list):
        return "".join(parse_motd(item) for item in description)

    if isinstance(description, dict):
        text = description.get('text', '')
        extra = description.get('extra', [])
        for component in extra:
            if isinstance(component, str):
                text += component
            elif isinstance(component, dict):
                text += parse_motd(component)
        return parse_motd(text)

    if not isinstance(description, str):
        return str(description)

    text = description
    # Normalize delimiters (Minecraft uses §, but plugins/configs often use &)
    text = text.replace('&', '§')
    
    if '§' not in text:
        return text

    # Color map for Minecraft § codes to Discord ANSI codes
    colors = {
        '0': '0;30',   # Black
        '1': '0;34',   # Dark Blue
        '2': '0;32',   # Dark Green
        '3': '0;36',   # Dark Aqua
        '4': '0;31',   # Dark Red
        '5': '0;35',   # Dark Purple
        '6': '0;33',   # Gold
        '7': '0;37',   # Gray
        '8': '1;30',   # Dark Gray (Bold Black)
        '9': '1;34',   # Blue
        'a': '1;32',   # Green
        'b': '1;36',   # Aqua
        'c': '1;31',   # Red
        'd': '1;35',   # Light Purple
        'e': '1;33',   # Yellow
        'f': '1;37',   # White
    }
    
    formats = {
        'l': '1',      # Bold
        'm': '9',      # Strikethrough
        'n': '4',      # Underline
        'o': '3',      # Italic
        'r': '0',      # Reset
    }

    # State
    current_color = '0;37' # Default (Gray/White)
    current_formats = set()
    is_obfuscated = False
    
    parts = text.split('§')
    result = parts[0]
    
    for part in parts[1:]:
        if not part:
            continue
            
        code = part[0].lower()
        content = part[1:]
        
        # Update State
        if code in colors:
            current_color = colors[code]
            current_formats.clear()
            is_obfuscated = False
        elif code in formats:
            if code == 'r':
                current_color = '0;37' # Reset
                current_formats.clear()
                is_obfuscated = False
            else:
                current_formats.add(formats[code])
        elif code == 'k':
            is_obfuscated = True
        else:
            # Invalid code, treat as text
            result += f"§{code}{content}"
            continue
            
        if content:
            if is_obfuscated:
                result += "✨" * len(content)
            else:
                style_parts = ['0', current_color]
                if current_formats:
                    style_parts.extend(current_formats)
                
                style = ";".join(style_parts)
                result += f"\u001b[{style}m{content}"
                
    return result

class Minecraft(commands.Cog, name="Minecraft"):
    def __init__(self, bot):
        self.bot = bot
        self.update_status.start()

    def cog_unload(self):
        self.update_status.cancel()

    @commands.hybrid_command(name="status", description="Check the status of a Minecraft server.")
    @discord.app_commands.describe(server_ip="The IP address of the server (e.g., ventra.dev)")
    async def status(self, context: commands.Context, server_ip: str):
        """
        Check the status of a Minecraft server.
        Usage: /status <server_ip>
        """
        await context.typing()
        
        try:
            server = await JavaServer.async_lookup(server_ip)
            status = await server.async_status()
            
            embed = discord.Embed(
                title=f"Minecraft Server Status: {server_ip}",
                color=0x42F56C
            )
            embed.add_field(name="Status", value="Online", inline=True)
            embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=True)
            embed.add_field(name="Latency", value=f"{round(status.latency)}ms", inline=True)
            embed.add_field(name="Version", value=status.version.name, inline=False)
            
            motd = parse_motd(status.description)
            embed.add_field(name="MOTD", value=f"```ansi\n{motd}```", inline=False)
            
            await context.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title=f"Minecraft Server Status: {server_ip}",
                description=f"Could not connect to server.\nError: {str(e)}",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @status.autocomplete("server_ip")
    async def status_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[discord.app_commands.Choice[str]]:
        """
        Autocomplete for the server_ip argument.
        """
        servers = ["ventra.dev", "hypixel.net", "mineplex.com"]
        
        return [
            discord.app_commands.Choice(name=server, value=server)
            for server in servers
            if current.lower() in server.lower()
        ][:25] # Discord limits choices to 25

    @commands.hybrid_command(name="player-list", description="Get the list of players currently on a Minecraft server.")
    @discord.app_commands.describe(server_ip="The IP address of the server (e.g., ventra.dev)")
    async def player_list(self, context: commands.Context, server_ip: str):
        """
        Get the list of players currently on a Minecraft server.
        Usage: /player-list <server_ip>
        """
        await context.typing()

        try:
            server = await JavaServer.async_lookup(server_ip)
            status = await server.async_status()
            
            if status.players.sample:
                player_names = [p.name for p in status.players.sample]
                players_str = "\n".join(player_names)
                
                if len(players_str) > 3900:
                    players_str = players_str[:3900] + "\n... and more"

                embed = discord.Embed(
                    title=f"Players on {server_ip}",
                    description=f"**Online:** {status.players.online}/{status.players.max}\n\n**Player List:**\n{players_str}",
                    color=0x42F56C
                )
            else:
                embed = discord.Embed(
                    title=f"Players on {server_ip}",
                    description=f"**Online:** {status.players.online}/{status.players.max}\n\nNo players listed (or player list is hidden).",
                    color=0x42F56C
                )
            
            await context.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title=f"Error querying {server_ip}",
                description=f"Could not connect or retrieve player list.\nError: {str(e)}",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @player_list.autocomplete("server_ip")
    async def player_list_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[discord.app_commands.Choice[str]]:
        """
        Autocomplete for the server_ip argument.
        """
        servers = ["ventra.dev", "hypixel.net", "mineplex.com"]
        return [
            discord.app_commands.Choice(name=server, value=server)
            for server in servers
            if current.lower() in server.lower()
        ][:25]

    @tasks.loop(minutes=1.0)
    async def update_status(self):
        """
        Background task to update the server status in the 'server-status' channel.
        """
        await self.bot.wait_until_ready()
        
        target_server = "ventra.dev"
        
        for guild in self.bot.guilds:
            channel = None
            for ch in guild.text_channels:
                if "server-status" in ch.name or "server_status" in ch.name:
                    channel = ch
                    break
            
            if channel:
                try:
                    try:
                        server = await JavaServer.async_lookup(target_server)
                        status = await server.async_status()
                        
                        embed = discord.Embed(
                            title=f"Server Status: {target_server}",
                            description="Updated every 1 minute.",
                            color=0x42F56C
                        )
                        embed.add_field(name="Status", value="🟢 Online", inline=True)
                        embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=True)
                        embed.add_field(name="Latency", value=f"{round(status.latency)}ms", inline=True)
                        embed.add_field(name="Version", value=status.version.name, inline=False)
                        
                        description = status.description
                        motd = parse_motd(description)
                        embed.add_field(name="MOTD", value=f"```ansi\n{motd}```", inline=False)
                        
                        embed.set_footer(text=f"Last Updated: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
                        
                    except Exception as e:
                        embed = discord.Embed(
                            title=f"Server Status: {target_server}",
                            description=f"🔴 Offline or Unreachable\nError: {str(e)}",
                            color=0xE02B2B
                        )
                        embed.set_footer(text=f"Last Updated: {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

                    last_message = None
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            last_message = message
                            break
                    
                    if last_message:
                        await last_message.edit(embed=embed)
                    else:
                        await channel.send(embed=embed)
                        
                except Exception as e:
                    print(f"Error updating server status in guild {guild.name}: {e}")

    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Minecraft(bot))

