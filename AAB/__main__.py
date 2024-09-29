import asyncio
import os
from typing import List, Dict, Any
from AAB import bot, file_client, Vars, LOG
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AAB.utils import extract_info, anime, download_magnet, encode_file, generate_hash, get_anime
from AAB.db import (
    get_file_by_hash, add_file, remove_anime_from_remain, update_worker,
    is_working, get_remain_anime, is_new_db, get_last_hash, add_remain_anime,
    add_hash, mongo_client
)
from AAB import file_client, bot

# Constants
MAIN_CHANNEL = Vars['main_channel']
FILE_CHANNEL = Vars['file_channel']
PRODUCTION_CHAT = Vars['production_chat']
OWNER = Vars['owner']
THUMBNAIL_URL = Vars['thumbnail_url']
POST_MESSAGE = Vars['post_message']

async def send_logs(client: Client, message: Message) -> None:
    try:
        await client.send_document(
            message.from_user.id,
            'logging.txt',
            caption="This is the log of the current session."
        )
        await message.reply_text("Sent logs to your PM")
        LOG.info(f"Sent logs to {message.from_user.id}")
    except Exception as e:
        error_message = f"Error occurred during sending of logs: {e}"
        await message.reply_text(error_message)
        LOG.error(error_message)

async def progress_callback(current: int, total: int) -> None:
    LOG.info(f"{current * 100 / total:.1f}%")

async def upload_file(file_path: str, file_name: str, caption: str) -> Message:
    return await file_client.send_document(
        chat_id=FILE_CHANNEL,
        document=file_path,
        file_name=file_name,
        caption=caption,
        force_document=True,
        thumb=THUMBNAIL_URL,
        progress=progress_callback
    )

async def process_anime_file(anime_info: Dict[str, Any], quality: str, magnet: str, title: str) -> None:
    update_msg = await bot.send_message(PRODUCTION_CHAT, f"Downloading {title}")
    
    try:
        file_info = await download_magnet(magnet, update_msg)
        await bot.send_message(PRODUCTION_CHAT, f"Uploading {title}")
        
        file_msg = await upload_file(file_info['file'], anime_info['main_res'], title)
        anime_hash = generate_hash(20)
        add_file(title, anime_hash, file_msg.id)

        if quality == " 720":
            await process_encoded_file(file_info['file'], anime_info, title)

        os.remove(file_info['file'])
        remove_anime_from_remain()
    except Exception as e:
        LOG.error(f"Error processing anime file: {e}")
        await bot.send_message(PRODUCTION_CHAT, "There was an issue sending a file. Check logs for more info.")

async def process_encoded_file(file_path: str, anime_info: Dict[str, Any], title: str) -> None:
    enc_msg = await bot.send_message(PRODUCTION_CHAT, f"Encoding {title}")
    encoded = await encode_file(file_path)
    await enc_msg.edit_text("Encoded successfully, now uploading")
    
    encode_msg = await upload_file(encoded, f"[ENCODED] {anime_info['main_res']}", f"[ENCODED] {title}")
    enc_anime_hash = generate_hash(20)
    add_file(title, enc_anime_hash, encode_msg.id)
    
    os.remove(encoded)

async def anime_upload(anime_list: List[Dict[str, Any]]) -> None:
    try:
        for anime_item in anime_list:
            name = extract_info(anime_item['title'][0])
            anime_info = anime(name['search_que'])

            message = await bot.send_photo(
                MAIN_CHANNEL,
                anime_info['image'],
                caption=POST_MESSAGE.format(name['main_res'], name['episode'], anime_info['status']),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Uploading", callback_data="NTG")]])
            )

            for i, hash_value in enumerate(anime_item['hash']):
                await process_anime_file(name, anime_item['quality'][i], anime_item['magnet'][i], anime_item['title'][i])
                
                markup = message.reply_markup.inline_keyboard if message.reply_markup else []
                markup.append([InlineKeyboardButton(
                    text=f'{anime_item["quality"][i]}',
                    url=f"https://t.me/{bot.me.username}?start={hash_value}"
                )])
                await message.edit_reply_markup(InlineKeyboardMarkup(markup))

        update_worker(False)
    except Exception as e:
        LOG.error(f"Error in anime_upload: {e}")
        update_worker(False)

async def anime_worker() -> None:
    if is_working():
        return

    try:
        anime_lst = get_remain_anime()
        if anime_lst:
            await anime_upload(anime_lst)
    except Exception as e:
        LOG.error(f"Error in anime_worker: {e}")

async def check_anime() -> None:
    if is_new_db():
        LOG.info("New DB, making required changes")
        anime_list = get_anime('0', 10)
        add_remain_amime(anime_list['array'])
        add_hash(anime_list['hash'])
    else:
        LOG.info("Checking for new anime")
        last_hash = get_last_hash()
        anime_list = get_anime(last_hash, 30)

        if anime_list:
            add_remain_amime(anime_list['array'])
            add_hash(anime_list['hash'])
            await bot.send_message(PRODUCTION_CHAT, f"{len(anime_list['array'])} new anime are added to db")
            LOG.info(f"{len(anime_list['array'])} new anime are added to db.")

@bot.on_message(filters.command("alive") & filters.user(OWNER), group=2)
async def alive(client: Client, message: Message) -> None:
    await message.reply_text("I am alive.")

@bot.on_message(filters.command('start') & filters.private)
async def start_pm(client: Client, message: Message) -> None:
    try:
        txt = message.text.split("_")[-1]
        doc = get_file_by_hash(txt)

        if not txt:
            await message.reply_text("Hello, I am the file sender bot. I send anime based on the given hash and id.")
        elif doc is None:
            await message.reply_text("Wrong hash given")
        else:
            await bot.forward_messages(message.chat.id, FILE_CHANNEL, doc['message_id'], protect_content=True)
    except Exception as e:
        LOG.error(f"Error in start_pm: {e}")

@bot.on_message(filters.command('logs') & filters.user(OWNER))
async def send_logs_command(client: Client, message: Message) -> None:
    await send_logs(client, message)

async def main() -> None:
    try:
        mongo_client.admin.command('ping')
        LOG.info("Connected to MongoDB")
    except Exception as e:
        LOG.critical(f"MongoDB not connected. Error: {e}")
        return

    await file_client.start()
    LOG.info('File Bot Started')

    await bot.start()
    LOG.info('Main Bot Started')

    update_worker(False)

    while True:
        await check_anime()
        await anime_worker()
        await asyncio.sleep(5 * 60)  # Check every 5 minutes

    await file_client.stop()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
