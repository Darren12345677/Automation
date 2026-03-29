"""
main.py — entry point. Run this file to start the bot.
 
    python main.py
"""
 
import asyncio
import logging
 
logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
    ],
)
from bot import run
 
if __name__ == "__main__":
    asyncio.run(run())