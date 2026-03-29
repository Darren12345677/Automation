"""
generate_session.py — run this once locally to produce a Telethon session string
for use as the TELEGRAM_SESSION environment variable on Railway (or any cloud host).

Usage:
    python generate_session.py

Copy the printed string and paste it into your Railway Variables as TELEGRAM_SESSION.
"""

# import asyncio
# from telethon import TelegramClient
# from telethon.sessions import StringSession
# from config import API_ID, API_HASH


# async def main():
#     async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
#         session_string = client.session.save()
#         print("\n✅ Your session string (copy this into TELEGRAM_SESSION on Railway):\n")
#         print(session_string)
#         print()


# if __name__ == "__main__":
#     asyncio.run(main())
