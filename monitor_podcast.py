import feedparser
import time
from pprint import pprint
from datetime import date, datetime
import pytz
import json
from util import *
import prettyprint 

class Episode:
  def __init__(self, name, podcast_name, episode_link, link, pub_time):
    self.name = name
    self.podcast_name = podcast_name
    self.episode_link = episode_link
    self.link = link
    self.pub_time = pub_time
  def __eq__(self, other):
        if isinstance(other, Episode):
            return self.name == other.name and self.podcast_name == podcast_name and self.episode_link and  self.link  == other.link and self.pub_time  == other.pub_time
        return False
  def __hash__(self):
      return hash((self.name, self.podcast_name, self.link, self.pub_time))
  def to_dict(self):
    return {"name": self.name, "podcast_name": self.podcast_name, "episode_link": self.episode_link, "link": self.link, "pub_time": self.pub_time}

def add_to_array_if_not_exists(obj, arr):
    if obj not in arr:
        arr.append(obj)
        print (f"added {obj.episode_link}")

def monitor_podcast(feed_url, cutoff_date, interval=30):
  """
  Monitors a podcast RSS feed for new episodes.

  Args:
    feed_url: The URL of the podcast RSS feed.
    interval: The time interval (in seconds) between checks.
  """
  date_format = "%a, %d %b %Y %H:%M:%S %z"
  cutoff_date = cutoff_date.replace(tzinfo=pytz.timezone('US/Eastern'))
  last_published = None
  episodes = []
  # while True:
  print (f"** processing {len(feed_url)} feeds")
  for channel in feed_url:
    print (channel["name"])
    try:
      feed = feedparser.parse(channel["FeedLink"])
      
    except Exception as e:
      print(f"Error fetching feed: {e}")
      time.sleep(interval)
      continue

    if not feed.entries:
      print("No episodes found in feed.")
      time.sleep(interval)
      continue
    for f in feed.entries:
      if str_to_datetime(f.published) > cutoff_date:
        # f_published_dt = datetime.strptime(f.published, date_format)
        # pub_date_est =  f_published_dt.replace(tzinfo=pytz.timezone('US/Eastern'))
        # print(f"Episode Name: {f.title }.\n Published: {pub_date_est} \n")
        episode_link = ""
        audio_link=""
        for link in f.links:
          if link.type == "text/html":
             episode_link=link.href
          if link.type == "audio/mpeg":
            audio_link = link.href
        if episode_link=="":
           episode_link = audio_link
        episode_obj = Episode(f.title, channel["name"], episode_link, audio_link,f.published)
        add_to_array_if_not_exists(episode_obj, episodes)
            # add_if_not_exists_multi(episodes,episode_obj, )

  data = [obj.to_dict() for obj in episodes]
  return data
  # time.sleep(interval)


def persist_episodes_to_be_processed(episodes, filepath):
  
 # Write data to JSON file
  with open(filepath, 'w') as outfile:
      json.dump(episodes, outfile, indent=4) 
  print (f"Successfully written {len(episodes)} records")

# if __name__ == "__main__":
#   feed_url = "YOUR_PODCAST_RSS_FEED_URL" 
#   monitor_podcast(feed_url)