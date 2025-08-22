import discord
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
    '!offended': "I'm offended that you are offended by the offensive thing that offended you. Even though what offended you wasn't offensive and you're just soft."
    
}


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    
    
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