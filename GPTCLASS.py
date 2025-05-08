import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import pandas as pd

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
            return None
        messageurl = f'https://app.gpt-trainer.com/api/v1/session/{self.sessionuuid}/message/stream'
        response = requests.post(messageurl, headers=self.headers, json=message_data, stream=True)
        if response.status_code == 200:
            output_text = ""
            for line in response.iter_lines(decode_unicode=True):
                output_text += line + '\n'
            if output_text.strip():
                return output_text
            else:
                print("Empty response received from the server.")
                return None
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response content: {response.text}")
            return None

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
        data = {"url": url_string}
        response = requests.post(urln, headers=self.headers, json=data)
        if response.status_code == 200:
            print("Add source successful!")
            source_uuid = response.json().get('uuid')
            return source_uuid
        else:
            print("Add source failed:", response.status_code)
            print(response.text)
            return None

    def Delete_Source(self, uuid):
        url = f'https://app.gpt-trainer.com/api/v1/data-source/{uuid}/delete'
        response = requests.post(url, headers=self.headers)
        if response.status_code == 200:
            print(f"Deleted source {uuid}")
        else:
            print("Delete source failed:", response.status_code)
            print(response.text)

    def URL(self, chatbotuuid, url_list, prompts, csv_headers):
        csv_file = "output.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["URL"] + csv_headers)

        for idx, target_url in enumerate(url_list):
            self.create_sessionuuid(chatbotuuid)
            prompt_list = prompts[0] if len(prompts) == 1 else prompts[idx]
            urluuid = self.Add_Source(chatbotuuid, target_url)
            if not urluuid:
                continue
            time.sleep(10)

            responses = []
            for prompt in prompt_list:
                message_data = {"query": prompt}
                try:
                    response = self.create_message(message_data)
                    lines = [line.strip() for line in response.strip().split('\n') if line.strip()] if response else []
                    responses.append(lines[0] if lines else "")
                except Exception as e:
                    print(f"Error during message generation: {e}")
                    responses.append("")

            with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([target_url] + responses)

            time.sleep(10)
            self.Delete_Source(urluuid)

        df = pd.read_csv(csv_file)
        markdown_table = df.to_markdown(index=False, numalign="left", stralign="left")
        print(markdown_table)
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(markdown_table)
        print("Markdown table saved to output.md")

# ==========================
# USAGE EXAMPLE
# ==========================

api_key = 'api_key_here' 
gpt = GPT(api_key)

chatbot_data = {
    "name": "URL Simplifier",
    "rate_limit": [20, 240],
    "rate_limit_message": "Too many messages",
    "show_citations": False,
    "visibility": "public"
}

# gpt.create_chatbot(chatbot_data)
chatbotuuid = "your_chatbot_uuid_here" 

prompts = [
    ["Name", "School", "Department", "Email", "Research interests", "Bio", "Other links"],
    ["Name", "School", "Department", "Email", "Research interests", "Bio", "Other links"],
    ["Name", "School", "Department", "Email", "Research interests", "Bio", "Other links"],
    ["Name", "School", "Department", "Email", "Research interests", "Bio", "Other links"]
]

url_list = [
    "https://finance.wharton.upenn.edu/~itayg/",
    "https://adamgrant.net/",
    "https://leadership.wharton.upenn.edu/mike-useem/",
    "https://jonahberger.com/"
]

csv_headers = ["Name", "School", "Department", "Email", "Research interests", "Bio", "Other links"]

gpt.URL(chatbotuuid, url_list, prompts, csv_headers)