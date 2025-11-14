import discord
from discord.ext import commands
from discord import app_commands
import logging
import os
from dotenv import load_dotenv
import sys

for logger_name in ["discord", "discord.gateway", "discord.client", "discord.http"]:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
logging.basicConfig(level=logging.CRITICAL)

TOKEN = input("Enter your Discord bot token: ")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Syntaxa(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="+", intents=intents)
    
    async def on_ready(self):
        print(f"[+] Bot connected: {self.user}")

bot = Syntaxa()

@bot.event
async def on_member_join(member):
    role = member.guild.get_role(1388984894692130969)
    if role:
        await member.add_roles(role)
        print(f"[+] Assigned role {role} to {member} on join")

bot.remove_command("help")

@bot.command(name="help")
async def help_bot(ctx):
    embed = discord.Embed(title="📖 Command List", description="Here are all available commands:", color=0xFFFFFF)
    embed.add_field(name="🛡️ Moderation", value="`+kick <member> [reason]`\n`+ban <member> [reason]`\n`+tempban <member> <time> [reason]`\n`+unban <member>`\n`+mute <member> [duration]`\n`+unmute <member>`", inline=False)
    embed.add_field(name="📡 Channel Management", value="`+lock-channel <channel>`\n`+unlock-channel <channel>`\n`+purge <amount>`", inline=False)
    embed.add_field(name="🎭 Role Management", value="`+add-role <member> <role>`\n`+remove-role <member> <role>`", inline=False)
    embed.add_field(name="ℹ️ Information", value="`+server-info`\n`+user-info <member>`\n`+roles`\n`+ping`", inline=False)
    await ctx.send(embed=embed)
    print(f"[+] {ctx.author} requested help")

@help_bot.error
async def help_error(ctx, error):
    embed = discord.Embed(title="[!] Error", description="An unexpected error occurred while displaying help.", color=0xFFFFFF)
    await ctx.send(embed=embed)
    print(f"[!] Help command error: {error}")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title="[+] Kick Successful", color=0xFFFFFF)
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason if reason else "No reason provided.", inline=False)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} kicked {member} | Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        embed = discord.Embed(title="[!] Error", description="I do not have permission to kick this user.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] {ctx.author} tried to kick {member} but lacks permissions.")
    except discord.HTTPException:
        embed = discord.Embed(title="[!] Error", description="An unexpected error occurred while trying to kick the user.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Failed to kick {member} due to HTTPException.")

@kick.error
async def kick_error(ctx, error):
    embed = discord.Embed(title="[!] Error", description=str(error), color=0xFFFFFF)
    await ctx.send(embed=embed)
    print(f"[!] Kick command error: {error}")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title="[+] Ban Successful", color=0xFFFFFF)
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason if reason else "No reason provided.", inline=False)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} banned {member} | Reason: {reason if reason else 'No reason provided.'}")
    except discord.Forbidden:
        embed = discord.Embed(title="[!] Error", description="I do not have permission to ban this user.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] {ctx.author} tried to ban {member} but lacks permissions.")
    except discord.HTTPException:
        embed = discord.Embed(title="[!] Error", description="An unexpected error occurred while trying to ban the user.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Failed to ban {member} due to HTTPException.")

@ban.error
async def ban_error(ctx, error):
    embed = discord.Embed(title="[!] Error", description=str(error), color=0xFFFFFF)
    await ctx.send(embed=embed)
    print(f"[!] Ban command error: {error}")

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, target: str):
    try:
        banned_entry = None
        import re
        id_match = re.search(r"(\d{17,19})", target)
        uid = int(id_match.group(1)) if id_match else None
        name = discrim = None
        if "#" in target and not uid:
            try:
                name, discrim = target.rsplit("#", 1)
            except ValueError:
                name = None
        async for entry in ctx.guild.bans():
            user = entry.user
            if uid and user.id == uid:
                banned_entry = entry
                break
            if name and discrim and user.name == name and user.discriminator == discrim:
                banned_entry = entry
                break
            if not uid and not (name and discrim) and user.name.lower() == target.lower():
                banned_entry = entry
                break
        if banned_entry is None:
            embed = discord.Embed(title="[!] Error", description="User not found in the ban list.", color=0xFFFFFF)
            await ctx.send(embed=embed)
            print(f"[!] {ctx.author} tried to unban {target} but user not found.")
            return
        await ctx.guild.unban(banned_entry.user)
        embed = discord.Embed(title="[+] User Unbanned", description=f"`{banned_entry.user}` ({banned_entry.user.id}) has been unbanned.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} unbanned {banned_entry.user}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=f"{e}", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Unban command error: {e}")

@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    role = ctx.guild.get_role(1438837179026509847)
    if role is None:
        embed = discord.Embed(title="[!] Error", description="Mute role not found.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        return
    try:
        await member.add_roles(role, reason=reason)
        embed = discord.Embed(title="[+] User Muted", color=0xFFFFFF)
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason if reason else "No reason provided.", inline=False)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} muted {member} | Reason: {reason if reason else 'No reason provided.'}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Mute command error: {e}")

@bot.command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = ctx.guild.get_role(1438837179026509847)
    if role is None:
        embed = discord.Embed(title="[!] Error", description="Mute role not found.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        return
    if role not in member.roles:
        embed = discord.Embed(title="[!] Error", description=f"{member.mention} is not muted.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] {ctx.author} tried to unmute {member} but user was not muted.")
        return
    try:
        await member.remove_roles(role)
        embed = discord.Embed(title="[+] User Unmuted", color=0xFFFFFF)
        embed.add_field(name="User", value=member.mention, inline=False)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} unmuted {member}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Unmute command error: {e}")

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    role = ctx.guild.get_role(1388984894692130969)
    if role is None:
        embed = discord.Embed(title="[!] Error", description="Specified role not found.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        return
    try:
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False
        await channel.set_permissions(role, overwrite=overwrite)
        embed = discord.Embed(title="[+] Channel Locked", description=f"{channel.mention} has been locked for members.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} locked {channel}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Lock command error: {e}")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    role = ctx.guild.get_role(1388984894692130969)
    if role is None:
        embed = discord.Embed(title="[!] Error", description="Specified role not found.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        return
    try:
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = True
        await channel.set_permissions(role, overwrite=overwrite)
        embed = discord.Embed(title="[+] Channel Unlocked", description=f"{channel.mention} is now unlocked for members.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} unlocked {channel}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Unlock command error: {e}")

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = None):
    try:
        if amount is None:
            deleted = await ctx.channel.purge(limit=None)
            embed = discord.Embed(title="[+] Channel Cleared", description=f"All messages in {ctx.channel.mention} have been deleted ({len(deleted)} messages).", color=0xFFFFFF)
            await ctx.send(embed=embed, delete_after=5)
        else:
            deleted = await ctx.channel.purge(limit=amount)
            embed = discord.Embed(title="[+] Messages Deleted", description=f"{len(deleted)} messages have been deleted in {ctx.channel.mention}.", color=0xFFFFFF)
            await ctx.send(embed=embed, delete_after=5)
        print(f"[+] {ctx.author} deleted {len(deleted)} messages in {ctx.channel}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Purge command error: {e}")

@bot.command(name="add-role")
@commands.has_permissions(manage_roles=True)
async def add_role(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.add_roles(role)
        embed = discord.Embed(title="[+] Role Added", description=f"{role.mention} has been added to {member.mention}.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} added role {role} to {member}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Add-role command error: {e}")

@bot.command(name="remove-role")
@commands.has_permissions(manage_roles=True)
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    try:
        if role not in member.roles:
            embed = discord.Embed(title="[!] Error", description=f"{member.mention} does not have the role {role.mention}.", color=0xFFFFFF)
            await ctx.send(embed=embed)
            print(f"[!] {ctx.author} tried to remove {role} from {member} but member does not have it")
            return
        await member.remove_roles(role)
        embed = discord.Embed(title="[+] Role Removed", description=f"{role.mention} has been removed from {member.mention}.", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} removed role {role} from {member}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Remove-role command error: {e}")

@bot.command(name="server-info")
async def server_info(ctx):
    try:
        guild = ctx.guild
        embed = discord.Embed(title=f"[+] Server Info: {guild.name}", color=0xFFFFFF)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Server ID", value=guild.id, inline=False)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
        embed.add_field(name="Members", value=guild.member_count, inline=False)
        embed.add_field(name="Roles", value=len(guild.roles), inline=False)
        embed.add_field(name="Channels", value=len(guild.channels), inline=False)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} viewed server info")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Server-info command error: {e}")

@bot.command(name="user-info")
async def user_info(ctx, member: discord.Member):
    try:
        embed = discord.Embed(title=f"[+] User Info: {member.display_name}", color=0xFFFFFF)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Display Name", value=member.display_name, inline=False)
        embed.add_field(name="Username", value=str(member), inline=False)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Status", value=str(member.status).title(), inline=False)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
        embed.add_field(name="Highest Role", value=member.top_role.mention, inline=False)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} viewed info of {member}")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] User-info command error: {e}")

@bot.command(name="roles")
async def roles(ctx):
    try:
        roles_list = [role.mention for role in ctx.guild.roles if role != ctx.guild.default_role]
        roles_text = ", ".join(roles_list) if roles_list else "No roles available."
        embed = discord.Embed(title="[+] Server Roles", description=roles_text, color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} viewed server roles")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Roles command error: {e}")

@bot.command(name="ping")
async def ping(ctx):
    try:
        latency = round(bot.latency * 1000)
        embed = discord.Embed(title="[+] Pong!", description=f"Latency: `{latency}ms`", color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[+] {ctx.author} used ping | Latency: {latency}ms")
    except Exception as e:
        embed = discord.Embed(title="[!] Error", description=str(e), color=0xFFFFFF)
        await ctx.send(embed=embed)
        print(f"[!] Ping command error: {e}")

@bot.command(name="stop")
@commands.is_owner()
async def stop_bot(ctx):
    embed = discord.Embed(title="[+] Bot Shutting Down", description="The bot is shutting down...", color=0xFFFFFF)
    await ctx.send(embed=embed)
    print(f"[+] {ctx.author} stopped the bot")
    await bot.close()
    sys.exit(0)

@stop_bot.error
async def stop_error(ctx, error):
    embed = discord.Embed(title="[!] Error", description=str(error), color=0xFFFFFF)
    await ctx.send(embed=embed)
    print(f"[!] Stop command error: {error}")

bot.run(TOKEN)
