# Telegram Bot AI

A Telegram bot for voice transcription, AI chat, image generation, and document summarization.

## Features

- 🎤 **Voice/Audio Transcription** - Speech-to-text using OpenAI Whisper
- 💬 **AI Chat** - Conversations powered by GPT-4o-mini
- 🖼️ **Image Generation** - Create images with DALL-E
- 📄 **Document Summarization** - PDF, DOC, PPT, TXT files
- 🌐 **URL Summarization** - Extract and summarize web pages
- 📊 **Mermaid Diagrams** - Generate flowcharts from text

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/cheuerde/telegram_bot_ai.git
cd telegram_bot_ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```bash
TELEGRAM_API_KEY=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run

```bash
source .venv/bin/activate
python bot.py
```

## Production Deployment (systemd)

For rock-solid 24/7 operation on a Linux server:

### Install systemd service

```bash
# Copy service file
sudo cp telegram-bot.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot.service
sudo systemctl start telegram-bot.service
```

### Manage the bot

```bash
sudo systemctl status telegram-bot   # Check status
sudo systemctl restart telegram-bot  # Restart
sudo systemctl stop telegram-bot     # Stop
sudo journalctl -u telegram-bot -f   # View live logs
```

The systemd service provides:
- ✅ Auto-restart on crashes
- ✅ Exponential backoff (won't spam restarts)
- ✅ Starts on boot
- ✅ Proper logging via journald
- ✅ Resource limits (512MB RAM, 50% CPU)

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/image <desc>` | Generate image from description |
| `/mermaid <code>` | Create Mermaid diagram |
| Send text | Chat with AI |
| Send URL | Summarize web page |
| Send voice/audio | Transcribe + summarize |
| Send PDF/DOC/PPT | Summarize document |

## API Keys

### Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather)
2. Create bot with `/newbot`
3. Copy the token

### OpenAI API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new key

## Screenshots

![Audio Processing](./data/audio_example.png)
![Chat Example](./data/chat_example.png)

## License

MIT License
