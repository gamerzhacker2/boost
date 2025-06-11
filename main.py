import asyncio
import discord
from discord.ext import commands, tasks
from discord import app_commands
import tls_client
import threading
import os
import requests
from base64 import b64encode
import json
from typing import Optional
from datetime import datetime, timezone
import secrets
from pystyle import Center, Colorate, Colors
from colorama import init, Fore, Style
import pystyle
from pystyle import Write, Colors
import time

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Clear file function
def clear_file(file_path):
    try:
        with open(file_path, "w") as file:
            file.truncate(0)
    except FileNotFoundError:
        pass
try:
    os.system("cls")
except:
    pass

ascii_art = """
██████╗  ██████╗  ██████╗ ███████╗████████╗    ██████╗  ██████╗ ████████╗
██╔══██╗██╔═══██╗██╔═══██╗██╔════╝╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║██║   ██║███████╗   ██║       ██████╔╝██║   ██║   ██║   
██╔══██╗██║   ██║██║   ██║╚════██║   ██║       ██╔══██╗██║   ██║   ██║   
██████╔╝╚██████╔╝╚██████╔╝███████║   ██║       ██████╔╝╚██████╔╝   ██║   
╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝   ╚═╝       ╚═════╝  ╚═════╝    ╚═╝    
"""
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
BUILD_NUMBER = 165486
CV = "108.0.0.0"
BOT_TOKEN = config['BOT_TOKEN']
CLIENT_SECRET = config['CLIENT_SECRET']
CLIENT_ID = config['CLIENT_ID']
REDIRECT_URI = "http://localhost:8080"
API_ENDPOINT = 'https://canary.discord.com/api/v9'
AUTH_URL = f"https://canary.discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds.join"
BOT_INVITE =f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=67108865&integration_type=0&scope=bot"
ALLOWED_USER_IDS = [1088731835959357450]
SUPER_PROPERTIES = b64encode(
    json.dumps(
        {
            "os": "Windows",
            "browser": "Chrome",
            "device": "PC",
            "system_locale": "en-GB",
            "browser_user_agent": USER_AGENT,
            "browser_version": CV,
            "os_version": "10",
            "referrer": "https://discord.com/channels/@me",
            "referring_domain": "discord.com",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": BUILD_NUMBER,
            "client_event_source": None
        },
        separators=(',', ':')).encode()).decode()

def get_headers(token):
    headers = {
        "Authorization": token,
        "Origin": "https://canary.discord.com",
        "Accept": "*/*",
        "X-Discord-Locale": "en-GB",
        "X-Super-Properties": SUPER_PROPERTIES,
        "User-Agent": USER_AGENT,
        "Referer": "https://canary.discord.com/channels/@me",
        "X-Debug-Options": "bugReporterEnabled",
        "Content-Type": "application/json"
    }
    return headers

def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(f"{API_ENDPOINT}/oauth2/token",
                      data=data,
                      headers=headers)
    if r.status_code in (200, 201, 204):
        return r.json()
    else:
        return False

def add_to_guild(access_token, userID, guild):
    url = f"{API_ENDPOINT}/guilds/{guild}/members/{userID}"
    botToken = BOT_TOKEN
    data = {
        "access_token": access_token,
    }
    headers = {
        "Authorization": f"Bot {botToken}",
        'Content-Type': 'application/json'
    }
    r = requests.put(url=url, headers=headers, json=data)
    return r.status_code

def rename(token, guild, nickname):
    headers = get_headers(token)
    client = tls_client.Session(client_identifier="firefox_102")
    client.headers.update(headers)
    r = client.patch(
        f"https://canary.discord.com/api/v9/guilds/{guild}/members/@me",
        json={"nick": nickname})
    if r.status_code in (200, 201, 204):
        return "ok"
    else:
        return "error"

def authorizer(token, guild, nickname):
    headers = get_headers(token)
    r = requests.post(AUTH_URL, headers=headers, json={"authorize": "true"})
    if r.status_code in (200, 201, 204):
        location = r.json()['location']
        code = location.replace(F"{REDIRECT_URI}?code=", "")
        exchange = exchange_code(code)
        access_token = exchange['access_token']
        userid = get_user(access_token)
        add_to_guild(access_token, userid, guild)
        if nickname:
            threading.Thread(target=rename, args=(token, guild, nickname)).start()
        return "ok"

def get_user(access: str):
    endp = "https://canary.discord.com/api/v9/users/@me"
    r = requests.get(endp, headers={"Authorization": f"Bearer {access}"})
    rjson = r.json()
    return rjson['id']

def main(token, guild, nickname=None):
    authorizer(token, guild, nickname)
    headers = get_headers(token)
    client = tls_client.Session(client_identifier="firefox_102")
    client.headers.update(headers)
    r = client.get(
        f"https://canary.discord.com/api/v9/users/@me/guilds/premium/subscription-slots"
    )
    idk = r.json()
    for x in idk:
        id_ = x['id']
        payload = {"user_premium_guild_subscription_slot_ids": [id_]}
        r = client.put(
            f"https://canary.discord.com/api/v9/guilds/{guild}/premium/subscriptions",
            json=payload)
        if r.status_code in (200, 201, 204):
            print(f"[+] Boosted {guild}")

            if nickname:
                rename(token, guild, nickname)

    return "ok"

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')    
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(f"An error occurred during command sync: {e}")
        synced = []
    text1 = f"Boost Bot connected with {bot.user}"
    text2 = f"Loaded {len(synced)} Commands"
    print(Colorate.Horizontal(Colors.red_to_black, Center.XCenter(ascii_art)))
    print(Colorate.Horizontal(Colors.red_to_black, Center.XCenter(text1)))
    print(Colorate.Horizontal(Colors.red_to_black, Center.XCenter(text2)))
    activity = discord.Activity(type=discord.ActivityType.watching, name=".gg/notspy")
    await bot.change_presence(activity=activity)

def is_allowed_user():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id in ALLOWED_USER_IDS:
            return True
        embed = discord.Embed(title="Permission Denied", description="You are not allowed to use this command.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
    return app_commands.check(predicate)

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="boost")
@is_allowed_user()
async def boost(
    interaction: discord.Interaction,
    guild_id: str,
    num_tokens: int,
    token_type: str,
    nickname: str = None
):
    if not guild_id or num_tokens <= 0:
        embed = discord.Embed(title="Invalid Arguments", description="Please provide a valid server ID and the number of boosts.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    if token_type not in ["1m", "3m"]:
        embed = discord.Embed(title="Invalid Token Type", description="Please specify '1m' for 1-month tokens or '3m' for 3-month tokens.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    file_name = f"{token_type}tokens.txt"

    try:
        with open(file_name, "r") as f:
            tokens = f.readlines()
    except FileNotFoundError:
        embed = discord.Embed(title="File Not Found", description=f"The file {file_name} does not exist.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    if len(tokens) < num_tokens:
        embed = discord.Embed(title="Insufficient Tokens", description=f"Not enough tokens available. Requested: {num_tokens}, Available: {len(tokens)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    boosting_embed = discord.Embed(title="Boosting Server", description=f"Starting to apply {2 * num_tokens} boost(s) to server ID: {guild_id}. This may take a while...", color=discord.Color.from_rgb(255, 105, 180))
    await interaction.response.send_message(embed=boosting_embed)

    successful_boosts = 0
    used_tokens = []

    for i in range(num_tokens):
        token = tokens[i].strip()
        if ":" in token:
            try:
                token = token.split(":")[2]
            except IndexError:
                await interaction.followup.send(f"Invalid token format: {token}")
                continue

        result = await interaction.client.loop.run_in_executor(executor, main, token, guild_id, nickname)

        if result == "ok":
            successful_boosts += 1
            used_tokens.append(tokens[i])

    remaining_tokens = tokens[num_tokens:]
    with open(file_name, "w") as f:
        f.writelines(remaining_tokens)

    if successful_boosts == num_tokens:
        embed = discord.Embed(title="Boosting Completed", description=f"Successfully applied boost(s) to server ID: {guild_id} with no failures.", color=discord.Color.from_rgb(255, 105, 180))
    else:
        embed = discord.Embed(title="Boosting Partial Success", description=f"Applied {successful_boosts} boost(s) to server ID: {guild_id}. Some tokens may have failed.", color=discord.Color.orange())

    await interaction.followup.send(embed=embed)

    if used_tokens:
        dm_embed = discord.Embed(
            title="Tokens Used for Boosting",
            description="Here are the tokens used to successfully boost the server:",
            color=discord.Color.blue()
        )
        dm_embed.add_field(name="Tokens", value="\n".join(used_tokens), inline=False)

        try:
            await interaction.user.send(embed=dm_embed)
        except discord.Forbidden:
            embed = discord.Embed(title="Failed", description=f"Could not send DM with the used tokens. The user may have DMs disabled.", color=discord.Color.red)            
            await interaction.followup.send(embed=embed)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="add_token")
@is_allowed_user()
@app_commands.describe(token="The token to add", token_type="The type of token ('1m' for 1-month tokens, '3m' for 3-month tokens)")
async def add_token(interaction: discord.Interaction, token: str, token_type: str):
    if not token or token_type not in ["1m", "3m"]:
        embed = discord.Embed(title="Missing or Invalid Arguments", description="Please provide the required token and specify the type ('1m' or '3m').", color=discord.Color.red())
        embed.add_field(name="Command Usage", value="/add_token <token> <token_type>")
        await interaction.response.send_message(embed=embed)
        return

    file_name = f"{token_type}tokens.txt"

    with open(file_name, "a") as f:
        f.write(f"{token}\n")
    await interaction.response.send_message(f"Token added to {file_name}: {token}")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="remove_token")
@is_allowed_user()
@app_commands.describe(token="The token to remove", token_type="The type of token ('1m' for 1-month tokens, '3m' for 3-month tokens)")
async def remove_token(interaction: discord.Interaction, token: str, token_type: str):
    if not token or token_type not in ["1m", "3m"]:
        embed = discord.Embed(title="Missing or Invalid Arguments", description="Please provide the required token and specify the type ('1m' or '3m').", color=discord.Color.red())
        embed.add_field(name="Command Usage", value="/remove_token <token> <token_type>")
        await interaction.response.send_message(embed=embed)
        return

    file_name = f"{token_type}tokens.txt"

    with open(file_name, "r") as f:
        tokens = f.readlines()
    tokens = [t.strip() for t in tokens if t.strip() != token]
    with open(file_name, "w") as f:
        f.write("\n".join(tokens) + "\n")
    await interaction.response.send_message(f"Token removed from {file_name}: {token}")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="list_tokens")
@is_allowed_user()
@app_commands.describe(token_type="The type of tokens to list ('1m' for 1-month tokens, '3m' for 3-month tokens)")
async def list_tokens(interaction: discord.Interaction, token_type: str):
    if token_type not in ["1m", "3m"]:
        embed = discord.Embed(title="Invalid Token Type", description="Please specify '1m' for 1-month tokens or '3m' for 3-month tokens.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    file_name = f"{token_type}tokens.txt"

    try:
        with open(file_name, "r") as f:
            tokens = f.readlines()
    except FileNotFoundError:
        embed = discord.Embed(title="File Not Found", description=f"The file {file_name} does not exist.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if tokens:

        await interaction.response.send_message(content="Listing tokens...", ephemeral=True)

        def split_into_chunks(text_list, max_length=4096):
            current_chunk = ""
            for line in text_list:
                if len(current_chunk) + len(line) > max_length:
                    yield current_chunk
                    current_chunk = line
                else:
                    current_chunk += line
            if current_chunk:
                yield current_chunk

        for chunk in split_into_chunks(tokens):
            embed = discord.Embed(
                title=f"{token_type.upper()} Tokens",
                description=chunk,
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(title=f"{token_type.upper()} Tokens", description="No tokens found.", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="file_restock")
@is_allowed_user()
@app_commands.describe(file="The file containing tokens to restock", token_type="The type of tokens to restock ('1m' for 1-month tokens, '3m' for 3-month tokens)")
async def file_restock(interaction: discord.Interaction, file: discord.Attachment, token_type: str):
    if token_type not in ["1m", "3m"]:
        embed = discord.Embed(title="Invalid Token Type", description="Please specify '1m' for 1-month tokens or '3m' for 3-month tokens.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    try:
        file_content = await file.read()

        content_str = file_content.decode('utf-8').strip()
        tokens = [line.strip() for line in content_str.splitlines() if line.strip()]
    except Exception as e:
        embed = discord.Embed(title="File Error", description=f"Failed to read the file: {str(e)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    file_name = f"{token_type}tokens.txt"

    with open(file_name, "a") as f:

        for token in tokens:
            f.write(f"{token}\n")

    await interaction.response.send_message(f"Tokens restocked from {file.filename} to {file_name}")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="stock")
async def stock(interaction: discord.Interaction):
    try:
        with open("1mtokens.txt", "r") as f:
            one_month_tokens = len(f.readlines())
    except FileNotFoundError:
        one_month_tokens = 0
    try:
        with open("3mtokens.txt", "r") as f:
            three_month_tokens = len(f.readlines()) 
    except FileNotFoundError:
        three_month_tokens = 0

    embed = discord.Embed(
        title="Token Stock",
        description="Current token stocks:",
        color=discord.Color.from_rgb(255, 105, 180)
    )
    embed.add_field(name="1-Month Tokens", value=str(one_month_tokens), inline=False)
    embed.add_field(name="3-Month Tokens", value=str(three_month_tokens), inline=False)

    await interaction.response.send_message(embed=embed)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="cleartokens")
@is_allowed_user()
@app_commands.describe(token_type="The type of tokens to clear ('1m' for 1-month tokens, '3m' for 3-month tokens)")
async def cleartokens(interaction: discord.Interaction, token_type: str):
    if token_type not in ["1m", "3m"]:
        embed = discord.Embed(title="Invalid Token Type", description="Please specify '1m' for 1-month tokens or '3m' for 3-month tokens.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    file_name = f"{token_type}tokens.txt"

    try:

        open(file_name, "w").close()
        embed = discord.Embed(title="Tokens Cleared", description=f"All tokens in {file_name} have been cleared.", color=discord.Color.from_rgb(255, 105, 180))
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"Failed to clear tokens: {str(e)}", color=discord.Color.red())

    await interaction.response.send_message(embed=embed)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name="give_token")
@is_allowed_user()
@app_commands.describe(
    amount="The number of tokens to give",
    token_type="The type of tokens ('1m' for 1-month, '3m' for 3-month)",
    user="The user to give the tokens to"
)
async def give_token(interaction: discord.Interaction, amount: int, token_type: str, user: discord.User):
    if not token_type in ["1m", "3m"]:
        embed = discord.Embed(title="Invalid Token Type", description="Please specify '1m' for 1-month tokens or '3m' for 3-month tokens.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    if amount <= 0:
        embed = discord.Embed(title="Invalid Amount", description="Please specify a valid number of tokens.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    file_name = f"{token_type}tokens.txt"
    try:
        with open(file_name, "r") as f:
            tokens = f.readlines()
    except FileNotFoundError:
        embed = discord.Embed(title="File Not Found", description=f"The file {file_name} does not exist.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    if len(tokens) < amount:
        embed = discord.Embed(title="Insufficient Tokens", description=f"Not enough tokens available. Required: {amount}, Available: {len(tokens)}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    tokens_to_give = tokens[:amount]

    remaining_tokens = tokens[amount:]
    with open(file_name, "w") as f:
        f.writelines(remaining_tokens)

    tokens_str = ''.join(tokens_to_give)
    embed = discord.Embed(title="Tokens Received", description=f"You have received {amount} token(s) of type {token_type}.", color=discord.Color.from_rgb(255, 105, 180))
    embed.add_field(name="Tokens", value=f"```\n{tokens_str}\n```", inline=False)

    try:
        await user.send(embed=embed)
        confirmation_message = f"Successfully sent {amount} token(s) of type {token_type} to {user.mention}."
    except discord.Forbidden:
        confirmation_message = f"Failed to send tokens to {user.mention}. They might have DMs disabled."

    admin_embed = discord.Embed(title="Tokens Given", description=confirmation_message, color=discord.Color.from_rgb(255, 105, 180))
    await interaction.response.send_message(embed=admin_embed)


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name='start_stock_update', description="Start live stock updates for tokens.")
@is_allowed_user()
@app_commands.describe(channel_id="The channel ID to send live stock updates.")
async def start_stock_update(interaction: discord.Interaction, channel_id: str):

    channel = bot.get_channel(int(channel_id))
    if not channel:
        await interaction.response.send_message("Invalid channel ID!")
        return

    live_stock_update.start(channel_id)
    await interaction.response.send_message(f"Live stock updates started in channel <#{channel_id}>.")

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name='invite', description="Sends a bot invite link.")
@is_allowed_user()
async def invite(interaction: discord.Interaction):
    invite_embed = discord.Embed(
        title="Bot invite link",
        description=f"[**__Click here to invite bot to your server__**]({BOT_INVITE})",
        color=discord.Color.from_rgb(255, 105, 180)
    )    
    await interaction.response.send_message(embed=invite_embed)

@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=True)
@bot.tree.command(name='stop_stock_update', description="Stop live stock updates.")
@is_allowed_user()
async def stop_stock_update(interaction: discord.Interaction):

    live_stock_update.stop()
    await interaction.response.send_message("Live stock updates stopped.")

@tasks.loop(hours=1)  
async def live_stock_update(channel_id):

    channel = bot.get_channel(int(channel_id))
    if not channel:
        print(f"Channel with ID {channel_id} not found.")
        return

    token_file_1m = os.path.join("1mtokens.txt")
    token_file_3m = os.path.join("3mtokens.txt")

    stock_1m = count_tokens_in_file(token_file_1m)
    stock_3m = count_tokens_in_file(token_file_3m)

    stock_embed = discord.Embed(
        title="Live Token Stock Update",
        description="Here is the current stock of tokens:",
        color=discord.Color.from_rgb(255, 105, 180)
    )
    stock_embed.add_field(name="1-Month Nitro Tokens", value=f"{stock_1m} tokens available", inline=False)
    stock_embed.add_field(name="3-Months Nitro Tokens", value=f"{stock_3m} tokens available", inline=False)

    await channel.send(embed=stock_embed)


def count_tokens_in_file(file_path):
    """Helper function to count the number of tokens in a given file."""
    if not os.path.exists(file_path):
        return 0  

    with open(file_path, 'r') as file:
        tokens = file.readlines()

    return len(tokens)  

bot.run(BOT_TOKEN)