import discord
from discord.ext import commands
import json, aiohttp
import re
import os, time, re, subprocess
from os import listdir
from os.path import isfile, join
import colorama
from colorama import init
init()
from colorama import Fore, Back, Style


#Get bot token and prefix from json config.
try:
    with open('config.json') as (f):
        data = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("Configuration file not found")
bot = commands.Bot(command_prefix=f'{data["Prefix"]}')
token = data["Token"]
Channel = data["Channel"]
AdministratorRole = data["AdministratorRole"]
Stocks = data["StockChannel"]

#Some shitty variables.
Accounts = []
Codes = "codes.txt"
client = discord.Client()

#Even when bot is turned on.
@bot.event
async def on_ready():
    #Print out text and bot name into console.
    print("  _____             _   _  __         ____        _     _           ")
    print(" / ____|           | | (_)/ _|       |  _ \      | |   | |          ")
    print("| (___  _ __   ___ | |_ _| |_ _   _  | |_) | ___ | |_  | |__  _   _ ")
    print(" \___ \| '_ \ / _ \| __| |  _| | | | |  _ < / _ \| __| | '_ \| | | |")
    print(" ____) | |_) | (_) | |_| | | | |_| | | |_) | (_) | |_  | |_) | |_| |")
    print("|_____/| .__/ \___/ \__|_|_|  \__, | |____/ \___/ \__| |_.__/ \__, |")
    print("       | |                     __/ |                           __/ |")
    print("       |_|                    |___/                           |___/ ")
    print("                 _   _   ")
    print("                | | | |  ")
    print(" _ __ ___   __ _| |_| |_ ")
    print("| '_ ` _ \ / _` | __| __|")
    print("| | | | | | (_| | |_| |_ ")
    print("|_| |_| |_|\__,_|\__|\__|")
    print(Fore.GREEN + f'Bot {bot.user.name} is ready to be used')
    try:
        with open(Codes, "r") as file:
            bot.codes = [code.strip("\n") for code in file.readlines()]
    except FileNotFoundError:
        raise FileNotFoundError(f"{Codes} doesn't exist.")

@bot.command()
@commands.has_role(f'{AdministratorRole}') #Check if user have role you set
async def refresh(ctx): #Refreshing codes, in case they will not be loaded so far
    """ Recheck if new codes are in codes file.
        !refresh - No arguments needed.
    """
    embed = discord.Embed(
        title=f"Codes file refreshed", color=0x00FF00)
    try:
        with open(Codes, "r") as file:
            bot.codes = [code.strip("\n") for code in file.readlines()]
            message = await ctx.send(embed=embed)
    except FileNotFoundError:
        embed = discord.Embed(
            title=f"Codes file doesn't exit, please create new one.", color=0xff5959)
        message = await ctx.send(embed=embed)
        raise FileNotFoundError(f"{Codes} doesn't exist.")
#Redeem command, class where we send invite to user
@bot.command()
async def redeem(ctx, country: str, email: str, code: str):
    """ You can use this command to upgrade your account to premium.
        country - Country you live in, and you have spotify account in.
        email - Your email address, where bot will send invitation link.
        code - Code you've bought/got to upgrade your account.
    """
    if '<' in country: #Checking for <> in Country
        embed = discord.Embed(
            title=f"Please use this command without <>, thanks", color=0xff5959)
        message = await ctx.send(embed=embed)
        return
    if '<' in email: #Checking for <> in Email
        embed = discord.Embed(
            title=f"Please use this command without <>, thanks", color=0xff5959)
        message = await ctx.send(embed=embed)
        return
    if '<' in code: #Checking for <> in Code
        embed = discord.Embed(
            title=f"Please use this command without <>, thanks", color=0xff5959)
        message = await ctx.send(embed=embed)
        return
    await ctx.channel.purge(limit=1) #Deleting message from user (So no one can se his email and shits like that)
    if str(ctx.channel) in Channel:
        if '@' in email: #Check if email is valid
            if code not in bot.codes: #Check if code is in codes.txt (If code is valid)
                embed = discord.Embed(
                    title=f"{ctx.author} That's a bad upgrade key, sorry :/, please try again. It's possible that code wasn't in system so far", color=0xff5959)
                message = await ctx.send(embed=embed)
                try: #Check if code file does exist
                    with open(Codes, "r") as file:
                        bot.codes = [code.strip("\n") for code in file.readlines()]
                        print(Fore.GREEN + 'Codes file refreshed')
                except FileNotFoundError:
                    print(Fore.RED + 'File with codes doesnt exist')
                    raise FileNotFoundError(f"{Codes} doesn't exist.")
                print(Fore.RED + f'@{ctx.author} tried to upgrade with wrong key ({code})')
                return
            else:
                print(Fore.YELLOW + f'@{ctx.author} tried to upgrade with a key ({code})')
                result = 'false'
                embed = discord.Embed(
                    title="Searching for an account...", color=0xffa500)
                message = await ctx.send(embed=embed)
                while result != 'true': #Repeat until user will get invite code/ bot will run out of stocks
                    try: #Check if file with users country exist
                        with open(f"Accounts/{country.upper()}.txt") as filehandle:
                            lines = filehandle.readlines()
                        with open(f"Accounts/{country.upper()}.txt", 'w') as filehandle:
                            lines = filter(lambda x: x.strip(), lines)
                            filehandle.writelines(lines)
                    except FileNotFoundError:
                        embed = discord.Embed(
                            title=f"Sorry, but {country.upper()} is currently out of stock", color=0xff5959)
                        await message.edit(embed=embed)
                        break
                    LastName = "Snow" #First name of invited
                    FirstName = "John" #Last name of invited
                    try:
                        with open('Accounts/'+f'{country.upper()}'+'.txt','r') as (f):
                            for line in f:
                                clean = line.split('\n')
                                Accounts.append(clean[0])
                                lines = f.readlines()
                    except FileNotFoundError:
                        embed = discord.Embed(
                            title=f"Sorry, but We currently don't offer upgrades in this country.", color=0xd3d3d3)
                        await ctx.send(embed=embed)
                    try:
                        account = Accounts.pop()
                        embed = discord.Embed(
                            title="An account has been found.", color=0x00FF00)
                        await message.edit(embed=embed)
                    except IndexError:
                        embed = discord.Embed(
                            title=f"Sorry, but {country.upper()} is currently out of stock.", color=0xff5959)
                        await message.edit(embed=embed)
                        print(Fore.RED + f'{country.upper()} is out of stock')
                        break
                    combo = account.split(':') #Splitting string into list
                    User = combo[0]
                    Pass = combo[1]
                    City = combo[4]
                    ZipCode = combo[3]
                    Address =combo[5]
                    Country = combo[2]
                    embed = discord.Embed(
                        title=f"Trying to send an invite...", color=0xffa500)
                    await message.edit(embed=embed)
                    #Try to login and try to send code to user
                    async with aiohttp.ClientSession() as session:

                        url = 'https://accounts.spotify.com/en/login?continue=https://www.spotify.com/int/account/overview/'
                        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
                        response = await session.get(url, headers=headers)
                        CSRF = session.cookie_jar.filter_cookies(url)[
                            'csrf_token'
                        ].value

                        headers = {
                            'Accept': '*/*',
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1',
                            'Referer': 'https://accounts.spotify.com/en/login/?continue=https://www.spotify.com/us/googlehome/register/&_locale=en-US'
                        }

                        url = 'https://accounts.spotify.com/api/login'

                        credentials = {
                            'remember': 'true',
                            'username': User,
                            'password': Pass,
                            'csrf_token': CSRF
                        }

                        cookies = dict(
                            __bon='MHwwfC0xNDAxNTMwNDkzfC01ODg2NDI4MDcwNnwxfDF8MXwx')

                        postLogin = await session.post(url, headers=headers, data=credentials, cookies=cookies)

                        postLoginJson = await postLogin.json()

                        if 'displayName' in postLoginJson: #If displayName is in source code, then we've successfully logged in.

                            url = "https://www.spotify.com/us/account/overview/"

                            secondLogin = await session.get(url,headers=headers)
                            csrf = secondLogin.headers['X-Csrf-Token']

                            url = 'https://www.spotify.com/us/family/api/master-invite-by-email/'

                            headers = {
                                'Accept': '*/*',
                                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1',
                                'x-csrf-token': csrf
                            }

                            postData = {
                                'firstName': FirstName,
                                'lastName': LastName,
                                'email': email
                            }

                            invitePost = await session.post(url,headers=headers,json=postData)
                            inviteJson = await invitePost.json()

                            print(inviteJson)
                            if inviteJson["success"] is True: #If user was successfully invited to familly plan
                                if not City:
                                    embed = discord.Embed(
                                        title=f"Invitation code was sent, check private messages @{ctx.author}.",color=0x00FF00)
                                    await message.edit(embed=embed)
                                    print(Fore.GREEN + f'@{ctx.author} successfully upgraded his account {email} from {country.upper()} with a key {code}')
                                    await ctx.author.send(f"Please check for an email from Spotify for an invitation link!"
                                                          f"\nFill in these informations in form!"
                                                          f"\n"
                                                          f"\nInvite sent to: {email}"
                                                          f'\n**City**: `You can add random {country.upper()} city`'
                                                          f'\n**Street Name**: `You can add random {country.upper()} street`'
                                                          f'\n**Postal Code**: `You can add random {country.upper()} postal code`'
                                                          f'\n**Country**: `{country.upper()}`'
                                                          f'\n**You can add random {country.upper()} address if these fields are empty.**'
                                                          )
                                    bot.codes.remove(code) #Remove code from codes list after user got invite code.
                                    with open("codes.txt", "a") as file:
                                        file.truncate(0)
                                        for code in bot.codes:
                                            file.write(f"{code}\n")
                                    break
                                else:
                                    embed = discord.Embed(
                                        title=f"Invitation code was sent, check private messages @{ctx.author}.", color=0x00FF00)
                                    await message.edit(embed=embed)
                                    print(Fore.GREEN + f'@{ctx.author} successfully upgraded his account {email} from {country.upper()} with a key {code}')
                                    await ctx.author.send(f"Please check for an email from Spotify for an invitation link!"
                                                               f"\nFill in these informations in form!"
                                                               f"\n"
                                                               f"\nInvite sent to: {email}"
                                                               f'\n**City**: `{City}`'
                                                               f'\n**Street Name**: `{Address}`'
                                                               f'\n**Postal Code**: `{ZipCode}`'
                                                               f'\n**Country**: `{Country}`'
                                                               f'\n**You can add random {country.upper()} address if these fields are empty.**'
                                                               )
                                    bot.codes.remove(code) #Remove code from codes list after user got invite code.
                                    with open("codes.txt", "a") as file:
                                        file.truncate(0)
                                        for code in bot.codes:
                                            file.write(f"{code}\n")
                                    break
                            else: #If user wasn't invited to familly plan so far
                                embed = discord.Embed(
                                    title=f"There were some issues, retrying.", color=0xd3d3d3)
                                await message.edit(embed=embed)
                                with open(f"Accounts/{country}.txt", "w") as f:
                                    for line in lines:
                                        if line.strip("\n") != f"{User}:{Pass}":
                                            f.write(line)
                                result = 'false'
        else: #If email address isn't valid, send this to user.
            embed = discord.Embed(
                title=f"Your email address isn't valid", color=0xff5959)
            message = await ctx.send(embed=embed)
    else: #If user is trying to reedem account in different channel that you've made for.
        embed = discord.Embed(
            title=f"You can only use this command in #{Channel}", color=0xd3d3d3)
        message = await ctx.send(embed=embed)
@bot.command()
async def stock(ctx, country:str):
    """ This command can be used to check current stocks.
        <country> - Country you want to check stocks in.
        Commands:
        !stock <country> - To check stocks for specific country
        !stock all - To check stocks for all countries
    """
    if '<' in country: #Checking for <> in country
        embed = discord.Embed(
            title=f"Please use this command without <>, thanks", color=0xff5959)
        message = await ctx.send(embed=embed)
        return
    print(Fore.YELLOW + f'@{ctx.author} checked stocks for {country.upper()}')
    await ctx.channel.purge(limit=1) #Deleting message.
    if str(ctx.channel) in Stocks:
        if country == 'all': #If command is !stock all then do this
            embed = discord.Embed(title='Current Stocks',
                                  colour=discord.Colour.blue())
            onlyfiles = [f for f in listdir('Accounts') if
                         isfile(join('Accounts', f))]
            for e in onlyfiles:
                num_lines = sum(1 for line in open(f'Accounts/{e}'))
                x = e.replace(".txt", "")
                embed.add_field(name=str(x), value=int(num_lines), inline=True)
            await ctx.send(embed=embed)
        else: #If command is with specific country (ex. !stock US) do this
            try: #Check if file even exist
                with open(f"Accounts/{country.upper()}.txt") as filehandle:
                    lines = filehandle.readlines()
                with open(f"Accounts/{country.upper()}.txt", 'w') as filehandle:
                    lines = filter(lambda x: x.strip(), lines)
                    filehandle.writelines(lines)
                embed = discord.Embed(title='Current Stocks',
                                      colour=discord.Colour.blue())
                num_lines = sum(1 for line in open(f'Accounts/{country}.txt'))
                embed.add_field(name=str(country.upper()), value=int(num_lines), inline=False)
                await ctx.send(embed=embed)
            except FileNotFoundError:
                embed = discord.Embed(
                    title=f"Sorry, but We currently don't offer upgrades in this country.", color=0xd3d3d3)
                await ctx.send(embed=embed)
    else: #If user is in different channel then he have to be
        embed = discord.Embed(
            title=f"Sorry, but you can't check stock channel, please go to #{Stocks}", color=0xd3d3d3)
        await ctx.send(embed=embed)
@bot.command()
@commands.has_role(f'{AdministratorRole}') #Same as before, checking if user have role as admin/mod
async def restock(ctx, file:str):
    """ This command can be used to restock accouts.
        <file> - Name of file in your bot folder you want to restock accounts from. (Without .extension)
        Commands:
        !restock <file> - Use this command to restock accounts from file you have in bot folder.
    """
    await ctx.channel.purge(limit=1) #Deleting message.
    print(Fore.YELLOW + f'@{ctx.author} tried to restock accounts with {file}')
    Line = []
    restocked = 'false'
    embed = discord.Embed(
        title="Restocking....", color=0xffa500)
    message = await ctx.send(embed=embed)
    while restocked != 'true':
        try:
            with open(f'{file}.txt', 'r') as (f):
                for line in f:
                    clean = line.split('\n')
                    Line.append(clean[0])
                    lines = f.readlines()
        except FileNotFoundError:
            embed = discord.Embed(
                title="Restock file doesn't exist", color=0xff5959)
            message = await ctx.send(embed=embed)
            print(Fore.RED + f'@{ctx.author} unsuccessfully restocked accounts with {file}(File doesnt exist)')
            return
        embed = discord.Embed(
            title="Restocking....", color=0xffa500)
        await message.edit(embed=embed)
        try:
            acCountry = Line.pop()
        except IndexError:
            embed = discord.Embed(
                title=f"Restocked", color=0x00FF00)
            await message.edit(embed=embed)
            print(Fore.GREEN + f'@{ctx.author} successfully restocked accounts with {ctx.author})')
            break
        accCountry = acCountry.split(':') #Splitting string into list
        accountCountry = accCountry[2]
        User = accCountry[0]
        Pass = accCountry[1]
        City = accCountry[4]
        ZipCode = accCountry[3]
        Address = accCountry[5]
        Country = accCountry[2]
        restockFile = open(f"Accounts/{accountCountry}.txt", "a+") #Loading lines 1 by 1 into files
        restockFile.write(f'\n{User}:{Pass}:{Country}:{ZipCode}:{City}:{Address}')
        with open(f"{file}.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != f"{User}:{Pass}":
                    f.write(line)

@bot.command()
async def info(ctx):
    """ Just some informations about coder."""
    print(Fore.YELLOW + f'@{ctx.author} used !info')
    await ctx.channel.purge(limit=1)
    await ctx.channel.send(f"```This is opensource spotify upgrade bot made by matt(matoooo),"
                          f"\nI've coded it to practice in Python and to get better in it."
                          f"\nAs said it's opensource, so if you have any problems, just go into code and edit it"
                          f"\nIf you will ever need something from me, just hit me up on Discord matooo#5132"
                           f"\nPlease ignore my broken English, I'm working on it!```"
                          )
bot.run(token)
