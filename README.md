# 🇹🇷 Turkey Med Helper Bot

**A Telegram bot that helps people in Turkey find duty pharmacies (nöbetçi eczane), discover local analogues of Russian medicines, and ask questions at the pharmacy — even if they don’t speak Turkish.**

---

## 🚀 Features

- 🔍 `/eczaneler` — Get current duty pharmacies in any Turkish province (powered by CollectAPI)
- 💊 `/analog` (coming soon) — Find Turkish equivalents of Russian brand-name medicines
- 🗣️ Turkish phrase generation (with optional voice playback)
- 📍 Location-based pharmacy search (future)
- 🛎 Notifications by district (Boosty-only feature)
- 📈 Usage statistics tracking

---

## 📦 Tech Stack

- Python 3.11+
- [aiogram](https://docs.aiogram.dev) for Telegram Bot API
- [CollectAPI](https://collectapi.com) for duty pharmacy data
- gTTS for text-to-speech (planned)
- SQLite / JSON for lightweight data logging

---

## ⚠️ Disclaimer

This bot is for **informational purposes only**.  
It does **not** provide medical advice, diagnosis or treatment recommendations.  
Always consult a licensed pharmacist or physician for healthcare decisions.

---

## 📄 License

This project is licensed under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.  
See [`LICENSE`](./LICENSE) for more.

Commercial use is **not permitted** without written permission.

---

## 🤝 Support

If you found this project useful, consider supporting via Boosty.  
Donations help keep the project running and available for more users.

---

## 🛠 Setup (dev)

1. Clone the repository  
2. Copy `.env.example` → `.env` and fill in your keys  
3. Install dependencies  
```bash
pip install -r requirements.txt
```

4. Run the bot  
```bash
python eczane_bot.py
```

---

> Built by Rustem Agziamov in Türkiye 🇹🇷