import os, json
from dotenv import load_dotenv
# from clsemail import *
load_dotenv()
import requests


class MailjetClient:
    def __init__(self, api_key, api_secret):
        self.auth = (api_key, api_secret)
        self.base_url = "https://api.mailjet.com/v3.1"  # Note: changed to v3.1

    def send_email(self, from_email, from_name, to_email,  subject, text_content,variables, html_content=None):
        endpoint = f"{self.base_url}/send"
        
        data = {
            "Messages": [{
                "From": {
                    "Email": from_email,
                    "Name": from_name
                },
                # "To": [{
                #     "Email": ["rahul.guha@fmr.com","rahul.guha@gmail.com", "nguha14@gmail.com"],
                #     "Name": ["Rahul Guha FMR", "Rahul Gmail", "Runa"]
                # }],
                "To": to_email,
                "Bcc": [{"EMail": "rahul.guha.us@gmail.com", "Name": "Rahul GMAIL US"}],
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
            
            # if response.status_code == 200:
            #     return response.json()
            # else:
            #     return {
            #         "error": True,
            #         "status_code": response.status_code,
            #         "response_text": response.text
            #     }
            if response.status_code in [200, 202]:  # 202 = Accepted, 200 = Success
                print("✅ Email sent successfully!")
                print("Response:", response.json())
                return response.json()
            else:
                print(f"⚠️ Failed to send email. Status Code: {response.status_code}")
                print("Response:", response.json())
                

        except requests.exceptions.HTTPError as http_err:
            print(f"❌ HTTP error occurred: {http_err}")  # Handles 400/500 errors
        except requests.exceptions.ConnectionError as conn_err:
            print(f"❌ Connection error occurred: {conn_err}")  # Handles network issues
        except requests.exceptions.Timeout as timeout_err:
            print(f"❌ Timeout error occurred: {timeout_err}")  # Handles request timeouts
        except requests.exceptions.RequestException as req_err:
            print(f"❌ General request error: {req_err}")  # Handles other request-related issues
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")  # Catches all unexpected errors
        finally:
            return response.json()
            # except Exception as e:
            #     print(f"Exception occurred: {str(e)}")
            #     return {
            #         "error": True,
            #         "exception": str(e)
            #     }


