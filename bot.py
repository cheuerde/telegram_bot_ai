import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
import requests
import os
import sqlite3
import openai
import json
import time
import tempfile
import urllib.parse
from base64 import b64decode
import whisper
import make_summary

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def is_url(string):
  try:
    result = urllib.parse.urlparse(string)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text_caps = ' '.join(context.args).upper()
  await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

#async def whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
#  model_in = ' '.join(context.args)
#
#  # check if model_in is one of the valid model sizes of whiser (tiny, base, small, medium, large)
#
#  # if not, return error message
#  if model_in not in ["tiny", "base", "small", "medium", "large"]:
#    await context.bot.send_message(chat_id=update.effective_chat.id, text="Model size not valid. Valid sizes are: tiny, base, small, medium, large")
#
#  else:
#
#    # if yes, set model
#    whisper_model = whisper.load_model(model_in)
#
#    # send message confirming the change
#    await context.bot.send_message(chat_id=update.effective_chat.id, text="Model set to: " + model_in)

# voice message receive (https://stackoverflow.com/a/72177751)
async def voice_message(update: Update, context: CallbackContext):
  # get basic info about the voice note file and prepare it for downloading
  #await context.bot.get_file(update.message.voice.file_id).download(out = open("voice_message.ogg", 'wb'))
  out_file_name = os.path.join(temp_dir, "voice_received.oga")

  file_id = update.message.voice.file_id
  file = await context.bot.get_file(file_id)
  await file.download_to_drive(out_file_name)
  await update.message.reply_text('Audio File saved - Processing and making summary')

  summary_header = "\n\n=======\nSummary\n=======\n"

  try:

    result = whisper_model.transcribe(out_file_name)
    out_test = result["text"]

    response = out_test

    try:

      # create openai response
      prompt_in = "Create a brief summary in the language of the message of the following message: " + out_test

      out = openai.Completion.create(
        model="text-davinci-003",
        #model = "text-curie-001",
        prompt = prompt_in,
        max_tokens=1000,
        temperature=0.7
      )

      json_object = json.loads(str(out))
      response_summary = json_object['choices'][0]['text']

      response = response + summary_header + response_summary

    except Exception as et:

      response = response + summary_header + "OpenAI Error"
      # response = context.args

  except Exception as et:

    response = "Whisper Error"

  await update.message.reply_text(response)


async def audio_message(update: Update, context: CallbackContext):
  # get basic info about the voice note file and prepare it for downloading
  #await context.bot.get_file(update.message.voice.file_id).download(out = open("voice_message.ogg", 'wb'))
  out_file_name = os.path.join(temp_dir, "audio_received.oga")
  file_id = update.message.audio.file_id
  file = await context.bot.get_file(file_id)
  await file.download_to_drive(out_file_name)
  await update.message.reply_text('Audio File saved - Processing and making summary')

  summary_header = "\n\n=======\nSummary\n=======\n\n"

  try:

    result = whisper_model.transcribe(out_file_name)
    out_test = result["text"]

    response = out_test

    try:

      # create openai response
      prompt_in = "Create a brief summary in the language of the message of the following message: " + out_test

      out = openai.Completion.create(
        model="text-davinci-003",
        #model = "text-curie-001",
        prompt = prompt_in,
        max_tokens=1000,
        temperature=0.7
      )

      json_object = json.loads(str(out))
      response_summary = json_object['choices'][0]['text']

      response = response + summary_header + response_summary

    except Exception as et:

      response = response + summary_header + "OpenAI Error"
      # response = context.args

  except Exception as et:

    response = "Whisper Error"

  await update.message.reply_text(response)


async def file_receive(update: Update, context: CallbackContext):
  file_id = update.message.document.file_id
  file_name = update.message.document.file_name
  file = await context.bot.get_file(file_id)
  out_file_name = os.path.join(temp_dir, file_name)
  await file.download_to_drive(out_file_name)
  await update.message.reply_text('File saved')

  # now check if its a pdf
  _, file_extension = os.path.splitext(out_file_name)

  if file_extension.upper() in ['.PDF', '.DOC', '.DOCX', '.PPT', '.PPTX']:

    if file_extension.upper() == '.PDF':

      await update.message.reply_text('Making Summary of PDF')
      summary_file_name = os.path.join(temp_dir, 'pdf_summary.pdf')

      out = make_summary.pdf_to_summary(out_file_name, summary_file_name)

    elif file_extension.upper() in ['.DOC','.DOCX']:

      await update.message.reply_text('Making Summary of DOC')
      summary_file_name = os.path.join(temp_dir, 'pdf_summary.pdf')

      out = make_summary.docx_to_summary(out_file_name, summary_file_name)

    elif file_extension.upper() in ['.PPT','.PPTX']:

      await update.message.reply_text('Making Summary of PPT')
      summary_file_name = os.path.join(temp_dir, 'pdf_summary.pdf')

      out = make_summary.pptx_to_summary(out_file_name, summary_file_name)

    if out[0] == "Error":
      await update.message.reply_text(out[1])
    else: 
      await update.message.reply_text(out[1])
      document = open(out[1], 'rb')
      await update.send_document(chat_id, document)
      await update.message.reply_text(out[0])



async def image(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try: 

    prompt_in = ' '.join(context.args)

    out = openai.Image.create(
      prompt = prompt_in,
      n=1,
      #size="256x256",
      size="512x512",
      #size="1024x1024",
      #response_format="b64_json"
      response_format="url"
    )

    json_object = json.loads(str(out))
    response = json_object['data'][0]['url']
    await context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=response)

  except Exception as e:
    response = "Prompt refused by OpenAI API"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):

  prompt_in = update.message.txt
  if is_url(prompt_in):

    await update.message.reply_text('Making Summary of URL')
    summary_file_name = os.path.join(temp_dir, 'pdf_summary.pdf')

    out = make_summary.url_to_summary(out_file_name, summary_file_name)

    if out[0] == "Error":
      await update.message.reply_text(out[1])
    else: 
      await update.message.reply_text(out[1])
      document = open(out[1], 'rb')
      await update.send_document(chat_id, document)
      await update.message.reply_text(out[0])
  else:
  try:

# create openai response

     out = openai.Completion.create(
       model="text-davinci-003",
       #model = "text-curie-001",
       prompt = prompt_in,
       max_tokens=1000,
       temperature=0.7
     )

     json_object = json.loads(str(out))
     response = json_object['choices'][0]['text']

  except Exception as et:

    response = "OpenAI error"

  await update.message.reply_text(response)

if __name__ == '__main__':

  # get the api token from the env varialbe teelgram_api_key
  telegram_api_key = os.environ.get("TELEGRAM_API_KEY")
  
  openai.api_key = os.environ.get("OPENAI_API_KEY")

  whisper_model = whisper.load_model("small")

  temp_dir = tempfile.mkdtemp()

  start_handler = CommandHandler('start', start)
  caps_handler = CommandHandler('caps', caps)
  voice_message_handler = MessageHandler(filters.VOICE, voice_message)
  audio_message_handler = MessageHandler(filters.AUDIO, audio_message)
  file_receive_handler = MessageHandler(filters.Document.ALL, file_receive)
  image_handler = CommandHandler('image', image)
  #whisper_handler = CommandHandler('whisper', whisper)
  gpt_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, gpt)

  # and the handler when no command was entered and we just respond to the message
  application = ApplicationBuilder().token(telegram_api_key).build()

  application.add_handler(start_handler)
  application.add_handler(caps_handler)
  application.add_handler(voice_message_handler)
  application.add_handler(audio_message_handler)
  application.add_handler(image_handler)
  #application.add_handler(whisper_handler)
  application.add_handler(gpt_handler)
  application.add_handler(file_receive_handler)

  application.run_polling()
