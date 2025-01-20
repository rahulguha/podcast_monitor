
from monitor_podcast import *
from util import *
from transcribe import *
from summarizer import *

from dotenv import load_dotenv
load_dotenv()
cutoff_date = str_to_datetime( os.getenv('CUTOFFDATE', '2025/1/3'), "%Y/%m/%d")
# transcription_folder=os.getenv("TRANSCRIPTIONFOLDER", "transcribed")
∂
feeds = load_json("content_monitor.json")
episodes = monitor_podcast(feeds, cutoff_date)

persist_episodes_to_be_processed(episodes, "to_be_processed.json")
# transcribe_podcasts("to_be_processed.json", transcription_folder)
transcribe_podcasts("to_be_processed.json")

# summerize_podcasts("transcribed", "podcast_summary")
summerize_podcasts("transcriptions", "podcast_summary")
send_mail(summary_text("podcast_summary"))
