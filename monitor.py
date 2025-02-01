
from monitor_podcast import *
from util import *
from transcribe import *
from summarizer import *

# from util_logging import  S3LogHandler
# from util_logging import *

log("info", "Starting process")
# logger = setup_logger()
# logger.info("Starting data processing")
from dotenv import load_dotenv
load_dotenv()
cutoff_date = str_to_datetime( os.getenv('CUTOFFDATE', '2025/1/3'), "%Y/%m/%d")
# transcription_folder=os.getenv("TRANSCRIPTIONFOLDER", "transcribed")
log("info", f"Cutoff Date = {cutoff_date}")
log("info", f"content config location - content_monitor.json ")
feeds = load_json("content_monitor.json")
episodes = monitor_podcast(feeds, cutoff_date)
log("info", f"Number of new episodes - {len(episodes)}")
persist_episodes_to_be_processed(episodes, "to_be_processed.json")
# log("info", f"New episode links persisted at to_be_processed.json")
# log("info", f"***** Starting transcription *****")
# transcribe_podcasts("to_be_processed.json")
# log("info", f"***** Starting Summarization *****")
# summerize_podcasts("transcriptions", "podcast_summary")
# log("info", f"***** Sending Email *****")
# send_mail(summary_text("podcast_summary"))
