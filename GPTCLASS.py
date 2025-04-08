import requests
from bs4 import BeautifulSoup
import json

class GPT:
    def __init__(self, api_key):
        self.url = 'https://app.gpt-trainer.com/api/v1/chatbot/create'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        self.uuid = None
        self.sessionuuid = None

    def create_chatbot(self, data):
        response = requests.post(self.url, headers=self.headers, json=data)
        if response.status_code == 200:
            print("Chatbot creation successful!")
            response_json = response.json()
            self.uuid = response_json.get('uuid')
            print(response_json)
        else:
            print("Chatbot creation failed with status code:", response.status_code)
            print(response.text)

    def create_sessionuuid(self, uuid):
        self.uuid = uuid
        if not self.uuid:
            print("UUID not found. Create the chatbot first.")
            return
        
        sessionurl = f'https://app.gpt-trainer.com/api/v1/chatbot/{self.uuid}/session/create'
        response = requests.post(sessionurl, headers=self.headers)
        if response.status_code == 200:
            print("Session creation successful!")
            response_json = response.json()
            print(response_json)
            self.sessionuuid = response_json.get('uuid')
        else:
            print("Session creation failed with status code:", response.status_code)
            print(response.text)

    def create_message(self, message_data):
        if not self.sessionuuid:
            print("Session UUID not found. Create the session first.")
            return
        
        messageurl = f'https://app.gpt-trainer.com/api/v1/session/{self.sessionuuid}/message/stream'
        response = requests.post(messageurl, headers=self.headers, json=message_data, stream=True)

        if response.status_code == 200:
             for line in response.iter_lines(decode_unicode=True):
                print(line + '\n')
        else:
            print("Error:", response.status_code)

    def URL_SCRAPING(self, urll):
        response = requests.get(urll)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
        
            title = soup.title.string if soup.title else 'No title'
            paragraphs = [p.get_text() for p in soup.find_all('p')]
        
            simplified_info = {
                'title': title,
                'paragraphs': paragraphs
            }
        
            json_data = json.dumps(simplified_info, indent=4)
        
            print(json_data)
            return json_data
        else:
            print(f"Failed to fetch the URL: {response.status_code}")
            return None

    def Add_Source(self, uuid, url_string):
        urln = f'https://app.gpt-trainer.com/api/v1/chatbot/{uuid}/data-source/url'
        data = {
            "url": url_string
        }

        response = requests.post(urln, headers=self.headers, json=data)

        if response.status_code == 200:
            print("Request successful!")
            print(response.json())
            source_uuid = response.json().get('uuid')
            return source_uuid
        else:
            print("Request failed with status code:", response.status_code)
            print(response.text)
            return None

    def Delete_Source(self, uuid):
        url = f'https://app.gpt-trainer.com/api/v1/data-source/{uuid}/delete'
        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            print("Source deletion successful!")
        else:
            print("Source deletion failed with status code:", response.status_code)
            print(response.text)

    def list_sources(self, uuid):
        url = f'https://app.gpt-trainer.com/api/v1/chatbot/{uuid}/data-sources'
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            sources = response.json()
            print("Current sources:", json.dumps(sources, indent=4))
            return sources
        else:
            print("Failed to fetch sources:", response.status_code, response.text)
            return None


api_key = 'your-api-key-here'
gpt = GPT(api_key)

# Define the chatbot data and create the chatbot
chatbot_data = {
    "name": "URL Simplifier",
    "rate_limit": [20, 240],
    "rate_limit_message": "Too many messages",
    "show_citations": False,
    "visibility": "public"
}

# Create the chatbot (if you haven't already created it before)
# gpt.create_chatbot(chatbot_data)

chatbotuuid = '140b54b76e594762abb4c9f7985d826d'
gpt.create_sessionuuid(chatbotuuid)

# URL to scrape and process
url = 'https://www.vice.com/en/article/how-to-cook-bugs-ants/'
info = gpt.URL_SCRAPING(url)

# Process the scraped data with a query
prompt_test = "Make a cooking recipe"
message_data = {
    "query": f"{prompt_test}. Please simplify the information from this json file: {info}"
}

# Add the URL as a data source
urluuid = gpt.Add_Source(chatbotuuid, url)

# Send the message to the chatbot with the simplified data
gpt.create_message(message_data)

# List sources before and after deletion
print("Before deletion:")
gpt.list_sources(chatbotuuid)

# Delete the source if needed
gpt.Delete_Source(urluuid)

print("After deletion:")
gpt.list_sources(chatbotuuid)