import os, json
from dotenv import load_dotenv
# from clsemail import *
load_dotenv()
import requests


class MailjetClient:
    def __init__(self, api_key, api_secret):
        self.auth = (api_key, api_secret)
        self.base_url = "https://api.mailjet.com/v3.1"  # Note: changed to v3.1

    def send_email(self, from_email, from_name, to_email, to_name, subject, text_content,variables, html_content=None):
        endpoint = f"{self.base_url}/send"
        
        data = {
            "Messages": [{
                "From": {
                    "Email": from_email,
                    "Name": from_name
                },
                "To": [{
                    "Email": to_email,
                    "Name": to_name
                }],
                "TemplateID": 6648977,
                "TemplateLanguage": True,
                "Subject": subject,
                "Variables":variables,
                # "TextPart": text_content,
            }]
        }
        if html_content:
            data["Messages"][0]["HTMLPart"] = html_content
        
        try:
            response = requests.post(
                endpoint, 
                auth=self.auth, 
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "response_text": response.text
                }
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return {
                "error": True,
                "exception": str(e)
            }


