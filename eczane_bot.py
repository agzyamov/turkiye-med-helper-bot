import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- /start ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Welcome to Türkiye Med Helper Bot!\nUse /eczaneler to find duty pharmacies.")

# --- /eczaneler ---
@dp.message_handler(commands=['eczaneler'])
async def send_pharmacies(message: types.Message):
    await message.answer("🔍 Fetching duty pharmacies in Antalya...")

    headers = {
        "authorization": f"apikey {os.getenv('COLLECT_API_KEY')}"
    }
    url = "https://api.collectapi.com/health/dutyPharmacy?il=antalya"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()

        pharmacies = data.get("result", [])
        if not pharmacies:
            await message.answer("⚠️ No pharmacies found.")
            return

        # Limit to 10 pharmacies (increased from 5)
        for pharmacy in pharmacies[:10]:
            name = pharmacy["name"]
            address = pharmacy["address"]
            phone = pharmacy["phone"]
            loc = pharmacy.get("loc")

            text = f"🏥 *{name}*\n📍 {address}\n📞 {phone}"

            keyboard = types.InlineKeyboardMarkup()

            if loc:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={loc}"
                keyboard.add(types.InlineKeyboardButton("🗺 Open Map", url=maps_url))

            await message.answer(text, reply_markup=keyboard if keyboard.inline_keyboard else None, parse_mode="Markdown")
    
    except Exception as e:
        error_message = f"❌ Error: {type(e).__name__} - {e}"
        await message.answer(error_message)
        logging.exception("Error fetching pharmacies")


# --- /healthcheck ---
@dp.message_handler(commands=['healthcheck'])
async def healthcheck(message: types.Message):
    await message.answer("✅ Bot is up and running!")

# --- Start bot ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)