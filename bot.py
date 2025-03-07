import discord
import asyncio
from discord.ext import tasks
import datetime
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CALENDAR_ID = os.getenv("CALENDAR_ID")  # ID twojego kalendarza

# Konfiguracja Google Calendar API
SERVICE_ACCOUNT_FILE = "credentials.json"  # Plik JSON z kluczem serwisowym
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=credentials)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(minutes=1)
async def check_events():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    future = (datetime.datetime.utcnow() + datetime.timedelta(minutes=30)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        timeMax=future,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if events:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            for event in events:
                start_time = event["start"].get("dateTime", event["start"].get("date"))
                await channel.send(f"📢 Wydarzenie za 30 minut: **{event['summary']}** o {start_time}")

@client.event
async def on_ready():
    print(f"✅ Zalogowano jako {client.user}")
    check_events.start()

client.run(TOKEN)
