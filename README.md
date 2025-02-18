# Telegram Cupid Bot

## Overview
Telegram Cupid Bot allows users to send secret messages to their valentine, leveraging secure encryption and a SQLite database for storing interactions.

## Features
- Lightweight database storage using SQLite
- Stream encryption helps to protect information stored in a database
- Built-in protection against SQL injection attacks
- A unique anonymous way to exchange valentines (idea from VK)

## Installation
### Prerequisites
Ensure you have Python 3.8+ installed.

### Steps
1. Clone the repository:
   ```sh
   https://github.com/N1ck6/telegram-cupid-bot.git
   cd telegram-cupid-bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file and set your bot token:
   ```sh
   BOT_TOKEN=your_telegram_bot_token
   ```
4. Run the bot:
   ```sh
   python bot.py
   ```

## Environment Variables
- `BOT_TOKEN`: Your Telegram bot token obtained from BotFather.

## Dependencies
The required dependencies are listed in `requirements.txt`:
- `aiogram`
- `python-dotenv`
- `aiohttp`
- `pycryptodome`

## Usage
- Start the bot by sending `/start`.
- Send the nickname of the user you would like to send a valentine to.
