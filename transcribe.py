import json

from util import *
from util_transcription import *


def transcribe_podcasts(source_file_path):
    
    transcribed_files = list_s3_files(get_bucket_name(), "transcriptions")
    
    # print (transcribed_files[0])
    existing_transcribed_files = []
    if transcribed_files:
        for f in transcribed_files:            
            existing_transcribed_files.append(f["name"])
    
    log("debug", f"transcription::existing transcription files - {len(existing_transcribed_files)}")
    file_to_be_transcribed = []
    with open(source_file_path, 'r') as f:
        data = json.load(f)
    
    for audiofile in data:
        file_name = generate_python_friendly_filename(audiofile["name"]) + ".txt"
        

        if  file_name in existing_transcribed_files:
            log("debug", f"transcription::transcription exists - {file_name}")
            # print (f"Transcription exists in s3 - {file_name}")
        else:
            file_to_be_transcribed.append(
                    {
                        'filename': file_name,
                        'link': audiofile["link"], 
                        'episode_link': audiofile["episode_link"],
                        'name': audiofile["name"],
                        'podcast_name': audiofile["podcast_name"],
                        'duration': audiofile["duration"],
                        'pub_time': audiofile["pub_time"]
                    })
    # print(len(file_to_be_transcribed))
    log("debug", f"transcription::# of audio to be transcribed - {len(file_to_be_transcribed)}")
    for f in file_to_be_transcribed:
        transcription_text = transcribe (f['link'])
        transcription_object = {
            "Episode Name": f["name"],
            "Podcast Name": f["podcast_name"],
            "Episode Link": f["episode_link"],
            "duration": f["duration"],
            "text": transcription_text
        }
        log("debug", f"transcription::transcribed object metadata - \nEpisode Name - {transcription_object['Episode Name']} ")
        create_s3_file(f["filename"],json.dumps(transcription_object), "transcriptions")



