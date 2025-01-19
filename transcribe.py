import json
import os
from util import *
from util_transcription import *


def transcribe_podcasts(source_file_path, destination_folder="txt"):
    os.makedirs(destination_folder, exist_ok=True)  # Create the folder if it doesn't exist
    transcribed_files = list_s3_files("podcast.monitor", "transcriptions")
    existing_transcribed_files = []
    if transcribed_files:
        for f in transcribed_files:
            existing_transcribed_files.append(f["name"])

    print (f"existing transcribed files: {existing_transcribed_files}")
    file_to_be_transcribed = []

    with open(source_file_path, 'r') as f:
        data = json.load(f)
    
    for audiofile in data:
        
        file_name = generate_python_friendly_filename(audiofile["name"]) + ".txt"
        
        if file_name in existing_transcribed_files:
            print (f"Transcription exists in s3 - {file_name}")
        else:
            file_to_be_transcribed.append(
                    {
                        # 'filepath':file_path, 
                        'filename': file_name,
                        'link': audiofile["link"], 
                        'episode_link': audiofile["episode_link"],
                        'name': audiofile["name"],
                        'podcast_name': audiofile["podcast_name"]
                    })


    
    print (f"files to be transcribed {file_to_be_transcribed}")
    for f in file_to_be_transcribed:
        transcription_text = transcribe (f['link'])
        transcription_object = {
            "Episode Name": f["name"],
            "Podcast Name": f["podcast_name"],
            "Episode Link": f["episode_link"],
            "text": transcription_text
        }
        create_s3_file(f["filename"],json.dumps(transcription_object), "transcriptions")



