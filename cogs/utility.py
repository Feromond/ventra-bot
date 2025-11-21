import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="poll", description="Create a simple Yes/No poll.")
    @app_commands.describe(question="The question for the poll")
    async def poll(self, context: commands.Context, *, question: str):
        """
        Create a simple poll with Thumbs Up and Thumbs Down reactions.
        """
        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=0x42F56C
        )
        embed.set_footer(text=f"Poll created by {context.author}")
        
        message = await context.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @commands.hybrid_command(name="userinfo", description="Get information about a user.")
    @app_commands.describe(user="The user to get info about")
    async def userinfo(self, context: commands.Context, user: discord.Member = None):
        """
        Get detailed information about a user (or yourself if no user provided).
        """
        if user is None:
            user = context.author

        embed = discord.Embed(
            title=f"User Info - {user.name}",
            color=user.color
        )
        
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        
        embed.add_field(name="🆔 ID", value=user.id, inline=True)
        embed.add_field(name="🏷️ Nickname", value=user.nick if user.nick else "None", inline=True)
        embed.add_field(name="📅 Account Created", value=user.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="📥 Joined Server", value=user.joined_at.strftime("%b %d, %Y"), inline=True)
        
        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        if len(roles) > 10:
            roles_str = ", ".join(roles[:10]) + f" and {len(roles) - 10} more..."
        else:
            roles_str = ", ".join(roles) if roles else "None"
            
        embed.add_field(name="🎭 Roles", value=roles_str, inline=False)
        
        await context.send(embed=embed)

    @app_commands.command(name="advancedpoll", description="Create an advanced poll with multiple options and custom emojis")
    @app_commands.describe(
        title="The title of the poll",
        option1="First option",
        emoji1="Emoji for first option (optional)",
        option2="Second option",
        emoji2="Emoji for second option (optional)",
        option3="Third option (optional)",
        emoji3="Emoji for third option (optional)",
        option4="Fourth option (optional)",
        emoji4="Emoji for fourth option (optional)",
        option5="Fifth option (optional)",
        emoji5="Emoji for fifth option (optional)",
    )
    async def advanced_poll(
        self, 
        interaction: discord.Interaction, 
        title: str, 
        option1: str, 
        option2: str, 
        emoji1: str = None,
        emoji2: str = None,
        option3: str = None, 
        emoji3: str = None,
        option4: str = None, 
        emoji4: str = None,
        option5: str = None,
        emoji5: str = None
    ):
        """
        Create an advanced poll with up to 5 options and optional custom emojis.
        """
        raw_options = [
            (option1, emoji1),
            (option2, emoji2),
            (option3, emoji3),
            (option4, emoji4),
            (option5, emoji5)
        ]
        
        valid_options = []
        for i, (opt, emo) in enumerate(raw_options):
            if opt:
                default_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][i]
                valid_options.append((opt, emo if emo else default_emoji))

        description = ""
        for option, emoji in valid_options:
            description += f"{emoji} {option}\n\n"
            
        embed = discord.Embed(
            title=f"📊 {title}",
            description=description,
            color=0x42F56C
        )
        embed.set_footer(text=f"Poll created by {interaction.user}")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        for option, emoji in valid_options:
            try:
                await message.add_reaction(emoji)
            except discord.HTTPException:
                await interaction.followup.send(f"Could not add reaction for emoji: {emoji}. Please make sure it is a valid emoji.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
