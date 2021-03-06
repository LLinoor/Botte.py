import discord
from discord.ext import commands
import json
import requests
import random
import time
import asyncio
from requests_html import HTMLSession
from dotenv import load_dotenv
import os
load_dotenv()
discord_key = os.environ.get("discord_key")
osu_api = os.environ.get("osu_key")

client = commands.Bot(command_prefix= '!')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game('mcow.ml/simpsons'))

@client.command(name="covid", brief='| Provides global statistics for COVID-19', aliases=["coronavirus"]) # From https://covid19api.com : "The basic API is free to use and rate limited. Upgrade to a subscription today to get extra data and no rate limit!" (Subscriptions range from $10 to $100.)
async def covid(ctx):
    response = requests.get('https://api.covid19api.com/world/total')
    data = response.json()
    x = data["TotalConfirmed"]  
    y = data["TotalDeaths"]
    z = data["TotalRecovered"]
    a = ("Total number of infected people in the world : "+"{:,}\n".format(x))
    b = ("Total number of dead in the world: "+"{:,}\n".format(y))
    c = ("Total number of people recovered in the world: "+"{:,}\n".format(z))
    await ctx.send(a + b + c)

@client.command(name="hot", description="!hot (number of launches)", brief='| Heads or Tails / Filp a coin', aliases=['fac'])
async def hot(ctx, text):

    try:
        nbPFF = int(text[-1])
    except:
        intOuPas = False
    else:
        intOuPas = True

    POF = ["Heads", "Tails"]
    diceColor = ":game_die:"

    if(intOuPas == True):
        if (nbPFF > 1):
            await ctx.send("Launch of Heads or Tails !")
            nbPOFe = 0
            x = 0
            while x < nbPFF:
                nbPOFe = nbPOFe + 1
                RNG = random.choice(POF)
                try:
                    await ctx.send(str(nbPOFe) + ". Result : " + RNG + "  " + diceColor)
                except:
                    pass
                else:
                    time.sleep(1)
                x += 1

        elif(nbPFF == 1):
                RNG = random.choice(POF)
                await ctx.send("Result : " + RNG + "  " + diceColor)

        elif(nbPFF < 1):
                await ctx.send(":x: Error : Please select a number (between 1 and 9)")
    elif(intOuPas == False):
        await ctx.send(":x: Error : Please select a number (between 1 and 9) (ex: !hot 3)")

@hot.error
async def hot_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        POF = ["Heads", "Tails"]
        diceColor = ":game_die:"
        RNG = random.choice(POF)
        await ctx.send("Result : " + RNG + "  " + diceColor)

@client.command(name="kick", brief='| Kick a member')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot kick yourself")
    try:
        await member.kick(reason=reason)
    except: 
        await ctx.channel.send(f"I do not have permission to kick {member}")
    else:
        await ctx.channel.send(f"{member} has been kicked !")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to perform this action.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention a user !")


@client.command(name="ban", brief='| Ban a member')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
    if(reason == None):
        reason = "Reason unspecified"
    if member == None or member == ctx.message.author:
        await ctx.channel.send("You cannot ban yourself")
        return
    try:
        await member.ban(reason=reason)
    except: 
        await ctx.channel.send(f"I do not have permission to ban {member}")
    else:
        await ctx.channel.send(f"{member} has been banned !")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to perform this action.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention a user !")

@client.command(name="unban", brief='| Unban a member')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, banned:str):
    try:
        realBanned = ""
        mentionBanned = banned
        banned = banned.replace("<","")
        banned = banned.replace("!","")
        banned = banned.replace(">","")
        banned = banned.replace("@","")
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            if (int(ban_entry.user.id) == int(banned)):
                realBanned = ban_entry.user
        
        try:
            await ctx.guild.unban(realBanned)
        except:
            pass
        else:
            await ctx.send(f'Revocation of the ban of {mentionBanned}')
    except:
        banner_users = await ctx.guild.bans()
        banned_name, banned_discriminator = banned.split("#")

        for ban_entry in banner_users:
            user = ban_entry.user

            if(user.name, user.discriminator) == (banned_name, banned_discriminator):
                try:
                    await ctx.guild.unban(user)
                except:
                    await ctx.send(f"Unable to revoke the ban of {user.mention}")
                else:
                    await ctx.send(f'Revocation of the ban of {user.mention}')

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to perform this action.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention a user !")

@client.event
@commands.has_permissions(manage_roles=True)

async def createMutedRole(ctx):
    mutedRole = await ctx.guild.create_role(name = "Muted",
                                            permissions = discord.Permissions(
                                                send_messages = False,
                                                speak = False))
    for channel in ctx.guild.channels:
        await channel.set_permissions(mutedRole, send_messages = False, speak = False)
    return mutedRole

async def getMutedRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Muted":
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages = False, speak = False)
            return role
    
    return await createMutedRole(ctx)

@client.command(name="mute", description='Use like that "!mute @user 30m" (Available arguments: s, m, h, d)', brief='| Temporary mute a member')
async def mute(ctx, member : discord.Member, *, mute_time):

    mutedRole = await getMutedRole(ctx)

    lengthMeesage = len(mute_time)
    lastCharMessage = mute_time[lengthMeesage -1]

    if (lastCharMessage == "s" or lastCharMessage == "S"):
        try:
            baseTime = int(mute_time[:-1])
            if(baseTime == 1):
                await ctx.send(f"Do you really want to mute {member.mention} for 1 second? :face_with_raised_eyebrow:")
                return
        
            await member.add_roles(mutedRole)
            await ctx.send(f"{member.mention} can't talk for {baseTime} seconds")
            await asyncio.sleep(baseTime)
            await member.remove_roles(mutedRole)
            await ctx.send(f"{member.mention} can talk again !")
        except:
            await ctx.send(f"Unable to mute {member}")

    elif (lastCharMessage == "m" or lastCharMessage == "M"):
        try:
            baseTime = int(mute_time[:-1])
            finalTime = baseTime * 60
            await member.add_roles(mutedRole)
            if(baseTime == 1):
                await ctx.send(f"{member.mention} can't talk for {baseTime} minute")
            else:
                await ctx.send(f"{member.mention} can't talk for {baseTime} minutes")
            await asyncio.sleep(finalTime)
            await member.remove_roles(mutedRole)
            await ctx.send(f"{member.mention} can talk again !")
        except:
            await ctx.send(f"Unable to mute {member}")
    
    elif (lastCharMessage == "h" or lastCharMessage == "H"):
        try:
            baseTime = int(mute_time[:-1])
            finalTime = baseTime * 3600
            await member.add_roles(mutedRole)
            if(baseTime == 1):
                await ctx.send(f"{member.mention} can't talk for {baseTime} hour")
            else:
                await ctx.send(f"{member.mention} can't talk for {baseTime} hours")
            await asyncio.sleep(finalTime)
            await member.remove_roles(mutedRole)
            await ctx.send(f"{member.mention} can talk again !")
        except:
            await ctx.send(f"Unable to mute {member}")

    elif (lastCharMessage == "d" or lastCharMessage == "D"):
        try:
            baseTime = int(mute_time[:-1])
            if(baseTime > 30):
                await ctx.send("You cannot go beyond 30 days.")
                return
            finalTime = baseTime * 86400
            await member.add_roles(mutedRole)
            if(baseTime == 1):
                await ctx.send(f"{member.mention} can't talk for {baseTime} day")
            else:
                await ctx.send(f"{member.mention} can't talk for {baseTime} days")
            await asyncio.sleep(finalTime)
            await member.remove_roles(mutedRole)
            await ctx.send(f"{member.mention} can talk again !")
        except:
            await ctx.send(f"Unable to mute {member}")
    else:
        await ctx.send("Indicate a valid duration (e.g. !mute @user 360s (or m for minutes, h for hours and d for days))")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to perform this action.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please fill in the required arguments (e.g. !mute @user 360s (or m for minutes, h for hours and d for days)!")

@client.command(name="unmute", brief='| Unmute an user')
async def unmute(ctx, *, member : discord.Member):
    mutedRole = await getMutedRole(ctx)
    await member.remove_roles(mutedRole)
    await ctx.send(f"{member.mention} can talk again !")
   
@client.command(name="clear", brief='| Clear a number of messages')
@commands.has_permissions(manage_messages=True)
async def clear (ctx, amount:int):
    amount = amount + 1
    if(amount >= 2):
        try:
            await ctx.channel.purge(limit=amount)
        except:
            await ctx.channel.send("Unable to delete messages.")
        else:
            if(amount == 2):
                amount = amount - 1
                message = await ctx.channel.send(f"{amount} deleted message.")
                await asyncio.sleep(2)
                await message.delete()
            else:
                amount = amount - 1
                message = await ctx.channel.send(f"{amount} deleted messages.")
                await asyncio.sleep(2)
                await message.delete()
    elif(amount < 2):
        await ctx.channel.send("Please indicate a positive value (ex: !clear 3)")

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to perform this action.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("How many messages should I delete? (ex: !clear 3)")

@client.command(name="bs", brief='| Beat Saber Stats')
async def bs(ctx, *, user):
        try:
            user = int(user)
            req = requests.get(f'https://new.scoresaber.com/api/player/{user}/full')
            stats = req.json()
            
        except:
            session = HTMLSession()
            URLsearch = f"https://scoresaber.com/global?search={user}"
            search = session.get(URLsearch)

            playersearch = search.html.find("td.player > a", first=True)
            usertmp = str(playersearch.absolute_links)
            user = usertmp.replace("{'https://scoresaber.com/u/", "").replace("'}", "")
            req = requests.get(f'https://new.scoresaber.com/api/player/{user}/full')
            stats = req.json()
            try:
                playerInfo = stats["playerInfo"]
            except: 
                await ctx.send ("Beat Saber user not found !")
                return
            else:
                scoreStats = stats["scoreStats"]
                country = playerInfo["country"]
                flag = f"https://www.countryflags.io/{country.lower()}/flat/64.png"

                rankText = playerInfo["rank"]
                rank = f'{int(rankText):,}' 

                countryRankText = playerInfo["countryRank"]
                countryRank = f'{int(countryRankText):,}' 

                totalScoreText = scoreStats["totalScore"]
                totalScore = f'{int(totalScoreText):,}' 

                totalRankedScoreText = scoreStats["totalRankedScore"]
                totalRankedScore = f'{int(totalRankedScoreText):,}' 

                bsEmbed = discord.Embed(
                    title = (f'{playerInfo["playerName"]}\'s Beat Saber Stats'),
                    description = f'''**Player's stats :**

                    **Username** : {playerInfo["playerName"]}
                    **World Ranking** : {rank}
                    **Ranking {playerInfo["country"]}** : {countryRank}
                    **Number of PPs** : {playerInfo["pp"]}
                    **Number of ban** : {playerInfo["banned"]}

                    **Advanced Stats :**

                    **Total Score** : {totalScore}
                    **Total Ranked Score** : {totalRankedScore}
                    **Number of games played :** : {scoreStats["totalPlayCount"]}
                    **Number of ranked games played** : {scoreStats["rankedPlayCount"]}

                    *(source : https://scoresaber.com/u/{user})*
                    '''
                    )
                bsEmbed.set_footer(text="If the profile does not match try with the profile ID. Data from ScoreSaber.")
                bsEmbed.set_thumbnail(url=f'https://new.scoresaber.com{playerInfo["avatar"]}')
                bsEmbed.set_author(name=f'{playerInfo["playerName"]}', icon_url=flag)
                await ctx.send(embed=bsEmbed)
                session.close()

        else:
            try:
                playerInfo = stats["playerInfo"]
            except: 
                await ctx.send ("Beat Saber user not found !")
                return
            else:
                scoreStats = stats["scoreStats"]
                country = playerInfo["country"]
                flag = f"https://www.countryflags.io/{country.lower()}/flat/64.png"

                rankText = playerInfo["rank"]
                rank = f'{int(rankText):,}' 

                countryRankText = playerInfo["countryRank"]
                countryRank = f'{int(countryRankText):,}' 

                totalScoreText = scoreStats["totalScore"]
                totalScore = f'{int(totalScoreText):,}' 

                totalRankedScoreText = scoreStats["totalRankedScore"]
                totalRankedScore = f'{int(totalRankedScoreText):,}' 

                bsEmbed = discord.Embed(
                    title = (f'{playerInfo["playerName"]}\'s Beat Saber Stats'),
                    description = f'''**Player's stats :**

                    **Username** : {playerInfo["playerName"]}
                    **World Ranking** : {rank}
                    **Ranking {playerInfo["country"]}** : {countryRank}
                    **Number of PPs** : {playerInfo["pp"]}
                    **Number of ban** : {playerInfo["banned"]}

                    **Advanced Stats :**

                    **Total Score** : {totalScore}
                    **Total Ranked Score** : {totalRankedScore}
                    **Number of games played :** : {scoreStats["totalPlayCount"]}
                    **Number of ranked games played** : {scoreStats["rankedPlayCount"]}

                    *(source : https://scoresaber.com/u/{user})*
                    '''
                    )
                bsEmbed.set_footer(text="If the profile does not match try with the profile ID. Data from ScoreSaber.")
                bsEmbed.set_thumbnail(url=f'https://new.scoresaber.com{playerInfo["avatar"]}')
                bsEmbed.set_author(name=f'{playerInfo["playerName"]}', icon_url=flag)
                await ctx.send(embed=bsEmbed)

@client.command(name="spam", description="!spam @user (amount of mention)", brief='| Spam an user')
async def spam(ctx, a:str, *, repeat:int):
    if(repeat <= 25):
        x = 0
        while x < repeat:
            await ctx.send(a)
            x += 1
    else:
        await ctx.send("Please choose a number between 1 and 25 inclusive")


@client.command(name="r6", brief='| R6 Statistics of user')
async def r6(ctx, platform, user):
    if(platform == 'PS4' or platform == "ps4"):
        platform = 'psn'
    elif(platform == 'PC'):
        platform = 'pc'

    session = HTMLSession()
    url = f'https://r6.tracker.network/profile/{platform}/{user}'
    API = session.get(url)

    try:
        rankAPI = API.html.find("div.trn-defstat__value")
        rank = rankAPI[2].text
        rankURL = "N/A"
        isRanked = True

    except:
        errorAPI = API.html.find('div.trn-card__content > div', first=True)
        error = errorAPI.text
        if(error == '404 Not Found. We are unable to find your profile.'):
            await ctx.send("404 Not Found. We are unable to find your profile")
            return

    else:
        try:
            ranking = int(rank[0])
        except:
            isRanked = True
        else:
            isRanked = ranking
            isRanked = False

        seasonURL = f"https://r6.tracker.network/profile/{platform}/{user}/seasons"
        s = session.get(seasonURL)

        userAPI = API.html.find("h1.trn-profile-header__name > span", first=True)
        user = userAPI.text

        avatarAPI = API.html.find("div.trn-profile-header__avatar > img", first=True)
        avatar = avatarAPI.attrs['src']

        MMRAPI = API.html.find("div.trn-text--dimmed")
        MMR = MMRAPI[2].text

        if(isRanked == False):
            rankURL = "https://imgur.com/Ydp4OYF.png"
        elif(rank == "COPPER V"):
            rankURL = "https://imgur.com/B8W0mif.png"
        elif(rank == "COPPER IV"):
            rankURL = "https://imgur.com/jy09RBO.png"
        elif(rank == "COPPER III"):
            rankURL = "https://imgur.com/bhXMzPj.png"
        elif(rank == "COPPER II"):
            rankURL = "https://imgur.com/9qrrbO5.png"
        elif(rank == "COPPER I"):
            rankURL = "https://imgur.com/YXAaQgV.png"
        elif(rank == "BRONZE V"):
            rankURL = "https://imgur.com/ALibyxr.png"
        elif(rank == "BRONZE IV"):
            rankURL = "https://imgur.com/ltaepRn.png"
        elif(rank == "BRONZE III"):
            rankURL = "https://imgur.com/fPOIuOE.png"
        elif(rank == "BRONZE II"):
            rankURL = "https://imgur.com/79m6xRw.png"
        elif(rank == "BRONZE I"):
            rankURL = "https://imgur.com/AuRBzDt.png"
        elif(rank == "SILVER V"):
            rankURL = "https://imgur.com/AtBchfd.png"
        elif(rank == "SILVER IV"):
            rankURL = "https://imgur.com/XLgAD3U.png"
        elif(rank == "SILVER III"):
            rankURL = "https://i.imgur.com/2DfOHpi.png"
        elif(rank == "SILVER II"):
            rankURL = "https://imgur.com/AzL8wmE.png"
        elif(rank == "SILVER I"):
            rankURL = "https://imgur.com/BPnBwKz.png"
        elif(rank == "GOLD III"):
            rankURL = "https://imgur.com/aPSFFOi.png"
        elif(rank == "GOLD II"):
            rankURL = "https://imgur.com/olzd8OF.png"
        elif(rank == "GOLD I"):
            rankURL = "https://imgur.com/b9MIzQL.png"
        elif(rank == "PLATINUM III"):
            rankURL = "https://imgur.com/CSBl6kY.png"
        elif(rank == "PLATINUM II"):
            rankURL = "https://imgur.com/ZPfEeYx.png"
        elif(rank == "PLATINUM I"):
            rankURL = "https://imgur.com/nnLRa3I.png"
        elif(rank == "DIAMOND"):
            rankURL = "https://imgur.com/soXE8up.png"
        elif(rank == "CHAMPION"):
            rankURL = "https://imgur.com/4MeDrk8.png"

        response = API.html.find("div.trn-defstat__value")

        maxrankAdd = response[1].text + " MMR"
        maxrank = maxrankAdd
        level = response[0].text
        TWin = response[6].text
        KD = response[8].text
        Win = response[20].text
        Losses = response[21].text
        response_season = s.html.find("div.trn-defstat__value")
        KDS = response_season[0].text
        WinS = response_season[5].text
        LossesS = response_season[6].text

        try:
            WLD = (int(WinS))/(int(LossesS))
            WL = (round(WLD, 2))
        except:
            WL = "0.00"
        

        SkillAPI = s.html.find("div.r6-season__skill > span")
        Skill = SkillAPI[1].text

        season = "Season"

        if(isRanked == False):
            maxrank = "n/a"
            season = "Casual"
            TWin = response[21].text
            KD = response[7].text
            Win = response[19].text
            Losses = response[20].text
            KD = round(float(KD), 2)
            KDS = round(float(KDS), 2) 

        embed=discord.Embed(title=f"R6 Statistics of {user}", url=f'https://r6.tracker.network/profile/{platform}/{user}', color=0xcc7a1d)
        embed.set_author(name=user, url=f'https://r6.tracker.network/profile/{platform}/{user}', icon_url=avatar)
        embed.set_thumbnail(url=rankURL)
        embed.add_field(name="Rank :", value=f"""**MMR :** {MMR} 
        **Max. MMR :** {maxrank}
        **Level :** {level}""", inline=True)
        embed.add_field(name="Global statistics :", value=f"""**K/D :** {KD}
        **Win :** {Win}
        **Lose :** {Losses}
        **Winrate% :** {TWin}""", inline=True)
        embed.add_field(name=f"{season} statistics :", value=f"""**K/D :** {KDS}
        **W/L :** {WL}
        **Skill :** {Skill}
        """, inline=False)
        embed.set_footer(text=f"https://r6.tracker.network/ for the stats :)")
        try:
            await ctx.send(embed=embed)
        except Exception as e: 
            print(e)
        session.close()


@r6.error
async def r6_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please use the command this way: !R6 (platform) (user) (e.g. !R6 PC D.Linoor)")

def rounder(input, floater):
    return round(input, floater)

@client.command(name="crypto", description="example : !crypto bitcoin (abbreviation unavailable)", brief='| Cryptocurrency overview')
async def crypto(ctx, crypto):
    response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={crypto.lower()}&vs_currencies=usd')
    jsonReturns = json.loads(response.text)
    res = not bool(jsonReturns) 
    if (res):
        await ctx.send("Cryptocurrency not found !")
        return
    temp = jsonReturns[crypto.lower()]

    await ctx.send(f"""Currently, {crypto.capitalize()} is at {temp["usd"]} USD""")

@crypto.error
async def crypto_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            bitcoinAPI = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
            bitcoin = json.loads(bitcoinAPI.text)
            bitcoinUSD = bitcoin['bitcoin']
            EthereumAPI = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
            Ethereum = json.loads(EthereumAPI.text)
            EthereumUSD = Ethereum["ethereum"]
            XRPAPI = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd')
            XRP = json.loads(XRPAPI.text)
            XRPUSD = XRP["ripple"]
            XRPRound = rounder(XRPUSD["usd"], 3)
            LitecoinAPI = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd')
            Litecoin = json.loads(LitecoinAPI.text)
            LitecoinUSD = Litecoin['litecoin']
            TetherAPI = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd')
            Tether = json.loads(TetherAPI.text)
            TetherUSD = Tether['tether']
            TetherRound = rounder(TetherUSD['usd'], 3)
            BATAPI = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=basic-attention-token&vs_currencies=usd')
            BAT = json.loads(BATAPI.text)
            BATUSD = BAT['basic-attention-token']
            BATRound = rounder(BATUSD['usd'], 3)
            embed=discord.Embed(title="Cryptocurrency overview today :", url='https://www.coingecko.com/', color=0x44a832)
            embed.set_author(name="CoinGecko", url='https://www.coingecko.com/', icon_url="https://static.coingecko.com/s/thumbnail-007177f3eca19695592f0b8b0eabbdae282b54154e1be912285c9034ea6cbaf2.png")
            embed.add_field(name="Bitcoin", value=f"""**{bitcoinUSD["usd"]} USD**""", inline=True)
            embed.add_field(name="Ethereum", value=f"""**{EthereumUSD["usd"]} USD**""", inline=True)
            embed.add_field(name="XRP", value=f"""**{XRPRound} USD**""", inline=True)
            embed.add_field(name="Litecoin", value=f"""**{LitecoinUSD["usd"]} USD**""", inline=True)
            embed.add_field(name="Tether", value=f"""**{TetherRound} USD**""", inline=True)
            embed.add_field(name="BAT", value=f"""**{BATRound} USD**""", inline=True)
            embed.set_footer(text="""You can use the command 
!crypto (name of the crypto) to see 
the price of a specific cryptomonnaie""")
            await ctx.send(embed=embed)

@client.command(name="osu", brief='| osu! Statistics of') #This command need an API key from https://osu.ppy.sh/p/api
async def osu(ctx, *, id):
    if(osu_api == "YOUR_OSU_API_TOKEN" or osu_api == ""):
        await ctx.send("(**For the bot manager**) You must enter your osu! token in the .env file.")

    payload = {'k': osu_api, 'u': id}
    response = requests.get('https://osu.ppy.sh/api/get_user', params=payload)
    data = response.json()
    if(len(data) == 0):
        await ctx.send("!osu command : User not found")
        return
    levelText = float(data[0]["level"])
    level = round(levelText)

    playcountText = data[0]["playcount"]
    playcount = f'{int(playcountText):,}' 

    rankedScoreText = data[0]["ranked_score"]
    rankedScore = f'{int(rankedScoreText):,}' 

    totalScoreText = data[0]["total_score"]
    totalScore = f'{int(totalScoreText):,}' 

    ppRawText = data[0]["pp_raw"]
    ppRaw = round(float(ppRawText))

    accuracyText = data[0]["accuracy"]
    accuracy = round(float(accuracyText), 2)

    totalSecondsPlayedText = data[0]["total_seconds_played"]
    totalHoursPlayed = float(totalSecondsPlayedText) / 3600
    totalHoursPlayed = round(totalHoursPlayed)
    totalHoursPlayed = f'{int(totalHoursPlayed):,}'

    country = data[0]["country"]
    flag = f"https://www.countryflags.io/{country.lower()}/flat/64.png"

    user = data[0]["username"]

    userID = data[0]["user_id"]
    avatar = f"http://s.ppy.sh/a/{userID}"

    countRankSS = data[0]["count_rank_ss"]
    countRankSSH = data[0]["count_rank_ssh"]
    countRankSS = int(countRankSS) + int(countRankSSH)
    countRankS = data[0]["count_rank_s"]
    countRankSH = data[0]["count_rank_sh"]
    countRankS = int(countRankS) + int(countRankSH)
    countRankA = data[0]["count_rank_a"]
    count = f"{str(countRankSS)}/{str(countRankS)}/{countRankA}"

    rank = data[0]["pp_rank"]
    rank = f'{int(rank):,}'

    rankCountry = data[0]["pp_country_rank"]
    rankCountry = f'{int(rankCountry):,}'

    url = f"https://osu.ppy.sh/users/{userID}"

    if(totalHoursPlayed == "1" or totalHoursPlayed == "0"): multipleHours = "hour" 
    else: multipleHours = "hours"

    if(playcount == "1" or playcount == "0"): multiplePlays = "game" 
    else: multiplePlays = "games"

    payload = {'k': osu_api, 'u': id}
    response = requests.get('https://osu.ppy.sh/api/get_user_best', params=payload)
    bestScoreData = response.json()

    bestPPListAPI = []
    bestReplaysAPI = []
    tempList = []
    bestScoreIDAPI = []

    attempt = 0
    while attempt <= 2:
        bestPPListAPI.append(bestScoreData[attempt]["pp"])
        tempList.append(bestScoreData[attempt]['replay_available'])
        if int(tempList[attempt]) == 1:
            bestReplaysAPI.append(bestScoreData[attempt]['score_id'])
        else:
            bestReplaysAPI.append("0")
        bestScoreIDAPI.append(bestScoreData[attempt]['score_id'])
        attempt += 1

    bestReplays = []
    for replay in bestReplaysAPI:
        if int(replay) != 0:
            bestReplays.append(f" - [Download Replay](https://osu.ppy.sh/scores/osu/{replay})")
        else:
            bestReplays.append("")

    bestScoreID = []
    for id in bestScoreIDAPI:
        bestScoreID.append(f"https://osu.ppy.sh/scores/osu/{id}")

    bestPPList = []

    for pp in bestPPListAPI:
        pp = round(float(pp))
        bestPPList.append(str(pp) + "pp")

    bestMapList = []

    attempt = 0
    while attempt <= 2:
        bestMapList.append(bestScoreData[attempt]["beatmap_id"])
        attempt += 1

    bestMapStarsAPI = []
    bestMapNames = []
    attempt = 0
    for map in bestMapList:
        payload = {'k': osu_api, 'b': map}
        response = requests.get('https://osu.ppy.sh/api/get_beatmaps', params=payload)
        bestMapData = response.json()
        bestMapStarsAPI.append(bestMapData[0]['difficultyrating'])
        bestMapNames.append(bestMapData[0]['title'])
        if(attempt >= 2):
            pass

    bestMapStars = []
    for star in bestMapStarsAPI:
        star = round(float(star))
        bestMapStars.append(str(star) + "★") 

    embed=discord.Embed(title=f"Stats osu! of {user}", url=url, color=0xbf4040)
    embed.set_author(name=user, url=url, icon_url=flag)
    embed.set_thumbnail(url=avatar)
    embed.add_field(name="User statistics", value=f"""**Username :** {user} 
    **Level :** {level}
    **Number of pp :** {ppRaw}pp""", inline=True)
    embed.add_field(name="Ranking", value=f"""**Global ranking :** {rank}
    **{country} ranking :** {rankCountry}
    **Accuracy :** {accuracy}%""", inline=True)
    embed.add_field(name="Stats :", value=f"""**Number of {multiplePlays} played :** {playcount} {multiplePlays}
    **Number of {multipleHours} played :** {totalHoursPlayed} {multipleHours}
    """, inline=False)
    embed.add_field(name="Score :", value=f"""**Ranked Score :** {rankedScore}
    **Total Score :** {totalScore}
    **Number of SS/S/A :** {count}
    """, inline=False)
    embed.add_field(name="Best score :", value=f"""[{bestMapNames[0]}]({bestScoreID[0]}) (**{bestPPList[0]}** - **{bestMapStars[0]}**{bestReplays[0]})
    [{bestMapNames[1]}]({bestScoreID[1]})  (**{bestPPList[1]}** - **{bestMapStars[1]}**{bestReplays[1]})
    [{bestMapNames[2]}]({bestScoreID[2]}) (**{bestPPList[2]}** - **{bestMapStars[2]}**{bestReplays[2]})
    """, inline=False)
    embed.set_footer(text="Statistics from the official osu! API (v1). If the user does not match your profile you can use your osu! ID (you can find it in the URL on the osu! site by going to your profile (e.g. https://osu.ppy.sh/users/13022778)). (e.g: !osu u 13022778)")
    await ctx.send(embed=embed)
    
@osu.error
async def osu_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please use the command like this: !osu (username) (e.g : !osu Linoor)")

client.run(discord_key)