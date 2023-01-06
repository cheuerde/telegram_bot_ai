# using a huggingface inference API endpoint
# NOTE: without paying for some inference endpoint, this is 
# too unreliable because of queuing for free users. Better
# to have the whisper model running locally (up until "small" model size)
import json
from typing import List
import requests as r
import base64
import mimetypes
import os

huggingface_api_key = os.environ.get("HUGGINGFACE_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-medium"

file = "sample1.flac"

headers= {
    "Authorization": f"Bearer {huggingface_api_key}",
}

def predict(path_to_audio:str=None):
    # read audio file
    with open(path_to_audio, "rb") as i:
      b = i.read()
    # get mimetype
    content_type= mimetypes.guess_type(path_to_audio)[0]
    headers= {
        "Authorization": f"Bearer {huggingface_api_key}",
        "Content-Type": content_type
    }
    response = r.post(API_URL, headers=headers, data=b)
    return response.json()

prediction = predict(path_to_audio=file)

prediction
