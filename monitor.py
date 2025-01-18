
from monitor_podcast import *
from util import *
from transcribe1 import *
# from summarizers import *
from summarizer1 import *


from dotenv import load_dotenv
load_dotenv()
cutoff_date = str_to_datetime( os.getenv('CUTOFFDATE', '2025/1/3'), "%Y/%m/%d")
transcrfiption_folder=os.getenv("TRANSCRIPTIONFOLDER", "transcribed")

feeds = load_json("content_monitor.json")
episodes = monitor_podcast(feeds, cutoff_date)

persist_episodes_to_be_processed(episodes, "to_be_processed.json")
transcribe_podcasts("to_be_processed.json", transcrfiption_folder)

summerize_podcasts("transcribed", "podcast_summary")

send_mail(summary_text("podcast_summary"))
