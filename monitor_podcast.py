import feedparser
import time
from pprint import pprint
from datetime import date, datetime
import pytz
import json
from util import *
import prettyprint 

class Episode:
  def __init__(self, name, podcast_name, episode_link, link, pub_time, duration):
    self.name = name
    self.podcast_name = podcast_name
    self.episode_link = episode_link
    self.link = link
    self.pub_time = pub_time
    self.duration = duration
  
  def __eq__(self, other):
        if isinstance(other, Episode):
            # return self.name == other.name and self.podcast_name == other.podcast_name and self.episode_link and  self.link  == other.link and self.pub_time  == other.pub_time and self.duration == other.duration
            return (self.name == other.name and 
                    self.podcast_name == other.podcast_name and 
                    self.episode_link == other.episode_link and  
                    self.link == other.link and 
                    self.pub_time == other.pub_time and 
                    self.duration == other.duration)
        return False
  def __hash__(self):
      return hash((self.name, self.podcast_name, self.link, self.pub_time, self.duration))
  def to_dict(self):
    return {"name": self.name, "podcast_name": self.podcast_name, "episode_link": self.episode_link, "link": self.link, "pub_time": self.pub_time, "duration": self.duration}

def add_to_array_if_not_exists(obj, arr):
    if obj not in arr:
        arr.append(obj)
        # print (f"added {obj.duration}")
def populate_episode(f, channel_name):
   # get only cut the clutter
    episode_link = ""
    audio_link=""
    duration = ""

    for link in f.links:
      if link.type == "text/html":
        episode_link=link.href
      if link.type == "audio/mpeg":
        audio_link = link.href
    if episode_link=="":
      episode_link = audio_link
    duration = f.get('itunes_duration', 'Duration not available')
    # print(f"duration - {duration}")
    episode_obj = Episode(f.title, channel_name, episode_link, audio_link,f.published, duration)
    return episode_obj
   
def monitor_podcast(feed_url, cutoff_date, interval=30):
  """
  Monitors a podcast RSS feed for new episodes.

  Args:
    feed_url: The URL of the podcast RSS feed.
    interval: The time interval (in seconds) between checks.
  """
  # date_format = "%a, %d %b %Y %H:%M:%S %z"
  cutoff_date = cutoff_date.replace(tzinfo=pytz.timezone('US/Eastern'))
  log("debug", f"monitor-feed::cutoff-date - {cutoff_date}")
  # last_published = None
  episodes = []
  # while True:
  for channel in feed_url:
    log("debug", f"monitor-feed::podcast name - {channel["name"]}")   
    try:
      feed = feedparser.parse(channel["FeedLink"])
    except Exception as e:
      log("error", f"monitor-feed:: error reaching {channel["FeedLink"]}... retrying")
      time.sleep(interval)
      continue

    if not feed.entries:
      log("info", f"monitor-feed::no new episode found in - {channel["name"]}")
      time.sleep(interval)
      continue
    for f in feed.entries:
      if str_to_datetime(f.published) > cutoff_date:
        # check if it's cut the clutter
        if channel["name"] == "The Print - Cut the Clutter":
           if "CutTheCLutter:" in f.title:
            episode_obj = populate_episode(f, channel["name"])
            # add_to_array_if_not_exists(episode_obj, episodes)
        else:
          episode_obj = populate_episode(f, channel["name"])
      add_to_array_if_not_exists(episode_obj, episodes)
                   # add_if_not_exists_multi(episodes,episode_obj, )

  data = [obj.to_dict() for obj in episodes]
  log("debug", f"monitor-feed:episodes to be transcribed  - {json.dumps(data)}")
  return data
  # time.sleep(interval)


def persist_episodes_to_be_processed(episodes, filepath):
  # pprint(f"episode 0 - {json.dumps(episodes[0])}")
 # Write data to JSON file
  with open(filepath, 'w') as outfile:
      json.dump(episodes, outfile, indent=4) 
  log("info", f"monitor-feed:persisted list  - {len(episodes)} records")
  print (f"Successfully written {len(episodes)} records")

# if __name__ == "__main__":
#   feed_url = "YOUR_PODCAST_RSS_FEED_URL" 
#   monitor_podcast(feed_url)