
import torch, whisper
from util import *

def transcribe (mp3_filename):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = whisper.load_model("tiny.en").to(device)
    txtfilepath = "txt"
    print (f"******* start transcription of {mp3_filename}")
    result = model.transcribe(mp3_filename)
    print (f"********* writing transcription ")
    return result["text"]
    
