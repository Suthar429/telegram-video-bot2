
import asyncio
import os
import subprocess
import uuid
from html import escape

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties  # ✅ Required

BOT_TOKEN = "8049347697:AAGTrUweR5aUznng4ZC-NbByjpNgQ_GdKI8"  # replace with your bot token

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # ✅ Fixed here
)
dp = Dispatcher()


user_links = {}  # Store link IDs temporarily


@dp.message()
async def handle_link(message: Message):
    text = message.text.strip()

    if "instagram.com/reel" in text:
        link_id = str(uuid.uuid4())
        user_links[link_id] = text

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Download Instagram Reel", callback_data=f"insta|{link_id}")]
        ])
        await message.answer("📸 Instagram link detected. Choose option:", reply_markup=markup)

    else:
        await message.answer("❌ Unsupported or invalid link.")


@dp.callback_query()
async def handle_download(call: CallbackQuery):
    try:
        action, link_id = call.data.split("|")
        url = user_links.get(link_id)

        if not url:
            await call.message.answer("⚠️ Link expired or not found.")
            return

        await call.message.answer("⏬ Downloading Instagram Reel... Please wait...")

        output_template = "reel_%(title).50s.%(ext)s"
        cmd = [
            "yt-dlp",
            "-f", "mp4",
            "-o", output_template,
            url
        ]
        subprocess.run(cmd, check=True)

        # Find latest downloaded video
        downloaded_files = sorted([f for f in os.listdir() if f.endswith(".mp4")], key=os.path.getmtime, reverse=True)
        if not downloaded_files:
            await call.message.answer("❌ Download failed. No file found.")
            return

        filename = downloaded_files[0]
        video = FSInputFile(filename)
        await call.message.answer_video(video=video, caption="✅ Here is your Instagram Reel!")

        os.remove(filename)
        del user_links[link_id]

    except Exception as e:
        await call.message.answer(f"⚠️ Error:\n<code>{escape(str(e))}</code>", parse_mode="HTML")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
