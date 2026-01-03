# Don't Remove Credit Tg - @Tushar0125
# Ask Doubt on telegram @Tushar0125

import os
import re
import sys
import json
import time
import m3u8
import aiohttp
import asyncio
import requests
import subprocess
import urllib.parse
import cloudscraper
import datetime
import random
import ffmpeg
import logging
import yt_dlp
from subprocess import getstatusoutput
from aiohttp import web
from core import *
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL
import yt_dlp as youtube_dl
import cloudscraper
import m3u8
import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput
from pytube import YouTube

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
cookies_file_path = os.getenv("COOKIES_FILE_PATH", "youtube_cookies.txt")

# ============= NEW IMAGE URL =============
NEW_IMAGE_URL = "https://image2url.com/r2/default/images/1767442486807-a8fc6055-8de4-4287-abf2-5e7fd75ba17d.png"
cpimg = NEW_IMAGE_URL

# ============= HELPER FUNCTIONS =============
async def handle_pdf_download(url, name, caption, m, bot, count):
    try:
        url = url.replace(" ", "%20")
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if response.status_code == 200:
            with open(f'{name}.pdf', 'wb') as f:
                f.write(response.content)
            await asyncio.sleep(4)
            await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=caption)
            os.remove(f'{name}.pdf')
            return True
        else:
            await m.reply_text(f"Failed to download PDF: {response.status_code}")
            return False
    except Exception as e:
        await m.reply_text(f"PDF Error: {str(e)}")
        return False

async def handle_image_download(url, name, caption, m, bot, count):
    try:
        await asyncio.sleep(4)
        url = url.replace(" ", "%20")
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if response.status_code == 200:
            with open(f'{name}.jpg', 'wb') as f:
                f.write(response.content)
            await asyncio.sleep(2)
            await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.jpg', caption=caption)
            os.remove(f'{name}.jpg')
            return True
        else:
            await m.reply_text(f"Failed to download Image: {response.status_code}")
            return False
    except Exception as e:
        await m.reply_text(f"Image Error: {str(e)}")
        return False

async def handle_zip_download(url, name, caption, m, bot, count):
    try:
        cmd = f'yt-dlp -o "{name}.zip" "{url}"'
        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
        os.system(download_cmd)
        await bot.send_document(chat_id=m.chat.id, document=f'{name}.zip', caption=caption)
        os.remove(f'{name}.zip')
        return True
    except Exception as e:
        await m.reply_text(f"ZIP Error: {str(e)}")
        return False

async def handle_video_download(url, name, caption, m, bot, count, helper, res, total_links, thumb):
    try:
        emoji_message = await show_random_emojis(m)
        remaining_links = total_links - count
        Show = f"**🍁 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 🍁**\n\n**📝ɴᴀᴍᴇ » ** `{name}\n\n🔗ᴛᴏᴛᴀʟ ᴜʀʟ » {total_links}\n\n🗂️ɪɴᴅᴇx » {str(count)}/{total_links}\n\n🌐ʀᴇᴍᴀɪɴɪɴɢ ᴜʀʟ » {remaining_links}\n\n❄ǫᴜᴀʟɪᴛʏ » {res}`\n\n**🔗ᴜʀʟ » ** `{url}`\n\n🤖𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 ➤ 𝗧𝗨𝗦𝗛𝗔𝗥\n\n🙂 चलो फिर से अजनबी बन जायें 🙂"
        prog = await m.reply_text(Show)
        res_file = await helper.download_video(url, cmd, name)
        filename = res_file
        await prog.delete(True)
        await emoji_message.delete()
        await helper.send_vid(bot, m, caption, filename, thumb, name, prog)
        return True
    except Exception as e:
        await m.reply_text(f"Video Error: {str(e)}")
        return False

async def show_random_emojis(message):
    emojis = ['🎊', '🔮', '😎', '⚡️', '🚀', '✨', '💥', '🎉', '🥂', '🍾', '🦠', '🤖', '❤️‍🔥', '🕊️', '💃', '🥳','🐅','🦁']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message

# Define the owner's user ID
OWNER_ID = 6334323103
SUDO_USERS = [6334323103]
AUTH_CHANNELS = [-1003651358527]

def is_authorized(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_USERS or user_id in AUTH_CHANNELS

# Flask app for webhook health check
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # Telegram sends updates here
    return "OK", 200

# Pyrogram Bot
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("sudo"))
async def sudo_command(bot: Client, message: Message):
    user_id = message.chat.id
    if user_id != OWNER_ID:
        await message.reply_text("**🚫 You are not authorized to use this command.**")
        return

    try:
        args = message.text.split(" ", 2)
        if len(args) < 2:
            await message.reply_text("**Usage:** `/sudo add <user_id>` or `/sudo remove <user_id>`")
            return

        action = args[1].lower()
        target_user_id = int(args[2])

        if action == "add":
            if target_user_id not in SUDO_USERS:
                SUDO_USERS.append(target_user_id)
                await message.reply_text(f"**✅ User {target_user_id} added to sudo list.**")
            else:
                await message.reply_text(f"**⚠️ User {target_user_id} is already in the sudo list.**")
        elif action == "remove":
            if target_user_id == OWNER_ID:
                await message.reply_text("**🚫 The owner cannot be removed from the sudo list.**")
            elif target_user_id in SUDO_USERS:
                SUDO_USERS.remove(target_user_id)
                await message.reply_text(f"**✅ User {target_user_id} removed from sudo list.**")
            else:
                await message.reply_text(f"**⚠️ User {target_user_id} is not in the sudo list.**")
        else:
            await message.reply_text("**Usage:** `/sudo add <user_id>` or `/sudo remove <user_id>`")
    except Exception as e:
        await message.reply_text(f"**Error:** {str(e)}")

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🇮🇳ʙᴏᴛ ᴍᴀᴅᴇ ʙʏ🇮🇳", url="https://t.me/Tushar0125")],
    [InlineKeyboardButton("🔔ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ🔔", url="https://t.me/TxtToVideoUpdateChannel")],
    [InlineKeyboardButton("🦋ғᴏʟʟᴏᴡ ᴜs🦋", url="https://t.me/TxtToVideoUpdateChannel")]
])

caption = (
    "**ʜᴇʟʟᴏ👋**\n\n"
    "➠ **ɪ ᴀᴍ ᴛxᴛ ᴛᴏ ᴠɪᴅᴇᴏ ᴜᴘʟᴏᴀᴅᴇʀ ʙᴏᴛ.**\n"
    "➠ **ғᴏʀ ᴜsᴇ ᴍᴇ sᴇɴᴅ /tushar.\n"
    "➠ **ғᴏʀ ɢᴜɪᴅᴇ sᴇɴᴅ /help."
)

@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, message: Message):
    await bot.send_photo(chat_id=message.chat.id, photo=NEW_IMAGE_URL, caption=caption, reply_markup=keyboard)

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    await m.reply_text("**𝗦𝘁𝗼𝗽𝗽𝗲𝗱**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command("restart"))
async def restart_handler(_, m):
    if not is_authorized(m.from_user.id):
        await m.reply_text("**🚫 You are not authorized to use this command.**")
        return
    await m.reply_text("🔮Restarted🔮", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

COOKIES_FILE_PATH = "youtube_cookies.txt"

@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    if not is_authorized(m.from_user.id):
        await m.reply_text("🚫 You are not authorized to use this command.")
        return
    
    await m.reply_text("𝗣𝗹𝗲𝗮𝘀𝗲 𝗨𝗽𝗹𝗼𝗮𝗱 𝗧𝗵𝗲 𝗖𝗼𝗼𝗸𝗶𝗲𝘀 𝗙𝗶𝗹𝗲 (.𝘁𝘅𝘁 𝗳𝗼𝗿𝗺𝗮𝘁).", quote=True)

    try:
        input_message: Message = await client.listen(m.chat.id)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        downloaded_path = await input_message.download()
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        with open(COOKIES_FILE_PATH, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text("✅ 𝗖𝗼𝗼𝗸𝗶𝗲𝘀 𝗨𝗽𝗱𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆.\n\n📂 𝗦𝗮𝘃𝗲𝗱 𝗜𝗻 youtube_cookies.txt.")

    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command("help"))
async def help_command(client: Client, msg: Message):
    help_text = (
        "`/start` - Start the bot⚡\n\n"
        "`/tushar` - Download and upload files (sudo)🎬\n\n"
        "`/restart` - Restart the bot🔮\n\n"
        "`/stop` - Stop ongoing process🛑\n\n"
        "`/cookies` - Upload cookies file🍪\n\n"
        "`/e2t` - Edit txt file📝\n\n"
        "`/yt2txt` - Create txt of yt playlist (owner)🗃️\n\n"
        "`/sudo add` - Add user or group or channel (owner)🎊\n\n"
        "`/sudo remove` - Remove user or group or channel (owner)❌\n\n"
        "`/userlist` - List of sudo user or group or channel📜\n\n"
    )
    await msg.reply_text(help_text)

@bot.on_message(filters.command(["tushar"]))
async def upload(bot: Client, m: Message):
    if not is_authorized(m.chat.id):
        await m.reply_text("**🚫You are not authorized to use this bot.**")
        return

    editable = await m.reply_text(f"⚡𝗦𝗘𝗡𝗗 𝗧𝗫𝗧 𝗙𝗜𝗟𝗘⚡")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    pdf_count = 0
    img_count = 0
    zip_count = 0
    video_count = 0
    failed_count = 0

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")

        links = []
        for i in content:
            if "://" in i:
                url = i.split("://", 1)[1]
                links.append(i.split("://", 1))
                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif ".zip" in url:
                    zip_count += 1
                else:
                    video_count += 1
        os.remove(x)
    except:
        await m.reply_text("😶𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗙𝗶𝗹𝗲 𝗜𝗻𝗽𝘂𝘁😶")
        os.remove(x)
        return

    await editable.edit(f"`𝗧𝗼𝘁𝗮𝗹 🔗 𝗟𝗶𝗻𝗸𝘀 𝗙𝗼𝘂𝗻𝗱 𝗔𝗿𝗲 {len(links)}\n\n🔹Img : {img_count}  🔹Pdf : {pdf_count}\n🔹Zip : {zip_count}  🔹Video : {video_count}\n\n𝗦𝗲𝗻𝗱 𝗙𝗿𝗼𝗺 𝗪𝗵𝗲𝗿𝗲 𝗬𝗼𝘂 𝗪𝗮𝗻𝘁 𝗧𝗼 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱.`")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    try:
        arg = int(raw_text)
    except:
        arg = 1
    await editable.edit("📚 𝗘𝗻𝘁𝗲𝗿 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 📚\n\n🦠 𝗦𝗲𝗻𝗱 `1` 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 🦠")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == '1':
        b_name = file_name
    else:
        b_name = raw_text0

    await editable.edit("**📸 𝗘𝗻𝘁𝗲𝗿 𝗥𝗲𝘀𝗼𝗹𝘂𝘁𝗶𝗼𝗻 📸**\n➤ `144`\n➤ `240`\n➤ `360`\n➤ `480`\n➤ `720`\n➤ `1080`")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080"
        else:
            res = "UN"
    except Exception:
        res = "UN"

    await editable.edit("📛 𝗘𝗻𝘁𝗲𝗿 𝗬𝗼𝘂𝗿 𝗡𝗮𝗺𝗲 📛\n\n🐥 𝗦𝗲𝗻𝗱 `1` 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗗𝗲𝗳𝗮𝘂𝗹𝘁 🐥")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    credit = "️[𝗧𝘂𝘀𝗵𝗮𝗿](https://t.me/Tushar0125)"
    if raw_text3 == '1':
        CR = '[𝗧𝘂𝘀𝗵𝗮𝗿](https://t.me/Tushar0125)'
    elif raw_text3:
        try:
            text, link = raw_text3.split(',')
            CR = f'[{text.strip()}]({link.strip()})'
        except ValueError:
            CR = raw_text3
    else:
        CR = credit

    # ========== FIXED: "3" FOR OTHERS LOGIC ==========
    await editable.edit("**𝗘𝗻𝘁𝗲𝗿 𝗣𝘄 𝗧𝗼𝗸𝗲𝗻 𝗙𝗼𝗿 𝗣𝘄 𝗨𝗽𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗼𝗿 𝗦𝗲𝗻𝗱 `3` 𝗙𝗼𝗿 𝗢𝘁𝗵𝗲𝗿𝘀**")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)
    
    if raw_text4 == '3':
        MR = None  # No token needed for other links
    else:
        MR = raw_text4  # Use the provided token

    await editable.edit("𝗡𝗼𝘄 𝗦𝗲𝗻𝗱 𝗧𝗵𝗲 𝗧𝗵𝘂𝗺𝗯 𝗨𝗿𝗹 𝗘𝗴 » " + NEW_IMAGE_URL + "\n\n𝗢𝗿 𝗜𝗳 𝗗𝗼𝗻'𝘁 𝗪𝗮𝗻𝘁 𝗧𝗵𝘂𝗺𝗯𝗻𝗮𝗶𝗹 𝗦𝗲𝗻𝗱 = 𝗻𝗼")
    input6 = message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = "no"
    failed_count = 0

    if len(links) == 1:
        count = 1
    else:
        count = int(raw_text)

    try:
        for i in range(count - 1, len(links)):
            try:
                V = (
                    links[i][1]
                    .replace("file/d/", "uc?export=download&id=")
                    .replace("www.youtube-nocookie.com/embed", "youtu.be")
                    .replace("?modestbranding=1", "")
                    .replace("/view?usp=sharing", "")
                )
                url = "https://" + V

                if "visionias" in url:
                    async with ClientSession() as session:
                        async with session.get(
                            url,
                            headers={
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                                'Accept-Language': 'en-US,en;q=0.9',
                                'Cache-Control': 'no-cache',
                                'Connection': 'keep-alive',
                                'Pragma': 'no-cache',
                                'Referer': 'http://www.visionias.in/',
                                'Sec-Fetch-Dest': 'iframe',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'cross-site',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (Linux; Android 12)',
                                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                                'sec-ch-ua-mobile': '?1',
                                'sec-ch-ua-platform': '"Android"',
                            }
                        ) as resp:
                            text = await resp.text()
                    url = re.search(r'(https://.*?playlist\.m3u8.*?)"', text).group(1)

                elif 'media-cdn.classplusapp.com/drm/' in url:
                    url = f"https://dragoapi.vercel.app/video/{url}"

                elif 'videos.classplusapp' in url:
                    resp = requests.get(
                        f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                        headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9'}
                    ).json()
                    url = resp['url']

                elif any(domain in url for domain in ["tencdn.classplusapp", "media-cdn-alisg.classplusapp.com", "media-cdn.classplusapp"]):
                    headers = {
                        'Host': 'api.classplusapp.com',
                        'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9',
                        'user-agent': 'Mobile-Android',
                        'app-version': '1.4.37.1',
                        'api-version': '18',
                        'device-id': '5d0d17ac8b3c9f51',
                        'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30',
                        'accept-encoding': 'gzip'
                    }
                    response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=(('url', url),))
                    url = response.json()['url']

                elif "appx-transcoded-videos.livelearn.in/videos/rozgar-data/" in url:
                    url = url.replace("https://appx-transcoded-videos.livelearn.in/videos/rozgar-data/", "")
                    name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                    name = f'{str(count).zfill(3)}) {name1[:60]}'
                    cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

                elif "/master.mpd" in url or "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                    if MR:
                        url = f"https://anonymouspwplayerr-f996115ea61a.herokuapp.com/pw?url={url}&token={MR}"
                    else:
                        url = f"https://anonymouspwplayerr-f996115ea61a.herokuapp.com/pw?url={url}"

                elif 'khansirvod4.pc.cdn.bitgravity.com' in url:
                    parts = url.split('/')
                    url = f"https://kgs-v4.akamaized.net/kgs-cv/{parts[3]}/{parts[4]}/{parts[5]}"

                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]" if "youtu" in url else f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
                
                if "edge.api.brightcove.com" in url:
                    bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzUxMzUzNjIsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiYmt3cmVIWmxZMFUwVXpkSmJYUkxVemw2ZW5Oclp6MDkiLCJmaXJzdF9uYW1lIjoiY25GdVpVdG5kRzR4U25sWVNGTjRiVW94VFhaUVVUMDkiLCJlbWFpbCI6ImFFWllPRXhKYVc1NWQyTlFTazk0YmtWWWJISTNRM3BKZW1OUVdIWXJWWE0wWldFNVIzZFNLelE0ZHowPSIsInBob25lIjoiZFhSNlFrSm9XVlpCYkN0clRUWTFOR3REU3pKTVVUMDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJhVVZGZGpBMk9XSnhlbXRZWm14amF6TTBVazQxUVQwOSIsImRldmljZV90eXBlIjoid2ViIiwiZGV2aWNlX3ZlcnNpb24iOiJDaHJvbWUrMTE5IiwiZGV2aWNlX21vZGVsIjoiY2hyb21lIiwicmVtb3RlX2FkZHIiOiIyNDA5OjQwYzI6MjA1NTo5MGQ0OjYzYmM6YTNjOTozMzBiOmIxOTkifX0.Kifitj1wCe_ohkdclvUt7WGuVBsQFiz7eezXoF1RduDJi4X7egejZlLZ0GCZmEKBwQpMJLvrdbAFIRniZoeAxL4FZ-pqIoYhH3PgZU6gWzKz5pdOCWfifnIzT5b3rzhDuG7sstfNiuNk9f-HMBievswEIPUC_ElazXdZPPt1gQqP7TmVg2Hjj6-JBcG7YPSqa6CUoXNDHpjWxK_KREnjWLM7vQ6J3vF1b7z_S3_CFti167C6UK5qb_turLnOUQzWzcwEaPGB3WXO0DAri6651WF33vzuzeclrcaQcMjum8n7VQ0Cl3fqypjaWD30btHQsu5j8j3pySWUlbyPVDOk-g'
                    url = url.split("bcov_auth")[0] + bcov

                   name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                name = f'{str(count).zfill(3)}) {name1[:60]}'

                # ================= URL PROCESSING =================
                # VISIONIAS
                if "visionias" in url:
                    async with ClientSession() as session:
                        async with session.get(
                            url,
                            headers={
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                                'Accept-Language': 'en-US,en;q=0.9',
                                'Cache-Control': 'no-cache',
                                'Connection': 'keep-alive',
                                'Pragma': 'no-cache',
                                'Referer': 'http://www.visionias.in/',
                                'Sec-Fetch-Dest': 'iframe',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'cross-site',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (Linux; Android 12)',
                                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                                'sec-ch-ua-mobile': '?1',
                                'sec-ch-ua-platform': '"Android"',
                            }
                        ) as resp:
                            text = await resp.text()
                    url = re.search(r'(https://.*?playlist\.m3u8.*?)"', text).group(1)

                # CLASSPLUS DRM
                elif 'media-cdn.classplusapp.com/drm/' in url:
                    url = f"https://dragoapi.vercel.app/video/{url}"

                elif 'videos.classplusapp' in url:
                    resp = requests.get(
                        f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                        headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9'}
                    ).json()
                    url = resp['url']

                elif any(domain in url for domain in ["tencdn.classplusapp", "media-cdn-alisg.classplusapp.com", "media-cdn.classplusapp"]):
                    headers = {
                        'Host': 'api.classplusapp.com',
                        'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9',
                        'user-agent': 'Mobile-Android',
                        'app-version': '1.4.37.1',
                        'api-version': '18',
                        'device-id': '5d0d17ac8b3c9f51',
                        'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30',
                        'accept-encoding': 'gzip'
                    }
                    response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=(('url', url),))
                    url = response.json()['url']

                # LIVELEARN
                elif "appx-transcoded-videos.livelearn.in/videos/rozgar-data/" in url:
                    url = url.replace("https://appx-transcoded-videos.livelearn.in/videos/rozgar-data/", "")
                    name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                    name = f'{str(count).zfill(3)}) {name1[:60]}'
                    cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

                # PW / MPD
                elif "/master.mpd" in url or "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                    # FIXED: Only add token if MR is not None (user didn't send "3")
                    if MR:
                        url = f"https://anonymouspwplayerr-f996115ea61a.herokuapp.com/pw?url={url}&token={MR}"
                    else:
                        url = f"https://anonymouspwplayerr-f996115ea61a.herokuapp.com/pw?url={url}"

                # FILE NAME PROCESSING
                name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                name = f'{str(count).zfill(3)}) {name1[:60]}'

                # KHANSIR VOD
                if 'khansirvod4.pc.cdn.bitgravity.com' in url:
                    parts = url.split('/')
                    url = f"https://kgs-v4.akamaized.net/kgs-cv/{parts[3]}/{parts[4]}/{parts[5]}"

                # YT-DLP COMMAND BUILDER
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]" if "youtu" in url else f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
                
                if "edge.api.brightcove.com" in url:
                    bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzUxMzUzNjIsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiYmt3cmVIWmxZMFUwVXpkSmJYUkxVemw2ZW5Oclp6MDkiLCJmaXJzdF9uYW1lIjoiY25GdVpVdG5kRzR4U25sWVNGTjRiVW94VFhaUVVUMDkiLCJlbWFpbCI6ImFFWllPRXhKYVc1NWQyTlFTazk0YmtWWWJISTNRM3BKZW1OUVdIWXJWWE0wWldFNVIzZFNLelE0ZHowPSIsInBob25lIjoiZFhSNlFrSm9XVlpCYkN0clRUWTFOR3REU3pKTVVUMDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJhVVZGZGpBMk9XSnhlbXRZWm14amF6TTBVazQxUVQwOSIsImRldmljZV90eXBlIjoid2ViIiwiZGV2aWNlX3ZlcnNpb24iOiJDaHJvbWUrMTE5IiwiZGV2aWNlX21vZGVsIjoiY2hyb21lIiwicmVtb3RlX2FkZHIiOiIyNDA5OjQwYzI6MjA1NTo5MGQ0OjYzYmM6YTNjOTozMzBiOmIxOTkifX0.Kifitj1wCe_ohkdclvUt7WGuVBsQFiz7eezXoF1RduDJi4X7egejZlLZ0GCZmEKBwQpMJLvrdbAFIRniZoeAxL4FZ-pqIoYhH3PgZU6gWzKz5pdOCWfifnIzT5b3rzhDuG7sstfNiuNk9f-HMBievswEIPUC_ElazXdZPPt1gQqP7TmVg2Hjj6-JBcG7YPSqa6CUoXNDHpjWxK_KREnjWLM7vQ6J3vF1b7z_S3_CFti167C6UK5qb_turLnOUQzWzcwEaPGB3WXO0DAri6651WF33vzuzeclrcaQcMjum8n7VQ0Cl3fqypjaWD30btHQsu5j8j3pySWUlbyPVDOk-g'
                    url = url.split("bcov_auth")[0] + bcov

                cmd = f'yt-dlp -o "{name}.mp4" "{url}"' if "jw-prod" in url else \
                      f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"' if "webvideos.classplusapp." in url else \
                      f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4' if "youtube.com" in url or "youtu.be" in url else \
                      f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

                # CAPTIONS
                cc = f'**[🎬] 𝗩𝗶𝗱_𝗜𝗱 : {str(count).zfill(3)}.\n\n\n☘️𝗧𝗶𝘁𝗹𝗲 𝗡𝗮𝗺𝗲 ➤ {name1}.({res}).𝔗𝔲𝔰𝔥𝔞𝔯.mkv\n\n\n<pre><code>📚𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 ➤ {b_name}</code></pre>\n\n\n📥 𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗕𝘆 ➤  {CR}**'
                cimg = f'**[📁] 𝗜𝗺𝗴_𝗜𝗱 : {str(count).zfill(3)}.\n\n\n☘️𝗧𝗶𝘁𝗹𝗲 𝗡𝗮𝗺𝗲 ➤ {name1}.𝔗𝔲𝔰𝔥𝔞𝔯.jpg\n\n\n<pre><code>📚𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 ➤ {b_name}</code></pre>\n\n\n📥 𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗕𝘆 ➤  {CR}**'
                cczip = f'**[📁] 𝗣𝗱𝗳_𝗜𝗱 : {str(count).zfill(3)}.\n\n\n☘️𝗧𝗶𝘁𝗹𝗲 𝗡𝗮𝗺𝗲 ➤ {name1}.𝔗𝔲𝔰𝔥𝔞𝔯.zip\n\n\n<pre><code>📚𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 ➤ {b_name}</code></pre>\n\n\n📥 𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗕𝘆 ➤  {CR}**'
                cc1 = f'**[📁] 𝗣𝗱𝗳_𝗜𝗱 : {str(count).zfill(3)}.\n\n\n☘️𝗧𝗶𝘁𝗹𝗲 𝗡𝗮𝗺𝗲 ➤ {name1}.𝔗𝔲𝔰𝔥𝔞𝔯.pdf\n\n\n<pre><code>📚𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 ➤ {b_name}</code></pre>\n\n\n📥 𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗕𝘆 ➤  {CR}**'

                # DOWNLOAD BASED ON FILE TYPE
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc1)
                        count += 1
                        os.remove(ka)
                        await asyncio.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    success = await handle_pdf_download(url, name, cc1, m, bot, count)
                    if success:
                        count += 1
                    else:
                        failed_count += 1

                elif any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png"]):
                    success = await handle_image_download(url, name, cimg, m, bot, count)
                    if success:
                        count += 1
                    else:
                        failed_count += 1

                elif ".zip" in url:
                    success = await handle_zip_download(url, name, cczip, m, bot, count)
                    if success:
                        count += 1
                    else:
                        failed_count += 1

                else:  # Video
                    success = await handle_video_download(url, name, cc, m, bot, count, helper, res, len(links), thumb)
                    if success:
                        count += 1
                    else:
                        failed_count += 1

            except Exception as e:  # INNER EXCEPT
                await m.reply_text(f'‼️𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗶𝗻𝗴 𝗙𝗮𝗶𝗹𝗲𝗱‼️\n\n'
                                   f'📝𝗡𝗮𝗺𝗲 » `{name if "name" in locals() else "Unknown"}`\n\n'
                                   f'🔗𝗨𝗿𝗹 » <a href="{url if "url" in locals() else ""}">__**Click Here to See Link**__</a>`')
                failed_count += 1
                continue

    except Exception as e:
        await m.reply_text(f"**Outer Error: **{str(e)}")

# ================= SUMMARY MESSAGES =================
    await m.reply_text(
        f"`✨𝗕𝗔𝗧𝗖𝗛 𝗦𝗨𝗠𝗠𝗔𝗥𝗬✨\n\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"📛𝗜𝗻𝗱𝗲𝘅 𝗥𝗮𝗻𝗴𝗲 » ({raw_text} to {len(links)})\n"
        f"📚𝗕𝗮𝘁𝗰𝗵 𝗡𝗮𝗺𝗲 » {b_name}\n\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"✨𝗧𝗫𝗧 𝗦𝗨𝗠𝗠𝗔𝗥𝗬✨ : {len(links)}\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"🔹𝗩𝗶𝗱𝗲𝗼 » {video_count}\n"
        f"🔹𝗣𝗱𝗳 » {pdf_count}\n"
        f"🔹𝗜𝗺𝗴 » {img_count}\n"
        f"🔹𝗭𝗶𝗽 » {zip_count}\n"
        f"🔹𝗙𝗮𝗶𝗹𝗲𝗱 𝗨𝗿𝗹 » {failed_count}\n\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"✅𝗦𝗧𝗔𝗧𝗨𝗦 » 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗`"
    )

    await m.reply_text(
        f"<pre><code>📥𝗘𝘅𝘁𝗿𝗮𝗰𝘁𝗲𝗱 𝗕𝘆 ➤『{CR}』</code></pre>"
    )

    await m.reply_text(
        f"<pre><code>『😏𝗥𝗲𝗮𝗰𝘁𝗶𝗼𝗻 𝗞𝗼𝗻 𝗗𝗲𝗴𝗮😏』</code></pre>"
    )

# ============= MAIN EXECUTION =============
if __name__ == '__main__':
    import asyncio
    
    # Start bot with webhook for production
    PORT = int(os.getenv("PORT", "10000"))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", f"https://your-app.onrender.com/webhook")
    
    try:
        # Set webhook
        bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook set to: {WEBHOOK_URL}")
        
        # Start Flask app
        from threading import Thread
        flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=PORT, debug=False))
        flask_thread.start()
        
        # Keep bot alive
        bot.idle()
        
    except Exception as e:
        print(f"⚠️ Webhook failed: {e}")
        print("ℹ️ Falling back to polling...")
        bot.run()
        