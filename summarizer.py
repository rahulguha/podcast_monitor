

from util import *

import requests


OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"


def summerize_podcasts(source, destination):
    
    transcribed_files = list_s3_files(get_bucket_name(), f"transcriptions" )
    
    summarized_files = list_s3_files(get_bucket_name(), f"summary" )
    if transcribed_files:
        log("info", f"summarization::# transcribed files - {len(transcribed_files)}")
    if summarized_files:
        log("info", f"summarization::# summary files - {len(summarized_files)}")
    if summarized_files is None:
        summarized_files = []
    if transcribed_files is None:
        transcribed_files = []
    
    # print(f"transcribed files {len(transcribed_files)}")
    # print(f"summarized files {len(summarized_files)}")
    for t in transcribed_files:
        content =""
        duration = ""
    
        if any(s["name"] == t["name"] for s in summarized_files):
            # print (f"summary file exists {t["name"]}")
            log("debug", f"summarization::# summary files exists - {t['name']}")
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
                duration = content["duration"] 
                if duration == "":
                    duration = "duration not found"
                content = content["text"]
            except KeyError:
                pass
            
            system_prompt = '''
                            Summarize the text given to you in 3 bullet points roughly 100 words in length. 
                            Remove any product promotions.
                            Be specific, remove any guesses, use third person like "This episodes talks about ..."
                            Please don't use following word "trinscription", "appears to" etc.
                            Don't exceed the 100 word limit. Be formal about your style
                            '''

            OLLAMA_PROMPT = f"{system_prompt}: {content}"
            OLLAMA_DATA = {
                "model": "llama3.2",
                # "model": "deepseek-r1",
                # "model": "gemma2",
                "prompt": OLLAMA_PROMPT,
                "stream": False,
                "keep_alive": "1m",
            }
            response = requests.post(OLLAMA_ENDPOINT, json=OLLAMA_DATA)
            html_response = summary_to_html(podcast_name, episode_name, episode_link, f"{get_now()}", duration, response.json()["response"])
            create_s3_file(t["name"], html_response, "summary")
            log("info", f"summarization::# summary created successfully - {t["name"]}")
    
def summary_text(source):
    email_body = ""
    # cutoff_date = get_cutoff_date()
    folders = get_s3_folders("summary/")
    # print(folders)
    summ_s3_files = []
    summ_filenames = []
    folder_content = list_s3_files(get_bucket_name(), f"summary" )
    for f in folder_content:
        filename = strip_before_last_slash(f["key"])
        if not filename in summ_filenames:
            summ_s3_files.append(f)
            summ_filenames.append(filename)
        # print(f['name'])
    # for f in folders: 
    #     # print (len(summ_s3_files))
    #     folder_content = list_s3_files(get_bucket_name(), f"summary" )
    #     # print(folder_content)
    #     for f in folder_content:
    #         # get filename - then compare with array of summary filenames - if not match add
    #         filename = strip_before_last_slash(f["key"])
    #         if not filename in summ_filenames:
    #             # add in both array
    #             summ_s3_files.append(f)
    #             summ_filenames.append(filename)
    
    summ_s3_files = sorted(
        summ_s3_files, 
        key=lambda x: x['last_modified'], 
        reverse=True  # Optional: descending order
        )
    if summ_s3_files:
        for s in summ_s3_files:
            content = read_s3_file(s["key"])
            email_body += "<hr>" + content
        return email_body