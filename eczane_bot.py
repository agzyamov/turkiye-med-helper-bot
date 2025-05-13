import aiohttp  # добавь к остальным импортам

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

        for pharmacy in pharmacies[:5]:  # показываем максимум 5 аптек
            name = pharmacy["name"]
            address = pharmacy["address"]
            phone = pharmacy["phone"]
            loc = pharmacy.get("loc")

            text = f"🏥 *{name}*\n📍 {address}\n📞 {phone}"
            keyboard = types.InlineKeyboardMarkup()

            if phone:
                keyboard.add(types.InlineKeyboardButton("📞 Call", url=f"tel:{phone}"))
            if loc:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={loc}"
                keyboard.add(types.InlineKeyboardButton("🗺 Open Map", url=maps_url))

            await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    except Exception as e:
        logging.exception("Error fetching pharmacies")
        await message.answer("❌ Failed to fetch pharmacy data.")