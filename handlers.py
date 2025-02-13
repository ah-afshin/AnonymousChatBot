import database as db
from config import ROOT_URL, KEY
from datetime import datetime

def xor(value: int, key: int) -> int:
    return value ^ key  # XOR operation


async def handle_new_account(chat_id: int, bale_id: str) -> str:
    try:
        id:str = await db.add_user(chat_id, bale_id)
        return f"Welcome {bale_id}! Your anonymous-ID is {id}\nuse this link to invite people:\n{ROOT_URL}?start={id}"
    except Exception as e:
        # print(e)
        return "```[error]you have already signed up.```"


async def handle_chat_start(anon_id: str) -> str:
    try:
        target: int = await db.get_chatid(anon_id)
        chat_code: str = str(xor(target, KEY))
        return f"```[.]{chat_code}```\nChat started. reply this message."
    except Exception as e:
        return f"```[error]{e}```"


async def reply_to_chat(last_text, chat_id, text) -> tuple[int, str]:
    target_id: str = str(xor(
        int(
            last_text.split("]")[1]
            .split("`")[0]
        ),
        KEY
    ))
    chat_code: str = str(xor(chat_id, KEY))
    txt: str = f"```[{datetime.now().strftime("%Y/%m/%d-%H:%M:%S")}]{chat_code}```\n{text}"
    return target_id, txt
