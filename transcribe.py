import json
import os
from util import *
from util_transcription import *


def transcribe_podcasts(source_file_path, destination_folder="txt"):
    os.makedirs(destination_folder, exist_ok=True)  # Create the folder if it doesn't exist

    file_to_be_transcribed = []
    with open(source_file_path, 'r') as f:
        data = json.load(f)
    
    for audiofile in data:
        subfolder = generate_python_friendly_filename(audiofile["podcast_name"])
        file_name = generate_python_friendly_filename(audiofile["name"]) + ".txt"
        file_path = os.path.join(destination_folder,subfolder, file_name)
        if  check_file(file_path):
            print(f"File exists: {file_path}")
        else:
            print(f"Episode Link: {audiofile["episode_link"]}")

            file_to_be_transcribed.append(
                    {'filepath':file_path, 
                     'link': audiofile["link"], 
                     'episode_link': audiofile["episode_link"],
                     'name': audiofile["name"],
                     'podcast_name': audiofile["podcast_name"]
                     })
            
    for f in file_to_be_transcribed:
        transcription_text = transcribe (f['link'], f['filepath'])
        transcription_object = {
            "Episode Name": f["name"],
            "Podcast Name": f["podcast_name"],
            "Episode Link": f["episode_link"],
            "text": transcription_text
        }

        create_file(f['filepath'], json.dumps(transcription_object))



