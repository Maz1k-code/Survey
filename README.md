# Survey Bot (aiogram 3.7+)

A Telegram bot that collects a 5-question survey from startup founders.

## Quick start

```bash
git clone <repo> && cd survey_bot_aiogram
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env      # or cp on mac/Linux
# edit .env and paste your BotFather token

python bot.py
