import asyncio
import os
import uuid

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = os.getenv("7794555956:AAHMWRWcEbzPNjjxGdHm3tl6gtMwSv4I_PA")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


async def download_video(file_id: str, path: str):
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, path)


async def convert(input_path: str, output_path: str):
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "scale=640:640:force_original_aspect_ratio=increase,crop=640:640",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "28",
        "-c:a", "aac",
        output_path
    ]

    process = await asyncio.create_subprocess_exec(*cmd)
    await process.communicate()


@dp.message(F.video)
async def handler(message: Message):
    video = message.video

    if video.duration > 60:
        await message.answer("❌ Видео больше 60 секунд")
        return

    uid = str(uuid.uuid4())
    inp = f"{uid}.mp4"
    out = f"{uid}_circle.mp4"

    try:
        await message.answer("📥 Скачиваю...")
        await download_video(video.file_id, inp)

        await message.answer("🎬 Обрабатываю...")
        await convert(inp, out)

        await message.answer_video_note(video_note=FSInputFile(out))

    finally:
        for f in [inp, out]:
            if os.path.exists(f):
                os.remove(f)


async def main():
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())