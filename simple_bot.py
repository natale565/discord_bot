import json
import discord
import random
import os
from dadjokes import Dadjoke
from discord import Intents
from datetime import datetime
from dotenv import load_dotenv
import requests
import time

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
weather_api = os.getenv('WEATHER_API')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

def load_data():
    if os.path.exists('levels.json'):
        with open('levels.json', 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}  # return empty dict if file is empty/broken
    else:
        return {}
    
def save_data(data):
    with open('levels.json', 'w') as f:
        json.dump(data, f, indent=4)

levels = load_data()

XP_COOLDOWN = 10
XP_PER_MESSAGE = 10
LEVEL_UP_XP = 100


# Level system will be integrated into the main on_message handler below

@client.event
async def on_ready():
    print('bot is online!')

bot_responses = {
    '!hello': 'Hi there!',
    '!bye': 'See ya later!',
    '!offended': "I'm offended that you are offended by the offensive thing that offended you. Even though what offended you wasn't offensive and you're just soft.",
    
}

commands = {
    '!hello': 'have the bot say hello',
    '!bye': 'have the bot say goodbye',
    '!offended': 'are you offended? tell the bot.',
    '!echo': 'Bot will echo back your message',
    '!dadjoke': 'For your daily dad joke',
    '!coinflip': 'self explanatory',
    '!rps': 'Play some rock, paper, scissors!',
    '!weather': 'type !weather and your city for the local weather',
    '!level': 'Check your current level and XP'

}

# twitch notification 
@client.event
async def on_member_update(before, after):
    print(f"[on_member_update] {after.name} updated.")
    print(f"[on_member_update] Before activities: {[type(a) for a in before.activities]}")
    print(f"[on_member_update] After activities: {[type(a) for a in after.activities]}")

    for activity in after.activities:
        if isinstance(activity, discord.Streaming):
            print(f"[on_member_update] {after.name} is streaming: {activity}")
            if not any(isinstance(a, discord.Streaming) for a in before.activities):
                print(f"[on_member_update] {after.name} was not previously streaming. Attempting to send notification.")
                channel = discord.utils.get(after.guild.text_channels, name="going-live")
                if channel:
                    await channel.send(f"🚨 {after.mention} just went live! Watch here: {activity.url}")
                    print(f"[on_member_update] Notification sent to #going-live.")
                else:
                    print(f"[on_member_update] Channel 'going-live' not found.")



@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Level system - handle XP and leveling up
    user_id = str(message.author.id)
    if user_id not in levels:
        print(f"[level] New user detected: {user_id}")
        levels[user_id] = {'xp': 0, 'level': 1, 'last_xp': 0}

    current_time = time.time()
    updated = False

    if current_time - levels[user_id].get('last_xp', 0) >= XP_COOLDOWN:
        levels[user_id]['xp'] += XP_PER_MESSAGE
        levels[user_id]['last_xp'] = current_time
        print(f"[level] {message.author} gained XP. Total XP: {levels[user_id]['xp']}")
        updated = True

    # Check for level up
    required_xp = levels[user_id]['level'] * LEVEL_UP_XP
    if levels[user_id]['xp'] >= required_xp:
        levels[user_id]['level'] += 1
        levels[user_id]['xp'] = 0  # Reset XP after level up
        print(f"[level] {message.author} leveled up to {levels[user_id]['level']}!")
        await message.channel.send(f"🎉 Congratulations {message.author.mention}, you've leveled up to level {levels[user_id]['level']}!")
        updated = True

    if updated:
        save_data(levels)
        print(f"[level] Data saved for user {user_id}.")

    # help command for a list of available commands
    if message.content.lower() == '!help':
        embed = discord.Embed(
            title="🤖 Bot Commands",
            description="Here are all the commands you can use:",
            color=discord.Color.blue()
        )

        for cmd, desc in commands.items():
            embed.add_field(name=cmd, value=desc, inline=False)

        await message.channel.send(embed=embed)

    elif message.content.lower() in bot_responses:
        await message.channel.send(bot_responses[message.content.lower()])

    elif message.content.lower().startswith('!echo'):
        parts = message.content.split()
        echo_text = ' '.join(parts[1:])
        await message.channel.send(echo_text)
    
    elif message.content.lower() == '!time':
        current_time_str = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S %p")
        await message.channel.send(current_time_str)
    
    elif message.content.lower() == '!dadjoke':
        dadjoke = Dadjoke()
        await message.channel.send(dadjoke.joke)
    
    elif message.content.lower() == '!coinflip':
        choices = ['Heads', 'Tails']
        parts = message.content.split()
        result = random.choice(choices).lower()

        if len(parts) > 1:
            if parts[1].lower() == result.lower():
                await message.channel.send(f"🎉 You guessed right! It was {result.capitalize()}!")
            else:
                await message.channel.send(f"Nope, it was {result.capitalize()}!")
        else: 
            await message.channel.send(result.capitalize())

    elif message.content.lower().startswith('!rps'):
        parts = message.content.split()
        choices = ['rock', 'paper', 'scissors']

        if len(parts) < 2:
            await message.channel.send('You need to pick rock, paper, or scissors!')
            return

        user_choice = parts[1].lower()
        comp_choice = random.choice(choices)

        if user_choice not in choices:
            await message.channel.send('Invalid input')
            return

        # dictionary of winning rules
        wins = {
            'rock': 'scissors',
            'paper': 'rock',
            'scissors': 'paper'
        }

        if user_choice == comp_choice:
            await message.channel.send(f'You picked {user_choice}, computer picked {comp_choice}. It\'s a tie!')
        elif wins[user_choice] == comp_choice:
            await message.channel.send(f'You picked {user_choice}, computer picked {comp_choice}. You win!')
        else:
            await message.channel.send(f'You picked {user_choice}, computer picked {comp_choice}. You lose!')

    elif message.content.lower() == '!level':
        user_id = str(message.author.id)
        if user_id in levels:
            current_level = levels[user_id]['level']
            current_xp = levels[user_id]['xp']
            required_xp = current_level * LEVEL_UP_XP
            progress = (current_xp / required_xp) * 100
            
            embed = discord.Embed(
                title=f"📊 {message.author.display_name}'s Level",
                color=discord.Color.gold()
            )
            embed.add_field(name="Level", value=current_level, inline=True)
            embed.add_field(name="XP", value=f"{current_xp}/{required_xp}", inline=True)
            embed.add_field(name="Progress", value=f"{progress:.1f}%", inline=True)
            
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("You haven't earned any XP yet! Start chatting to level up!")

    # crypto ticker command
    elif message.content.lower().startswith('!crypto'):
        parts = message.content.split()

        if len(parts) < 2:
            await message.channel.send('Please provide a coin. Example: !crypto bitcoin')
        else:
            coin = parts[1].lower()
            url = f'https://api.coingecko.com/api/v3/coins/{coin}'

            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                market_data = data.get("market_data", {})
                if market_data:
                    price = market_data["current_price"]["usd"]
                    change_24h = market_data["price_change_percentage_24h"]
                    market_cap = market_data["market_cap"]["usd"]
                    volume_24h = market_data["total_volume"]["usd"]

                    await message.channel.send(
                        f"📊 **{data['name']} ({data['symbol'].upper()})**\n"
                        f"💰 Price: ${price:,.2f}\n"
                        f"📉 24h Change: {change_24h:.2f}%\n"
                        f"🏦 Market Cap: ${market_cap:,.0f}\n"
                        f"📊 24h Volume: ${volume_24h:,.0f}"
                        )
                else:
                    await message.channel.send(f"❌ No market data found for `{coin}`.")
            except Exception as e:
                print(f"Crypto API error: {e}")
                await message.channel.send("⚠️ Unable to fetch crypto prices right now. Please try again later.")
        


    elif message.content.lower().startswith('!horoscope'):
        parts = message.content.split()

        if len(parts) < 2:
            await message.channel.send('Please provide your zodiac sign. Example: !horoscope leo')
            return

        sign = ' '.join(parts[1:])

        valid_signs = [
            "aries", "taurus", "gemini", "cancer", "leo", "virgo",
            "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
        ]

        if sign.lower() not in valid_signs:
            await message.channel.send("That’s not a valid zodiac sign. Try again!")
            return

        try:
            # API needs POST with params, not query string
            response = requests.post(
                "https://aztro.sameerkumar.website/",
                params={"sign": sign.lower(), "day": "today"},
                timeout=5
            )
            response.raise_for_status()

            print("Status code:", response.status_code)
            print("Response content:", response.text[:200])  # Limit to first 200 chars


            data = response.json()
            horoscope_text = data['description']

            await message.channel.send(f"Horoscope for {sign.title()}: {horoscope_text}")

        except Exception as e:
            await message.channel.send("Sorry, I couldn’t fetch your horoscope right now 🌌")
            print("Horoscope error:", e)





    elif message.content.lower().startswith('!weather'):
        parts = message.content.split()
        weather = ' '.join(parts[1:]).lower()

        API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={weather}&appid={weather_api}&units=imperial'

        response = requests.get(API_URL)
        data = response.json()

        if response.status_code == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            await message.channel.send(f'Weather in {weather}: {temp}°F, {description}')
        else:
            await message.channel.send(f"Couldn't find weather for {weather}")

      



client.run(TOKEN)