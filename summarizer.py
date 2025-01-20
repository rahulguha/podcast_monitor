

from util import *

import requests


OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"


def summerize_podcasts(source, destination):
    
    transcribed_files = list_s3_files("podcast.monitor", f"transcriptions/{get_now()}" )
    summarized_files = list_s3_files("podcast.monitor", f"summary/{get_now()}" )
    if summarized_files is None:
        summarized_files = []
    if transcribed_files is None:
        transcribed_files = []
    for t in transcribed_files:
        content =""
    
        if any(s["name"] == t["name"] for s in summarized_files):
            print (f"summary file exists {t["name"]}")
        else:
            # read the transcription
            try: 
                podcast_name=""
                episode_name=""
                episode_link=""
                raw_file = read_s3_file(t["key"])
                content = json.loads(raw_file)
                podcast_name = content["Podcast Name"]
                episode_name = content["Episode Name"]
                episode_link = content["Episode Link"]
                content = content["text"]
            except KeyError:
                pass
            
            system_prompt = '''
                            Summarize the text given to you in roughly 100 words in 3 bullet points. 
                            Remove any product promotions.
                            Don't try to figure out what type of transcription it is.
                            Don't exceed the 100 word limit.
                            '''

            OLLAMA_PROMPT = f"{system_prompt}: {content}"
            OLLAMA_DATA = {
                "model": "llama3.2",
                # "model": "gemma2",
                "prompt": OLLAMA_PROMPT,
                "stream": False,
                "keep_alive": "1m",
            }
            response = requests.post(OLLAMA_ENDPOINT, json=OLLAMA_DATA)
            html_response = summary_to_html(podcast_name, episode_name, episode_link, response.json()["response"])
            create_s3_file(t["name"], html_response, "summary")
            print(f"***** Summery created for {t["name"]}")


    
def summary_text(source):
    email_body = ""
    summ_s3_files = list_s3_files("podcast.monitor", f"summary/{get_now()}/" )
    for s in summ_s3_files:
        # print(s["key"])
        content = read_s3_file(s["key"])
        email_body += "<hr>" + content
    return email_body