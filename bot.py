import typing as t
import aiohttp, asyncio
from config import URL
from database import init_db
import handlers



async def send_message(chat_id: int, text: str) -> dict[str, t.Any]:
    send_api: str = URL + "sendMessage"
    data: dict[str, str] = {
            'chat_id': str(chat_id),
            'text': text,
            'parse_mode': 'MarkdownV2' # add markdown support (Telegram)
        }

    async with aiohttp.ClientSession() as session:
        async with session.post(send_api, json=data) as response:
            return await response.json()


async def get_updates(offset: int) -> list[dict[str, t.Any]]:
    get_api: str = URL + "getUpdates"
    params: dict[str, t.Any] = {'offset': offset} if offset else {}

    async with aiohttp.ClientSession() as session:
        async with session.get(get_api, params=params) as response:
            if response.status == 200:
                data: dict[str, t.Any] = await response.json()
                return data.get('result', [])
    return []


async def process_update(update: dict[str, t.Any]) -> None:
    """Processes incoming messages and handles deep linking."""
    message: dict[str, t.Any] = update.get("message", {})
    chat_id: int = message["chat"]["id"]
    bale_id: str = message["chat"]["username"]
    text: str = message.get("text", "")

    # /start command
    if text.startswith("/start"):
        parts: list[str] = text.split('=')
        if len(parts) > 1:  # There's a payload
            anon_id: str = parts[1]
            txt: str = await handlers.handle_chat_start(anon_id)
        else:
            txt: str = await handlers.handle_new_account(chat_id, bale_id)
        await send_message(chat_id, txt)
    
    # Check if replied to message
    if "reply_to_message" in message:
        original_message: dict[str, t.Any] = message["reply_to_message"]
        if original_message.get("from", {}).get("is_bot", False):
            original_text: str = original_message.get("text", "")
            res: tuple[int, str] = await handlers.reply_to_chat(original_text, chat_id, text)
            await send_message(res[0], res[1])
        else:
            await send_message(chat_id, "You can only reply other user's message, and not your owns.")


async def main() -> None:
    await init_db()

    offset: int = 0
    while True:
        updates: list[dict[str, t.Any]] = await get_updates(offset)
        if updates:
            for update in updates:
            # # callback for reports and blocks
            # if "callback_query" in update:
            #     handle_callback_query(update["callback_query"])            

                await process_update(update)
                offset = update["update_id"] + 1
        # Avoid excessive polling [??]
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
