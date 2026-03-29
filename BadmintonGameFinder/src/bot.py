"""
bot.py — Telethon client setup, group/topic resolution, and event handler.
"""

import logging
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession


from config import (
    API_ID, API_HASH, ALERT_CHAT,
    WATCH_GROUPS, WATCH_TOPICS, SESSION_FILE,
    SESSION_STRING
)
from filters import is_badminton_post, is_west_singapore
from parser import format_alert

logger = logging.getLogger(__name__)


async def resolve_watch_ids(client: TelegramClient) -> set[int]:
    """Resolve WATCH_GROUPS names/usernames to numeric chat IDs."""
    if not WATCH_GROUPS:
        return set()

    watch_ids = set()
    for attempt in range(3):
        try:
            async for dialog in client.iter_dialogs():
                name     = (dialog.name or "").lower()
                username = (getattr(dialog.entity, "username", "") or "").lower()
                for wg in WATCH_GROUPS:
                    wg_clean = wg.lstrip("@").lower()
                    if wg_clean in name or wg_clean == username:
                        watch_ids.add(dialog.id)
                        logger.info(f"Watching group: '{dialog.name}' (id={dialog.id})")
            break
        except Exception as e:
            logger.warning(f"Dialog fetch attempt {attempt + 1} failed: {e}")
            import asyncio; await asyncio.sleep(5)

    return watch_ids


async def _get_topic_title(client: TelegramClient, chat_id: int, topic_id: int) -> str | None:
    """Look up the title of a forum topic by its ID."""
    try:
        result = await client(functions.channels.GetForumTopicsRequest(
            channel=chat_id,
            offset_date=0, offset_id=0, offset_topic=0,
            limit=100, q="",
        ))
        for topic in result.topics:
            if topic.id == topic_id:
                return topic.title
    except Exception as e:
        logger.debug(f"Could not fetch topic title: {e}")
    return None


def make_handler(client: TelegramClient, watch_ids: set[int]):
    """
    Return the Telethon event handler function.
    Defined as a factory so it closes over client and watch_ids.
    """

    @client.on(events.NewMessage(chats=list(watch_ids) if watch_ids else None))
    async def handler(event):
        if not event.is_group and not event.is_channel:
            return

        # --- Topic filter ---
        if WATCH_TOPICS and event.message.reply_to:
            topic_id = (
                event.message.reply_to.reply_to_top_id
                or event.message.reply_to.reply_to_msg_id
            )
            if topic_id:
                title = await _get_topic_title(client, event.chat_id, topic_id)
                if title and not any(w.lower() in title.lower() for w in WATCH_TOPICS):
                    return  # wrong topic

        text = event.raw_text or ""
        if not text:
            return

        chat       = await event.get_chat()
        chat_title = getattr(chat, "title", None) or getattr(chat, "username", "Unknown")

        if not is_badminton_post(text):
            return

        if not is_west_singapore(text):
            logger.info(f"Badminton post in '{chat_title}' — not West SG, skipped.")
            return

        logger.info(f"West SG game detected in '{chat_title}'")

        sender = await event.get_sender()
        alert  = format_alert(text, chat_title, sender)

        await client.send_message(ALERT_CHAT, alert, parse_mode="md")

    return handler


async def run():
    """Start the Telethon client and begin listening."""
    session = StringSession(SESSION_STRING) if SESSION_STRING else SESSION_FILE
    client = TelegramClient(session, API_ID, API_HASH)

    await client.start()
    me = await client.get_me()
    logger.info(f"Logged in as {me.first_name} (@{me.username})")

    watch_ids = await resolve_watch_ids(client)
    make_handler(client, watch_ids)

    logger.info("Listening for West SG badminton games… (Ctrl+C to stop)")
    await client.run_until_disconnected()