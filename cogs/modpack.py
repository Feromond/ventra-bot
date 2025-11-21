import discord
from discord.ext import commands, tasks
import aiohttp
import datetime

MODPACK_SLUG = "ventra-modpack"
API_URL = f"https://api.modrinth.com/v2/project/{MODPACK_SLUG}/version"
ROLE_NAME = "Ventra Modpack Updates"
CHANNEL_NAME = "modpack"

class SubscriptionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Subscribe/Unsubscribe", style=discord.ButtonStyle.primary, custom_id="ventra_modpack_sub")
    async def toggle_subscription(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_NAME)
        if not role:
            try:
                role = await interaction.guild.create_role(name=ROLE_NAME, mentionable=True, reason="Modpack update notifications")
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to create the notification role!", ephemeral=True)
                return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"You have unsubscribed from {role.mention}.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"You have subscribed to {role.mention}.", ephemeral=True)

class Modpack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_updates.start()

    def cog_unload(self):
        self.check_updates.cancel()

    @tasks.loop(minutes=1.0)
    async def check_updates(self):
        await self.bot.wait_until_ready()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL) as response:
                    if response.status == 200:
                        versions = await response.json()
                        if versions:
                            await self.process_versions(versions[0])
                    else:
                        print(f"Failed to fetch modpack versions: {response.status}")
            except Exception as e:
                print(f"Error in modpack update loop: {e}")

    async def process_versions(self, latest_version):
        version_number = latest_version['version_number']
        version_name = latest_version['name']
        version_id = latest_version['id']
        date_published = latest_version['date_published']
        changelog = latest_version.get('changelog', 'No changelog available.')
        
        if len(changelog) > 1000:
            changelog = changelog[:990] + "..."

        try:
            dt = datetime.datetime.fromisoformat(date_published.replace('Z', '+00:00'))
            timestamp = int(dt.timestamp())
        except Exception:
            timestamp = int(discord.utils.utcnow().timestamp())

        for guild in self.bot.guilds:
            channel = None
            for ch in guild.text_channels:
                if CHANNEL_NAME in ch.name:
                    channel = ch
                    break
            
            if not channel:
                continue

            # Check for existing status message
            status_msg = None
            async for msg in channel.history(limit=20):
                if msg.author == self.bot.user and msg.embeds and msg.embeds[0].title == "Ventra Modpack Status":
                    status_msg = msg
                    break
            
            embed = discord.Embed(
                title="Ventra Modpack Status",
                url=f"https://modrinth.com/modpack/{MODPACK_SLUG}",
                color=0x42F56C
            )
            embed.add_field(name="Latest Version", value=version_number, inline=True)
            embed.add_field(name="Version Name", value=version_name, inline=True)
            embed.add_field(name="Released", value=f"<t:{timestamp}:R>", inline=False)
            embed.add_field(name="Changelog", value=f"```{changelog}```", inline=False)
            embed.set_footer(text=f"Version ID: {version_id}")

            view = SubscriptionView()

            if status_msg:
                current_footer = status_msg.embeds[0].footer.text
                if current_footer != f"Version ID: {version_id}":
                    await status_msg.edit(embed=embed, view=view)
                    async for msg in channel.history(limit=50):
                        if msg.author == self.bot.user and msg.id != status_msg.id:
                            if "**New Update Available:**" in msg.content:
                                try:
                                    await msg.delete()
                                except discord.HTTPException:
                                    pass

                    # Notify role
                    role = discord.utils.get(guild.roles, name=ROLE_NAME)
                    if role:
                        await channel.send(f"{role.mention} **New Update Available:** {version_number} - {version_name}")
                    else:
                        await channel.send(f"**New Update Available:** {version_number} - {version_name}")
            else:
                await channel.send(embed=embed, view=view)

async def setup(bot):
    bot.add_view(SubscriptionView())
    await bot.add_cog(Modpack(bot))

