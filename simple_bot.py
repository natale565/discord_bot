import discord
import random
import os
from dadjokes import Dadjoke
from discord import Intents
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
weather_api = os.getenv('WEATHER_API')

intents = Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

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
    '!weather': 'type !weather and your city for the local weather'

}


@client.event
async def on_message(message):
    if message.author == client.user:
        return


    elif message.content.lower() == '!help':
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
        time = datetime.now().strftime("%A, %B %d, %Y %H:%M:%S %p")
        await message.channel.send(time)
    
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

    elif message.content.lower().startswith('!rsp'):
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
        weather = ' '.join(parts[1:])

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