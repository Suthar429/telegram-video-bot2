import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F

import yt_dlp

BOT_TOKEN = "8049347697:AAGTrUweR5aUznng4ZC-NbByjpNgQ_GdKI8"

bot = Bot(token=BOT_TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

@dp.message(F.text.startswith("http"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    builder = InlineKeyboardBuilder()
    builder.button(text="🎥 Download Video", callback_data=f"download_video|{url}")
    builder.button(text="🎵 Download MP3", callback_data=f"download_mp3|{url}")
    await message.answer("🎬 Link detected. Choose an option:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("download_video"))
async def handle_video_download(call: types.CallbackQuery):
    await call.answer()
    _, url = call.data.split("|", 1)
    filename = "video.mp4"
    try:
        ydl_opts = {
            'outtmpl': filename,
            'format': 'mp4',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.getsize(filename) > 48 * 1024 * 1024:
            await call.message.answer("⚠️ Video too large to send via Telegram. Uploading to pixeldrain...")
            # Upload to pixeldrain logic here
        else:
            video = FSInputFile(filename)
            await call.message.answer_video(video=video, caption="✅ Here's your video!")

    except Exception as e:
        await call.message.answer(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

@dp.callback_query(F.data.startswith("download_mp3"))
async def handle_audio_download(call: types.CallbackQuery):
    await call.answer()
    _, url = call.data.split("|", 1)
    filename = "audio.mp3"
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio = FSInputFile(filename)
        await call.message.answer_audio(audio=audio, caption="🎧 Here's your MP3!")

    except Exception as e:
        await call.message.answer(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
