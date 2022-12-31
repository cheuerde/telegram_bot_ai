# using a huggingface inference API endpoint
# NOTE: without paying for some inference endpoint, this is 
# too unreliable because of queuing for free users. Better
# to have the whisper model running locally (up until "small" model size)
import json
from typing import List
import requests as r
import base64
import mimetypes

import requests

hugginface_api_key = os.environ.get("HUGGINGFACE_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-medium"
headers= {
    "Authorization": f"Bearer {hugginface_api_key}",
}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

output = query("voice_received.oga")

def predict(path_to_audio:str=None):
    # read audio file
    with open(path_to_audio, "rb") as i:
      b = i.read()
    # get mimetype
    content_type= mimetypes.guess_type(path_to_audio)[0]

    headers= {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": content_type
    }
    response = r.post(ENDPOINT_URL, headers=headers, data=b)
    return response.json()

prediction = predict(path_to_audio="sample1.flac")

prediction
