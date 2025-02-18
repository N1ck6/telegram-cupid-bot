import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import re
import aiohttp
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import sqlite3

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
db_name = "valentines.db"
logging.basicConfig(level=logging.CRITICAL)
bot = Bot(token=TOKEN)
dp = Dispatcher()
logger = logging.getLogger(__name__)


def sanitize(user_input):  # Remove SQL-injection
    sanitized = re.sub(r"^A-Za-z0-9_", "", user_input)
    return sanitized.strip().split()[0]


async def check_for_user(username):  # Check if user exists
    if not 5 <= len(username) <= 32:
        return False
    url = f"https://t.me/{username}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                html = await response.text()
                if '<div class="tgme_page_icon">' in html:
                    return False
                else:
                    return True
        except aiohttp.ClientError:
            return False


def generate_key(name):
    key = hashlib.sha256(name.encode()).digest()
    return key


def encrypt_name(name, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=b'1234567890123456')
    encrypted_bytes = cipher.encrypt(pad(name.encode(), AES.block_size))
    return base64.b64encode(encrypted_bytes).decode()


def decrypt_name(encrypted_name, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=b'1234567890123456')
    decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_name)), AES.block_size)
    return decrypted_bytes.decode()


def check_db(sender, receiver, sender_id):  # Working with db
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT receiver, sender, first_data FROM users WHERE receiver = ? AND sender = ?", (receiver, sender))
    result = cursor.fetchone()
    if result:
        cursor.execute("UPDATE users SET double = ? WHERE receiver = ? AND sender = ?", (True, receiver, sender))
        conn.commit()
        conn.close()
        return result[0], result[1], result[2]
    else:
        cursor.execute("SELECT receiver FROM users WHERE receiver = ? AND sender = ?", (sender, receiver))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (receiver, sender, first_data, double) VALUES (?, ?, ?, ?)", (sender, receiver, sender_id, False))
            conn.commit()
            conn.close()
        return False


def clear_db():  # Deletes all data from db (For testing purposes)
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
        conn.close()
        logger.critical('Database is cleared!')
    except Exception as e:
        logging.error(f"Error: {e}")


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Hi, my new friend! I can help you send someone a ❤️! The receiver can see that you sent it ONLY if they send you a ❤️ too")
    await message.answer("If you have someone on you mind, send me their nickname - give them a heart ❤️")


@dp.message()
async def handler(message: Message):
    if message:
        sender = message.from_user.username.lower()
        if not sender:
            await message.answer("You should have a nickname in Telegram for this to work!")
            return
        text = message.text
        if text == "❤️":  # Easter egg
            await message.answer("I'll Ctrl+V it back: ❤️!")
            return
        if not text:
            await message.answer("You need to provide me with a nickname")
            return
        receiver = sanitize(text).lower()
        if sender == receiver:
            await message.answer("It's a pity, but it doesn't count that way ಥ_ಥ")
            return
        else:
            if await check_for_user(receiver):
                key1 = generate_key("".join(sorted([sender, receiver])))
                userid = message.from_user.id
                sender_enc = encrypt_name(sender, key1)
                receiver_enc = encrypt_name(receiver, key1)
                userid_enc = encrypt_name(str(userid), key1)
                res = check_db(sender_enc, receiver_enc, userid_enc)
                if res:
                    name1 = decrypt_name(res[0], key1)
                    name2 = decrypt_name(res[1], key1)
                    id1 = decrypt_name(res[2], key1)
                    response = f"And there is a Match 💞: {name1} and {name2}! Good luck, you two!"
                    await message.answer(response)
                    await message.answer("❤️")
                    await bot.send_message(chat_id=int(id1), text=response)
                    await bot.send_message(chat_id=int(id1), text="❤️")
                else:
                    await message.answer("The valentine card is saved! Good luck!")
            else:
                await message.answer("That user doesn't exist in telegram, Sorry!")


async def main():
    async with bot:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        logger.critical('Cupid is activated!')
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Error: {e}")
