# import torch, whisper
import json
import os
import re
from typing import List, Dict, Optional 
from string import Template
from bs4 import BeautifulSoup
import markdown
import commonmark
from markdownify import markdownify
from dotenv import load_dotenv
load_dotenv()

# import yt_dlp
import sys
from datetime import datetime
from datetime import date, datetime
from email_client import MailjetClient
from s3Connect import S3Uploader


def generate_python_friendly_filename(input_string):
  """
  Generates a Python-friendly filename from a given string.

  Args:
    input_string: The input string to be converted.

  Returns:
    A Python-friendly filename string.
  """

  # 1. Remove invalid characters
  filename = re.sub(r'[\\/:"*?<>|]', '', input_string)  # Remove invalid characters

  # 2. Replace spaces and other whitespace with underscores
  filename = filename.replace(" ", "_") 

  # 3. Convert to lowercase (optional)
  filename = filename.lower()

  # 4. Limit filename length (optional)
  max_length = 255  # Adjust as needed
  filename = filename[:max_length] 

  return filename
def strip_extension(filename):
    """
    Strips the extension from a filename.
    
    Args:
    filename (str): The filename including the extension.
    
    Returns:
    str: The filename without the extension.
    """
    return os.path.splitext(filename)[0]
def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data
def check_file(file_name):
    if not os.path.exists(file_name):
        return False
    else: 
        return True
def strip_before_last_slash(string):
    return string.rsplit('/', 1)[-1]
def create_file(filename, content):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:   # Opens file and casts as f 
        f.write(content )       # Writing
def get_now() ->str:
  now = datetime.now()
  formatted_date = now.strftime("%m-%d-%Y")
  return formatted_date

   
def my_hook(d):
    if d['status'] == 'downloading':
        print ("###### downloading "+ str(round(float(d['downloaded_bytes'])/float(d['total_bytes'])*100,1))+"%")
    if d['status'] == 'finished':
        filename=d['###### filename']
        print(filename)

def str_to_datetime(date_string, input_type="%a, %d %b %Y %H:%M:%S %z" ):
  """
  Converts a string in the format "Mon, 30 Dec 2024 02:04:44 -0000" 
  to a Python datetime object.

  Args:
    date_string: The string representing the date and time.

  Returns:
    A datetime object representing the date and time, 
    or None if the string cannot be parsed.
  TODO:
    Add another arg to take input of date type to expect - regular expression
  """
  try:
    # return datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
    return datetime.strptime(date_string, input_type)
  except ValueError:
    print(f"Invalid date/time format: {date_string}")
    return None
def check_folder_exists(folder_path):
  """
  Checks if a folder exists at the given path.

  Args:
    folder_path: The path to the folder.

  Returns:
    True if the folder exists, False otherwise.
  """
  return os.path.isdir(folder_path)

def stop_program_if_condition(condition):
  """
  Stops program execution if the given condition is True.

  Args:
    condition: The boolean condition to evaluate.
  """
  if condition:
    sys.exit(0)  # Exit the program with a success code (0)

def get_subfolders(root_dir):
  """
  Gets a list of all subfolders within the specified root directory.

  Args:
    root_dir: The path to the root directory.

  Returns:
    A list of subfolder paths.
  """
  subfolders = []
  for dirpath, dirnames, filenames in os.walk(root_dir):
    for dirname in dirnames:
      # subfolders.append(os.path.join(dirpath, dirname))
      subfolders.append(dirname)
  return subfolders
def join_path_with_subfolders(*args):
  """
  Joins path components, including subfolders, 
  and returns the full path.

  Args:
    *args: One or more path components to join.

  Returns:
    The joined path string.
  """
  return os.path.join(*args)

def send_mail(content):
  api_key = os.getenv("MJ_APIKEY_PUBLIC")
  api_secret =os.getenv("MJ_APIKEY_PRIVATE")
  # try:
  mailjet = MailjetClient(api_key, api_secret)
  now = datetime.now()
  # formatted_date = now.strftime("%m-%d-%y")
  formatted_date = now.strftime("%B %d %A %Y")
  dynamic_content = {
      "date_string": formatted_date,
      "content_html": content
  }
  
  # Send an email
  response = mailjet.send_email(
      from_email="recommendation@rahulguha.com",
      from_name="New Podcast Newsletter",
      to_email="rahul.guha@gmail.com",
      to_name="Rahul Guha",
      subject=f"New Podcast List as of {formatted_date} ",
      text_content=content,
      variables=dynamic_content,
      html_content=None
  )
  
  return response  
  # except:
  #   print ("error sending email")

def create_s3_file(filename, content, prefix):
  formatted_date = get_now()
  uploader = S3Uploader(
    bucket_name=get_bucket_name(),
    prefix=f"{prefix}/{formatted_date}"  # All files will be uploaded under this prefix
  )
  uploader.upload_string(
        content=content,
        key=filename  # Will be uploaded as "data/2024/hello.txt"
    ) 
def list_s3_files(
  bucket_name: str,
  prefix: str = "",
  suffix: str = None,
  max_files: int = None
  ) -> List[Dict]:
    """
    List files in an S3 bucket under a specific prefix (folder)
    
    Args:
        bucket_name (str): Name of the S3 bucket
        prefix (str): Folder path in S3 (optional)
        suffix (str): Filter files by extension (e.g., '.csv', '.txt')
        max_files (int): Maximum number of files to return (optional)
    
    Returns:
        List[Dict]: List of dictionaries containing file information
    """
    now = datetime.now()
    formatted_date = now.strftime("%m-%d-%y")
    
    uploader = S3Uploader(
      bucket_name=bucket_name,
      prefix=f"{prefix}/{formatted_date}"  # All files will be uploaded under this prefix
    )
    
    return uploader.list_files_by_bucket(bucket_name, prefix)
def get_bucket_name() ->str:
   return os.getenv("S3_BUCKET")
def read_s3_file(  key) ->str:
  formatted_date = get_now()  

  uploader = S3Uploader(
      bucket_name=get_bucket_name(),
      prefix=""  # All files will be uploaded under this prefix
    )
  return uploader.read_s3_file(key)


def summary_to_html(podcast_name="", episode_name="", episode_link="", sum_text=""):
  
  sum_text = convert_markdown_to_html(sum_text)
  # Sample JSON data
  data = {
      "podcast_name": podcast_name,
      "episode_name": episode_name,
      "episode_link": episode_link,
      "sum_text": sum_text
  }

  # HTML Template as string with placeholders
  html_template = """
      <h2>${podcast_name}</h2>
      <h3>${episode_name}</h3>
      <div><a href=${episode_link}> Open Episode</a></div>
      <br/>
      <div>${sum_text}</div>
  """

  # Create a Template object
  template = Template(html_template)

  # Replace placeholders with actual data from JSON
  html_output = template.safe_substitute(data)
  html_output = prettify_html(html_output)

  return(html_output)


def prettify_html(html_text: str) -> str:
    """
    Format HTML to be more readable
    """
    try:
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.prettify()
    except Exception as e:
        print(f"Error prettifying HTML: {e}")
        return html_text

def convert_markdown_to_html(markdown_text: str, method: str = 'python-markdown') -> str:
    """
    Convert Markdown to HTML using different methods
    
    Args:
        markdown_text (str): The markdown text to convert
        method (str): Conversion method ('python-markdown', 'commonmark', or 'custom')
    
    Returns:
        str: The converted HTML
    """
    try:
        if method == 'python-markdown':
            # Using python-markdown (more features)
            return markdown.markdown(
                markdown_text,
                extensions=['tables', 'fenced_code', 'codehilite', 'toc']
            )
            
        elif method == 'commonmark':
            # Using commonmark (strictly follows CommonMark spec)
            parser = commonmark.Parser()
            renderer = commonmark.HtmlRenderer()
            ast = parser.parse(markdown_text)
            return renderer.render(ast)
            
        elif method == 'custom':
            # Basic custom conversion (example for simple cases)
            lines = markdown_text.split('\n')
            html_lines = []
            
            for line in lines:
                # Headers
                if line.startswith('# '):
                    html_lines.append(f'<h1>{line[2:]}</h1>')
                elif line.startswith('## '):
                    html_lines.append(f'<h2>{line[3:]}</h2>')
                # Bold
                elif '**' in line:
                    line = line.replace('**', '<strong>', 1)
                    line = line.replace('**', '</strong>', 1)
                    html_lines.append(f'<p>{line}</p>')
                # Regular paragraph
                elif line.strip():
                    html_lines.append(f'<p>{line}</p>')
                else:
                    html_lines.append('<br>')
                    
            return '\n'.join(html_lines)
        
        else:
            raise ValueError(f"Unsupported method: {method}")
            
    except Exception as e:
        print(f"Error converting markdown to HTML: {e}")
        return ""