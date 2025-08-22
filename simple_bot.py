import discord
import os
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