import torch, whisper
import json
import os
# import pytube as pt
import yt_dlp

ydl_opts = {}
vdo_title = "" 

def dwl_vid(video_url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def download_audio(link):
#   with yt_dlp.YoutubeDL({'extract_audio': True, 'audio-format': 'mp4', 'outtmpl': 'mp3s/%(title)s.mp3'}) as video:
    # with yt_dlp.YoutubeDL({'extract_audio': True, 'audio-format': 'mp4', 'outtmpl': 'mp3s/%(title)s.mp3'}) as video:
    with yt_dlp.YoutubeDL({'extract_audio': True, 'audio-format': 'mp3',  'outtmpl': 'mp3s/%(title)s'}) as video:
        info_dict = video.extract_info(link, download = True)
        print(info_dict)
        video_title = info_dict['title']
        print(video_title)
        video.download(link)    
        vdo_title = "mp3s/" + video_title + ".opus"
        print("Successfully Downloaded " + vdo_title )

download_audio('https://www.youtube.com/watch?v=hZhBE3hw5P4')



device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = whisper.load_model("tiny.en").to(device)
txtfilepath = "txt"
result = model.transcribe(vdo_title)
with open("/txt" + vdo_title + ".txt", "w") as f:   # Opens file and casts as f 
    f.write(result["text"] )       # Writing

# file_to_be_transcribed = []
# with open('audio-files.json', 'r') as f:
#     data = json.load(f)

# for audiofile in data:
#     file_path = "txt/" + audiofile["filename"]
#     if os.path.exists(file_path):
#         print(f"File exists: {file_path}")
#     else:
#         print(f"File does not exist: {file_path}")
#         file_to_be_transcribed.append({'filepath':file_path, 'link': audiofile["link"]})
        
# for dictionaryValues in file_to_be_transcribed:
#     result = model.transcribe(dictionaryValues['link'])
#     with open(dictionaryValues['filepath'], "w") as f:   # Opens file and casts as f 
#         f.write(result["text"] )       # Writing
