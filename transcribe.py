import torch, whisper
import json
import os
from util import *
from util_transcription import *

txtfilepath = "txt"
file_to_be_transcribed = []
with open('audio-files.json', 'r') as f:
    data = json.load(f)

for audiofile in data:
    file_path = "txt/" + audiofile["filename"]
    if  check_file(file_path):
        print(f"File exists: {file_path}")
    else:
        print(f"File does not exist: {file_path}")
        file_to_be_transcribed.append({'filepath':file_path, 'link': audiofile["link"]})
        
for dictionaryValues in file_to_be_transcribed:
    transcribe (dictionaryValues['link'], dictionaryValues['filepath'])
