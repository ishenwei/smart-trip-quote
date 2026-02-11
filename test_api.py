import requests
import json

url = 'http://localhost:7000/api/llm/process/'
headers = {'Content-Type': 'application/json'}
data = {
    'user_input': 'test',
    'save_to_db': True
}

response = requests.post(url, headers=headers, json=data)
print(f'Status Code: {response.status_code}')
print(f'Response: {response.text}')
