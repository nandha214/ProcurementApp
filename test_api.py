import requests
import json

url = "http://127.0.0.1:8000/api/recommend/"
payload = {"tender_text": "Supply of thermo-mechanically treated steel rods"}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
