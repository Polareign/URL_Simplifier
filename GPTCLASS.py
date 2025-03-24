import requests
from bs4 import BeautifulSoup
import json

class GPT:
    def __init__(self, api_key):
        url='https://app.gpt-trainer.com/api/v1/chatbot/create'
        self.url = url
        sessionuuid=None
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        self.uuid = None

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

    def create_agent(self, agent_data):
        if not self.uuid:
            print("UUID not found. Create the chatbot first.")
            return

        otherurl = f'https://app.gpt-trainer.com/api/v1/chatbot/{self.uuid}/agent/create'
        response = requests.post(otherurl, headers=self.headers, json=agent_data)
        if response.status_code == 200:
            print("Agent creation successful!")
            print(response.json())
        else:
            print("Agent creation failed with status code:", response.status_code)
            print(response.text)
    def create_session(self):
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

    def create_sessionuuid(self, uuid):
        self.uuid=uuid
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

def URL_SCRAPING(urll):
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



api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MTIyNDg2NSwianRpIjoiMmVlZmJjNDctZjhkMS00YTg5LThlYWMtYzlhNTI0ZDE4ZDEwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJhcGlfa2V5IjoiYjk1YTEzZjE1ODgzYzRjMThiOGFlZDEyOThlNGEzZmMzMDk4Mjk0N2YyZTY4Nzg4MzZmYzU5ZmMyYzM4NTg2ZCJ9LCJuYmYiOjE3NDEyMjQ4NjV9.b3TiSWOufZZ8rOHQjey7_0n5B022fijBykATLXWdhQI'
gpt = GPT(api_key)

chatbot_data = {
    "name": "URL Simplifier",
    "rate_limit": [20, 240],
    "rate_limit_message": "Too many messages",
    "show_citations": False,
    "visibility": "public"
}

# gpt.create_chatbot(chatbot_data)
otheruuid='140b54b76e594762abb4c9f7985d826d'
gpt.create_sessionuuid(otheruuid)
# gpt.create_session()

url = 'https://www.vice.com/en/article/how-to-cook-bugs-ants/'
info=URL_SCRAPING(url)
prompt_test="Make a cooking recipe"
message_data = {
    "query": f"{prompt_test}. Please simplify the information from this json file: {info}"
}
gpt.create_message(message_data)

# urll='https://www.healthline.com/health/how-to-be-happy'
# infoo=URL_SCRAPING(urll)
# message_dataa = {
#     "query": f"Please simplify the information from this json file: {infoo}"
# }
# gpt.create_message(message_dataa)

# urlll='https://www.thegoodtrade.com/features/summer-activities/'
# infooo=URL_SCRAPING(urlll)
# message_dataaa = {
#     "query": f"Please simplify the information from this json file: {infooo}"
# }
# gpt.create_message(message_dataaa)

# message_test ={
#     "query": f"Create a web scraper using Python and the Beautiful Soup library"
# }
# gpt.create_message(message_test)
