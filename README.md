# telegram_bot_ai

Telegram bot that uses AI tools for chat, image and audio

# Dependencies

 - [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
 - [openai](https://github.com/openai/openai-python)
 - [whisper](https://github.com/openai/whisper)
 - [A telegram bot with API Key](https://core.telegram.org/bots/tutorial)
 - [An OpenAI API Key](https://elephas.app/blog/how-to-create-openai-api-keys-cl5c4f21d281431po7k8fgyol0)

# Functions

 - [x] Instruction chat with bot (through openai davinci)
 - [x] Image generation (through openai DALLE, trigger with `/image`)
 - [x] Voice message transcription and summary (through openai whisper + davinci)
 - [ ] Generate [stories](https://github.com/cheuerde/story_generator)
 - [ ] Text to speech (read stories)

# Usage

```sh
export TELEGRAM_API_KEY="your_telegram_api_key"
export OPENAI_API_KEY="your_openai_api_key"

python3 bot.py
```

