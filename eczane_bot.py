import logging
import os
import aiohttp
import sys
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
    logging.info(f"Received /start command from user {message.from_user.id}")
    await message.reply("👋 Welcome to Türkiye Med Helper Bot!\nUse /eczaneler to find duty pharmacies in any province.")

# --- /eczaneler ---
@dp.message_handler(commands=['eczaneler'])
async def choose_province(message: types.Message):
    """
    Show province selection keyboard
    """
    logging.info(f"Received /eczaneler command from user {message.from_user.id}")
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
    logging.info(f"Received province selection callback from user {callback_query.from_user.id}, data: {callback_query.data}")
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
    logging.info(f"Received /healthcheck command from user {message.from_user.id}")
    await message.answer("✅ Bot is up and running!")

# --- Webhook settings ---
WEBHOOK_HOST = os.getenv('RENDER_EXTERNAL_URL')  # Render.com sets this automatically
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# Webserver settings
WEBAPP_HOST = '0.0.0.0'  # Bind to all interfaces
WEBAPP_PORT = int(os.getenv('PORT', 10000))  # Render sets PORT env variable automatically

async def on_startup(dp):
    # Setup webhook
    logging.info(f"Setting webhook to {WEBHOOK_URL}")
    try:
        await bot.delete_webhook()
        await bot.set_webhook(WEBHOOK_URL)
        logging.info("Webhook setup successful")
        
        # Get and log webhook info for debugging
        webhook_info = await bot.get_webhook_info()
        logging.info(f"Webhook info: URL={webhook_info.url}, has custom certificate={webhook_info.has_custom_certificate}, "
                    f"pending update count={webhook_info.pending_update_count}")
    except Exception as e:
        logging.error(f"Failed to set webhook: {e}")

async def on_shutdown(dp):
    # Remove webhook on shutdown
    logging.info("Shutting down webhook connection")
    await bot.delete_webhook()
    
    # Close DB connections, etc.
    await dp.storage.close()
    await dp.storage.wait_closed()

# --- Start bot ---
if __name__ == '__main__':
    # Check if we're running on Render
    if os.getenv('RENDER', ''):
        # Start in webhook mode (for production)
        logging.info("Starting bot in webhook mode")
        logging.info(f"WEBHOOK_HOST: {WEBHOOK_HOST}")
        logging.info(f"WEBHOOK_PATH: {WEBHOOK_PATH}")
        logging.info(f"WEBHOOK_URL: {WEBHOOK_URL}")
        logging.info(f"WEBAPP_HOST: {WEBAPP_HOST}")
        logging.info(f"WEBAPP_PORT: {WEBAPP_PORT}")
        
        if not WEBHOOK_HOST:
            logging.error("RENDER_EXTERNAL_URL environment variable is not set! Setting fallback URL.")
            WEBHOOK_HOST = "https://your-app-name.onrender.com"
            WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
            
        try:
            start_webhook(
                dispatcher=dp,
                webhook_path=WEBHOOK_PATH,
                on_startup=on_startup,
                on_shutdown=on_shutdown,
                skip_updates=True,
                host=WEBAPP_HOST,
                port=WEBAPP_PORT,
            )
        except Exception as e:
            logging.critical(f"Failed to start webhook: {e}")
            sys.exit(1)
    else:
        # Use polling for local development
        logging.info("Starting bot in polling mode (development)")
        executor.start_polling(dp, skip_updates=True)