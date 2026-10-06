import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Testing /api/status/ ...")
    try:
        res = requests.get(f"{BASE_URL}/api/status/")
        print("Status Code:", res.status_code)
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print("Error testing /api/status/:", e)

    print("\nTesting /api/recommend/ ...")
    payload = {"tender_text": "Supply of thermo-mechanically treated steel rods for bridges"}
    try:
        res = requests.post(f"{BASE_URL}/api/recommend/", json=payload)
        print("Status Code:", res.status_code)
        data = res.json()
        print(f"Model: {data.get('model')}")
        print(f"Inference Time: {data.get('inference_time_ms')} ms")
        print(f"DynamoDB Logged: {data.get('aws_dynamodb_logged')}")
        print(f"Results Count: {len(data.get('recommendations', []))}")
        if data.get('recommendations'):
            print("Top recommendation:", data['recommendations'][0]['is_code'], "-", data['recommendations'][0]['title'])
    except Exception as e:
        print("Error testing /api/recommend/:", e)

if __name__ == "__main__":
    test_api()
