# Telegram Bot AI

A telegram bot for voice transcription, text generation, image creation, and document processing.

## ✨ Features

- 🎤 **Voice/Audio Transcription** - High-quality speech-to-text using OpenAI Whisper API
- 💬 **AI Chat** - Intelligent conversations powered by GPT-3.5-turbo-instruct
- 🖼️ **Image Generation** - Create images from text descriptions using DALL-E
- 📄 **Document Summarization** - Automatic summaries for PDF, DOC, PPT, and TXT files
- 🌐 **URL Summarization** - Extract and summarize content from web pages
- 📊 **Mermaid Diagrams** - Generate flowcharts and diagrams from text descriptions

## 🛠️ Dependencies

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) >=21.0
- [openai](https://github.com/openai/openai-python) >=1.0.0
- [pdfminer](https://pypi.org/project/pdfminer/) - PDF text extraction
- [python-docx](https://pypi.org/project/python-docx/) - Word document processing
- [python-pptx](https://pypi.org/project/python-pptx/) - PowerPoint processing
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - Web scraping
- [requests](https://pypi.org/project/requests/) - HTTP library

## 🚀 Quick Setup with UV (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/cheuerde/telegram_bot_ai.git
   cd telegram_bot_ai
   ```

2. **Set up environment variables**
   ```bash
   export TELEGRAM_API_KEY="your_telegram_bot_token"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

3. **Run the setup script**
   ```bash
   bash set_uv_env.sh
   ```

4. **Start the bot**
   ```bash
   bash run_app.sh
   ```

## 🔄 Production Setup (Auto-Restart & Monitoring)

For reliable production deployment on your server:

1. **Setup monitoring system**
   ```bash
   bash setup_monitoring.sh
   ```

2. **Add cron job for auto-monitoring** (every 2 minutes)
   ```bash
   crontab -e
   # Add this line:
   */2 * * * * /path/to/telegram_bot_ai/monitor_bot.sh >> /path/to/telegram_bot_ai/logs/cron.log 2>&1
   ```

3. **Add weekly log rotation** (optional, prevents logs from growing too large)
   ```bash
   crontab -e
   # Add this line:
   0 2 * * 0 /path/to/telegram_bot_ai/rotate_logs.sh
   ```

4. **Bot management commands**
   ```bash
   ./monitor_bot.sh start    # Start the bot
   ./monitor_bot.sh stop     # Stop the bot  
   ./monitor_bot.sh restart  # Restart the bot
   ./monitor_bot.sh status   # Check bot status
   ```

### 🛡️ Monitoring Features
- **Auto-restart** on crashes or hangs
- **Smart failure detection** (checks for errors in logs)
- **Restart limits** (max 5 restarts to prevent infinite loops)
- **Comprehensive logging** (bot output, monitoring events, cron activity)
- **Log rotation** (prevents disk space issues)
- **PID tracking** (reliable process management)

## 📋 Manual Setup

If you prefer manual installation:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_API_KEY="your_telegram_bot_token"
export OPENAI_API_KEY="your_openai_api_key"

# Run the bot
python bot.py
```

## 🎯 Bot Commands & Features

### Text Commands
- **General Chat** - Just send any text message for AI-powered responses
- `/start` - Initialize the bot
- `/caps [text]` - Convert text to uppercase
- `/image [description]` - Generate images from text descriptions
- `/mermaid [diagram_code]` - Create Mermaid diagrams

### File Processing
- **Voice Messages** - Automatic transcription + summary
- **Audio Files** - Transcription + summary  
- **PDF Files** - Text extraction + summary
- **Word Documents** (.doc, .docx) - Content extraction + summary
- **PowerPoint** (.ppt, .pptx) - Content extraction + summary
- **Text Files** (.txt) - Content summary
- **URLs** - Web page content extraction + summary

## 🔧 API Requirements

### Telegram Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the provided API token

### OpenAI API Key
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Ensure you have credits/billing set up

## 🎨 Technologies Used

- **OpenAI Whisper API** - Advanced speech-to-text transcription
- **GPT-3.5-turbo-instruct** - Text generation and chat
- **DALL-E** - AI image generation
- **Python-telegram-bot** - Telegram Bot API wrapper
- **UV** - Fast Python package installer

## 📸 Screenshots

![Audio Processing Example](./data/audio_example.png)

![Chat Example](./data/chat_example.png)

## 🔄 Recent Updates

- ✅ Migrated from local Whisper to OpenAI Whisper API
- ✅ Updated to latest OpenAI Python client (v1.0+)
- ✅ Removed heavy dependencies (PyTorch, Transformers)
- ✅ Added UV-based environment management
- ✅ Improved error handling and fallbacks

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
