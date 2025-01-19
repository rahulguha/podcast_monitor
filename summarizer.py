import os
import glob

from util import *

import requests


OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"


def summerize_podcasts(source, destination):
    
    if not check_folder_exists(source):
        print (f"Source folder doesn't exist {source}")
        stop_program_if_condition(True)
    
    
    os.makedirs(destination, exist_ok=True)  # Create the folder if it doesn't exist
    destination_subfolders = get_subfolders(source)
    
    if len(destination_subfolders) > 0:
        for subfolder in destination_subfolders:
            existing_file_names = []
            destination_s3_files = list_s3_files("podcast.monitor", f"summary/{get_now()}/{subfolder}" )
            if destination_s3_files:
                for s in destination_s3_files:
                    existing_file_names.append(s["name"])
            source_subfolder_path = os.path.join(source, subfolder)
            # destination_subfolder_path = os.path.join(destination, subfolder)
            # os.makedirs(destination_subfolder_path, exist_ok=True)  # Create Subfolders
            source_files = glob.glob(source_subfolder_path + "/*.*") # read all files
            
            for source_file in source_files:
                file_name = strip_extension(strip_before_last_slash(source_file)) + ".txt"
                # summery_file_name = os.path.join(destination, subfolder,  file_name)
                print (existing_file_names)
                print (file_name)
                if file_name in existing_file_names:
                    print(f"file exists in s3 {file_name}")
                else:
                    summery_file_name = os.path.join( subfolder,  file_name)
                    try: 
                        podcast_name=""
                        episode_name=""
                        episode_link=""
                        with open(source_file, 'r') as file:
                            content = json.load(file)
                            podcast_name = content["Podcast Name"]
                            episode_name = content["Episode Name"]
                            episode_link = content["Episode Link"]
                            content = content["text"]
                    except KeyError:
                        pass
                            
                    system_prompt = '''
                        Your goal is to summarize the text given to you in roughly 100 words with 3 bullet points. 
                        Include the name and the Episode link to the episode.
                        Please remove any product promotions.

                        Try not to exceed the word limit.
                        '''
                    # conversation_string = load_conversation_data()

                    OLLAMA_PROMPT = f"{system_prompt}: {content}"
                    OLLAMA_DATA = {
                        "model": "llama3.2",
                        # "model": "gemma2",
                        "prompt": OLLAMA_PROMPT,
                        "stream": False,
                        "keep_alive": "1m",
                    }
                    # response = requests.post(OLLAMA_ENDPOINT, json=OLLAMA_DATA)
                    response = requests.post(OLLAMA_ENDPOINT, json=OLLAMA_DATA)
                    html_response = summary_to_html(podcast_name, episode_name, episode_link, response.json()["response"])
                    # create_file(summery_file_name, response.json()["response"])
                    # create_file(summery_file_name, html_response)
                    create_s3_file(summery_file_name, html_response, "summary")
                    print(f"***** Summery created for {source_file} to {summery_file_name}")
                        # print(response.json()["response"])
                # else:
                #     print (f"{summery_file_name} already exists. Skipping ...")
    
def summary_text(source):
    email_body = ""
    summ_s3_files = list_s3_files("podcast.monitor", f"summary/{get_now()}/" )
    for s in summ_s3_files:
        print(s["key"])
        content = read_s3_file(s["key"])
        email_body += "<hr>" + content
    return email_body