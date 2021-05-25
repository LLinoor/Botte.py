# Botte.py

Simple bot Discord coded in Python

## What does the bot do?

Here is a list of what the bot does:

- Ban (and unban) users
- Temporarily mutes users
- Kick users
- Gives the R6S stats of the requested players
- Gives the Beat Saber stats of the requested players
- Gives the osu! stats of the requested players
- Make heads or tails
- Provides statistics on COVID-19
- Delete a requested number of messages
- Gives price of cryptocurrency

## Command Prefix :
Please use "?" before typing the command (ex: `?help`)

## Add the bot to your Discord server:

There are several ways to add the bot to your Discord server, you can host it by yourself (to have full control over it, deploy your own version, ...) or use the already hosted version (for people who don't want/can't host the bot, or who want to use the bot as it is)

### Without hosting the bot :

You can add the bot to your Discord server, however since the bot is hosted on Heroku, it will only be online 23/30 days.

Invitation link : https://discord.com/oauth2/authorize?client_id=708796959628198071&scope=bot&permissions=268463126

<details><summary>Hosted vs GitHub version</summary>
<p>
<i>If some features are reserved for the hosted version it's to not complicate the code with things that people might not use</i>

- The hosted version has a Firebase database to save people's in-game username (in order to facilitate the use of !osu, !bs, ...), with that they just have to use ?osu to get their stats and are not obliged to put their username anymore
</p>
</details>

(The version already hosted is constantly updated and the requested permissions are required for the good functioning of the commands)

### By hosting the bot :

You can host the bot yourself, but you have to install the required dependencies on the bot. 
#### Requirements : 
- [Python](https://www.python.org/downloads/)
- `pip install -r requirements.txt` or `pip3 install -r requirements.txt`