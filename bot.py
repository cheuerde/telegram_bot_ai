#!/usr/bin/env python3
"""
Telegram Bot AI - Robust Production Version

Features:
- Voice/Audio transcription (OpenAI Whisper)
- AI Chat (GPT-4o-mini)
- Image generation (DALL-E)
- Document summarization (PDF, DOC, PPT, TXT)
- URL summarization

Robustness features:
- Startup retry with exponential backoff
- Graceful error handling for transient network issues
- Proper logging
"""

import logging
import os
import sys
import time
import tempfile
import urllib.parse
import asyncio
from typing import Optional

from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
)
from telegram.error import NetworkError, TimedOut
from openai import OpenAI

import make_summary

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# Reduce noise from httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

# Global clients (initialized in main)
openai_client: Optional[OpenAI] = None
temp_dir: Optional[str] = None


def is_url(string: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urllib.parse.urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using OpenAI Whisper API."""
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language=None  # Auto-detect language
            )
        return transcript.text if hasattr(transcript, 'text') else transcript
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise Exception(f"Transcription Error: {str(e)}")


def create_summary(text: str) -> str:
    """Create a concise bullet-point summary using GPT-4o-mini."""
    try:
        # Detect if text is German or English
        german_words = ['und', 'der', 'die', 'das', 'ist', 'eine', 'ein', 'ich', 'bin', 'haben', 'sind']
        is_german = any(word in text.lower() for word in german_words)

        if is_german:
            prompt = f"""Erstelle eine präzise Zusammenfassung des folgenden Textes auf Deutsch:

REGELN:
- Maximal 3-5 Stichpunkte
- Jeder Punkt maximal 15 Wörter
- Nur die wichtigsten Informationen
- Verwende Bullet Points (•)

TEXT:
{text}

ZUSAMMENFASSUNG:"""
        else:
            prompt = f"""Create a precise summary of the following text in English:

RULES:
- Maximum 3-5 bullet points
- Each point maximum 15 words
- Only the most important information
- Use bullet points (•)

TEXT:
{text}

SUMMARY:"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at creating concise, bullet-point summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Summary error: {e}")
        return f"Summary Error: {str(e)}"


# ============ Command Handlers ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋 Hi! I'm your AI assistant bot.\n\n"
             "I can:\n"
             "• 🎤 Transcribe voice messages\n"
             "• 💬 Chat with you (just send text)\n"
             "• 🖼️ Generate images (/image description)\n"
             "• 📄 Summarize documents (PDF, DOC, PPT)\n"
             "• 🌐 Summarize URLs (just paste a link)\n"
             "• 📊 Create diagrams (/mermaid code)"
    )


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /caps command - convert text to uppercase."""
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


async def voice_message(update: Update, context: CallbackContext):
    """Handle voice messages - transcribe and summarize."""
    out_file_name = os.path.join(temp_dir, "voice_received.oga")

    try:
        file_id = update.message.voice.file_id
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(out_file_name)
        await update.message.reply_text('🎤 Processing voice message...')

        # Transcribe
        transcription = transcribe_audio(out_file_name)
        response = transcription

        # Add summary
        try:
            summary = create_summary(transcription)
            response += "\n\n📋 **Summary:**\n" + summary
        except Exception as e:
            logger.error(f"Summary failed: {e}")
            response += "\n\n⚠️ Summary unavailable"

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Voice message error: {e}")
        await update.message.reply_text("❌ Failed to process voice message")


async def audio_message(update: Update, context: CallbackContext):
    """Handle audio files - transcribe and summarize."""
    out_file_name = os.path.join(temp_dir, "audio_received.oga")

    try:
        file_id = update.message.audio.file_id
        file = await context.bot.get_file(file_id)
        await file.download_to_drive(out_file_name)
        await update.message.reply_text('🎵 Processing audio file...')

        # Transcribe
        transcription = transcribe_audio(out_file_name)
        response = transcription

        # Add summary
        try:
            summary = create_summary(transcription)
            response += "\n\n📋 **Summary:**\n" + summary
        except Exception as e:
            logger.error(f"Summary failed: {e}")
            response += "\n\n⚠️ Summary unavailable"

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Audio message error: {e}")
        await update.message.reply_text("❌ Failed to process audio file")


async def file_receive(update: Update, context: CallbackContext):
    """Handle document uploads - extract and summarize."""
    try:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        file = await context.bot.get_file(file_id)
        out_file_name = os.path.join(temp_dir, file_name)
        await file.download_to_drive(out_file_name)
        await update.message.reply_text('📁 File received, processing...')

        _, file_extension = os.path.splitext(out_file_name)
        summary_file_name = os.path.join(temp_dir, 'pdf_summary.pdf')

        if file_extension.upper() == '.PDF':
            await update.message.reply_text('📄 Creating PDF summary...')
            out = make_summary.pdf_to_summary(out_file_name, summary_file_name)

        elif file_extension.upper() in ['.DOC', '.DOCX']:
            await update.message.reply_text('📝 Creating Word document summary...')
            out = make_summary.docx_to_summary(out_file_name, summary_file_name)

        elif file_extension.upper() in ['.PPT', '.PPTX']:
            await update.message.reply_text('📊 Creating PowerPoint summary...')
            out = make_summary.pptx_to_summary(out_file_name, summary_file_name)

        elif file_extension.upper() == '.TXT':
            await update.message.reply_text('📃 Creating text file summary...')
            out = make_summary.txt_to_summary(out_file_name, summary_file_name)

        else:
            await update.message.reply_text(f'⚠️ Unsupported file type: {file_extension}')
            return

        if out[0] == "Error":
            await update.message.reply_text(f"❌ {out[1]}")
        else:
            await update.message.reply_text(f"✅ {out[1]}")
            with open(out[0], 'rb') as document:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=document)

    except Exception as e:
        logger.error(f"File processing error: {e}")
        await update.message.reply_text("❌ Failed to process file")


async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /image command - generate images with DALL-E."""
    try:
        prompt_in = ' '.join(context.args)
        if not prompt_in:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Usage: /image <description>\nExample: /image a cat wearing a hat"
            )
            return

        await context.bot.send_message(chat_id=update.effective_chat.id, text="🎨 Generating image...")

        out = openai_client.images.generate(
            prompt=prompt_in,
            n=1,
            size="512x512",
        )

        response = out.data[0].url
        await context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=response)

    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Image generation failed (prompt may have been refused)"
        )


async def mermaid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mermaid command - generate diagrams."""
    try:
        prompt_in = ' '.join(context.args)
        if not prompt_in:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Usage: /mermaid <diagram code>\nExample: /mermaid graph TD; A-->B; B-->C;"
            )
            return

        command_file_name = os.path.join(temp_dir, 'mm_in.txt')
        with open(command_file_name, "w") as f:
            f.write(prompt_in)

        out_file_name = os.path.join(temp_dir, 'out.png')
        out_file_name_pdf = os.path.join(temp_dir, 'out.pdf')

        os.system(f'mmdc -i {command_file_name} -o {out_file_name}')
        os.system(f'mmdc -i {command_file_name} -o {out_file_name_pdf}')

        with open(out_file_name, 'rb') as photo:
            await context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=photo)
        with open(out_file_name_pdf, 'rb') as document:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=document)

    except Exception as e:
        logger.error(f"Mermaid generation error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Mermaid diagram generation failed"
        )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - chat or URL summarization."""
    prompt_in = update.message.text

    # Check if it's a URL
    if is_url(prompt_in):
        await update.message.reply_text('🌐 Summarizing URL...')
        summary_file_name = os.path.join(temp_dir, 'pdf_summary.pdf')

        try:
            out = make_summary.url_to_summary(prompt_in, summary_file_name)

            if out[0] == "Error":
                await update.message.reply_text(f"❌ {out[1]}")
            else:
                await update.message.reply_text(f"✅ {out[1]}")
                with open(out[0], 'rb') as document:
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=document)
        except Exception as e:
            logger.error(f"URL summarization error: {e}")
            await update.message.reply_text("❌ Failed to summarize URL")
        return

    # Regular chat message
    try:
        response_obj = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond naturally and concisely in the same language as the user's message. Keep responses under 150 words unless more detail is specifically requested."
                },
                {"role": "user", "content": prompt_in}
            ],
            max_tokens=300,
            temperature=0.7
        )

        response = response_obj.choices[0].message.content
        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        await update.message.reply_text("❌ Failed to generate response")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors gracefully."""
    logger.error(f"Exception while handling an update: {context.error}")

    # Don't crash on network errors - they're usually transient
    if isinstance(context.error, (NetworkError, TimedOut)):
        logger.warning("Network error occurred, will retry automatically")
        return

    # For other errors, try to notify user if possible
    if update and hasattr(update, 'effective_chat'):
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ An error occurred. Please try again."
            )
        except Exception:
            pass


def run_bot_with_retry(telegram_api_key: str, max_retries: int = None, base_delay: float = 5.0):
    """
    Run the bot with exponential backoff retry on startup failures.
    
    Args:
        telegram_api_key: Telegram bot API token
        max_retries: Maximum retry attempts (None = infinite)
        base_delay: Initial delay between retries in seconds
    """
    global openai_client, temp_dir

    # Initialize OpenAI client
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Temp directory: {temp_dir}")

    # Build application
    application = ApplicationBuilder().token(telegram_api_key).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('caps', caps))
    application.add_handler(CommandHandler('mermaid', mermaid))
    application.add_handler(CommandHandler('image', image))
    application.add_handler(MessageHandler(filters.VOICE, voice_message))
    application.add_handler(MessageHandler(filters.AUDIO, audio_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    application.add_handler(MessageHandler(filters.Document.ALL, file_receive))

    # Add error handler
    application.add_error_handler(error_handler)

    # Retry loop for startup
    attempt = 0
    while True:
        attempt += 1
        delay = min(base_delay * (2 ** (attempt - 1)), 300)  # Cap at 5 minutes

        try:
            logger.info(f"Starting bot (attempt {attempt})...")
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
            )
            # If we get here, bot exited cleanly
            logger.info("Bot stopped cleanly")
            break

        except NetworkError as e:
            logger.warning(f"Network error on startup (attempt {attempt}): {e}")
            if max_retries and attempt >= max_retries:
                logger.error(f"Max retries ({max_retries}) reached, giving up")
                raise

            logger.info(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break

        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt}): {e}")
            if max_retries and attempt >= max_retries:
                logger.error(f"Max retries ({max_retries}) reached, giving up")
                raise

            logger.info(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)


if __name__ == '__main__':
    # Get API keys from environment
    telegram_api_key = os.environ.get("TELEGRAM_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if not telegram_api_key:
        logger.error("TELEGRAM_API_KEY environment variable not set")
        sys.exit(1)

    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    logger.info("=" * 50)
    logger.info("Telegram Bot AI - Starting")
    logger.info("=" * 50)

    # Run with infinite retries (systemd will handle permanent failures)
    run_bot_with_retry(telegram_api_key, max_retries=None)
