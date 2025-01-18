import torch, whisper
import json
import os
import yt_dlp
from util import *
from util_transcription import *



txtfilepath = "txt"
file_to_be_transcribed = []
with open('video-files.json', 'r') as f:
    data = json.load(f)
    
for videofile in data:
    file_path = "txt/" + videofile["filename"]
    if  check_file(file_path):
    # if os.path.exists(file_path):
        print(f"File exists: {file_path}")
    else:
        print(f"File does not exist: {file_path}")
        file_to_be_transcribed.append({'filepath':file_path, 'link': videofile["link"]})

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'progress_hooks': [my_hook]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for dictionaryValues in file_to_be_transcribed:
        video_url = dictionaryValues['link']
        transcription_filename = dictionaryValues['filepath']
        download_filename = "mp3s/" + strip_extension( strip_before_last_slash(dictionaryValues['filepath'])) + ".webm"
        if not check_file(download_filename):
            info = ydl.extract_info(video_url, download=False)
            formats = info['formats']
            for i,format in enumerate(formats):
                # print the url
                if format['audio_ext'] == "webm":
                    audio_url = format['url'] # url for audio stream
                    with yt_dlp.YoutubeDL({'extract_audio': True,  'outtmpl': download_filename}) as video:
                            video.download(audio_url)    
                            print(f"*********** Successfully Downloaded { video_url } at {download_filename} " )
                            
                            
                            
        # assume mp3 exists
        transcribe (download_filename, transcription_filename)
