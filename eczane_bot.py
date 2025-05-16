import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# List of major provinces in Turkey (Turkish names, lowercase for API)
PROVINCES = [
    "adana", "ankara", "antalya", "bursa", "diyarbakir", 
    "erzurum", "eskisehir", "gaziantep", "istanbul", "izmir", 
    "kayseri", "konya", "malatya", "mersin", "samsun", "trabzon"
]

# Initialize bot and dispatcher with storage for FSM
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# --- /start ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("👋 Welcome to Türkiye Med Helper Bot!\nUse /eczaneler to find duty pharmacies in any province.")

# --- /eczaneler ---
@dp.message_handler(commands=['eczaneler'])
async def choose_province(message: types.Message):
    """
    Show province selection keyboard
    """
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    
    # Create buttons for each province
    buttons = []
    for province in PROVINCES:
        # Capitalize the first letter for display
        display_name = province.capitalize()
        # Create callback data in the format "province:name"
        callback_data = f"province:{province}"
        buttons.append(types.InlineKeyboardButton(display_name, callback_data=callback_data))
    
    # Add all buttons to the keyboard
    keyboard.add(*buttons)
    
    await message.answer("🇹🇷 Please select a province (il):", reply_markup=keyboard)

# Province selection callback handler
@dp.callback_query_handler(lambda c: c.data.startswith('province:'))
async def process_province_selection(callback_query: types.CallbackQuery):
    # Get the selected province from the callback data
    selected_province = callback_query.data.split(':')[1]
    
    # Acknowledge the selection to remove the loading indicator
    await callback_query.answer(f"Selected: {selected_province.capitalize()}")
    
    # Inform the user that we're fetching data
    await callback_query.message.answer(f"🔍 Fetching duty pharmacies in {selected_province.capitalize()}...")
    
    headers = {
        "authorization": f"apikey {os.getenv('COLLECT_API_KEY')}"
    }
    url = f"https://api.collectapi.com/health/dutyPharmacy?il={selected_province}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()

        pharmacies = data.get("result", [])
        if not pharmacies:
            await callback_query.message.answer("⚠️ No pharmacies found.")
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

            await callback_query.message.answer(text, reply_markup=keyboard if keyboard.inline_keyboard else None, parse_mode="Markdown")
    
    except Exception as e:
        error_message = f"❌ Error: {type(e).__name__} - {e}"
        await callback_query.message.answer(error_message)
        logging.exception("Error fetching pharmacies")


# --- /healthcheck ---
@dp.message_handler(commands=['healthcheck'])
async def healthcheck(message: types.Message):
    await message.answer("✅ Bot is up and running!")

# --- Start bot ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)