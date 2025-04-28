import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import pandas as pd

class GPT:
    def __init__(self, api_key):
        url = 'https://app.gpt-trainer.com/api/v1/chatbot/create'
        self.url = url
        self.sessionuuid = None
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
        data = {
            "url": url_string
        }

        response = requests.post(urln, headers=self.headers, json=data)

        if response.status_code == 200:
            print("Request successful!")
            print(response.json())
            source_uuid = response.json().get('uuid')
            print(source_uuid)
            return source_uuid
        else:
            print("Request failed with status code:", response.status_code)
            print(response.text)
            return None

    def Update_Source(self, uuids):
        url = 'https://app.gpt-trainer.com/api/v1/data-sources/url/re-scrape'
        data = {
            "uuids": uuids
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            print("Request successful!")
            print(response.json())
        else:
            print("Request failed with status code:", response.status_code)
            print(response.text)

    def Delete_Source(self, uuid):
        url = f'https://app.gpt-trainer.com/api/v1/data-source/{uuid}/delete'

        response = requests.post(url, headers=self.headers)

        if response.status_code == 200:
            print("Request successful!")
            print(response.json())
        else:
            print("Request failed with status code:", response.status_code)
            print(response.text)

    def URL(self, chatbotuuid, url_list, prompts, csv_headers):
        csv_file = "output.csv"
        urluuid = [["" for _ in row] for row in url_list]

        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["URL"] + csv_headers)

        for idx, row in enumerate(url_list):
            print(f"Processing row {idx + 1}...")

            for idy, single_url in enumerate(row):
                self.create_sessionuuid(chatbotuuid)

                uuid = self.Add_Source(chatbotuuid, single_url)
                if not uuid:
                    print(f"Failed to add source for URL: {single_url}")
                    continue
                urluuid[idx][idy] = uuid

            time.sleep(10)

            try:
                prompt = prompts[0] if len(prompts) == 1 else prompts[idx]
                message_data = {"query": prompt}

                response = self.create_message(message_data)
                if response:
                    lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
                    while len(lines) < len(csv_headers):
                        lines.append("")
                    extracted_data = lines[:len(csv_headers)]

                    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
                        writer = csv.writer(file)
                        writer.writerow([", ".join(row)] + extracted_data)
                else:
                    print(f"Failed to create message for row {idx + 1}")
                    continue

            except Exception as e:
                print(f"Error processing response for row {idx + 1}: {e}")

            time.sleep(10)

            try:
                for idy, uuid in enumerate(urluuid[idx]):
                    if uuid: 
                        self.Delete_Source(uuid)
                        print(f"Source with UUID {uuid} deleted successfully.")
            except Exception as e:
                print(f"Error deleting sources for row {idx + 1}: {e}")

        # Generate Markdown table from the CSV file
        df = pd.read_csv(csv_file)
        markdown_table = df.to_markdown(index=False, numalign="left", stralign="left")
        print(markdown_table)

        # Save the Markdown table to a file
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(markdown_table)
        print("Markdown table saved to output.md")


api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MTIyNDg2NSwianRpIjoiMmVlZmJjNDctZjhkMS00YTg5LThlYWMtYzlhNTI0ZDE4ZDEwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJhcGlfa2V5IjoiYjk1YTEzZjE1ODgzYzRjMThiOGFlZDEyOThlNGEzZmMzMDk4Mjk0N2YyZTY4Nzg4MzZmYzU5ZmMyYzM4NTg2ZCJ9LCJuYmYiOjE3NDEyMjQ4NjV9.b3TiSWOufZZ8rOHQjey7_0n5B022fijBykATLXWdhQI'
gpt = GPT(api_key)
 
chatbot_data = {
     "name": "URL Simplifier",
     "rate_limit": [20, 240],
     "rate_limit_message": "Too many messages",
     "show_citations": False,
     "visibility": "public"
 }
 
chatbotuuid="140b54b76e594762abb4c9f7985d826d"
gpt.create_sessionuuid(chatbotuuid)

prompts = [
    "Name, School, Department, Email, Research interests, Bio, Other links, all in different columns",
]
url=[]
url.append(['https://finance.wharton.upenn.edu/~itayg/', 'https://adamgrant.net/', 'https://leadership.wharton.upenn.edu/mike-useem/'])
url.append(['https://jonahberger.com/'])
url.append(['https://www.collegeessayguy.com/blog/upenn-university-pennsylvania-supplemental-essay','https://www.upenn.edu/about/university-values'])

csv_headers = ["Name", "School", "Department", "Email", "Research interests", "Bio", "Other links"]
gpt.URL(chatbotuuid, url, prompts, csv_headers)