import requests
import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("ENDPOINT")
KEY = os.getenv("API_KEY")

IMAGE_PATH = "images/foto2.jpeg"  # Change the image path


url = f"{ENDPOINT}/computervision/imageanalysis:analyze"

params = {
    "api-version": "2023-10-01",
    "features": "objects,denseCaptions",  # Using object detection and dense captions
    "language": "en"
}

headers = {
    "Ocp-Apim-Subscription-Key": KEY,
    "Content-Type": "application/octet-stream"
}

with open(IMAGE_PATH, "rb") as image_file:
    image_data = image_file.read()

response = requests.post(
    url,
    params=params,
    headers=headers,
    data=image_data
)

if response.status_code != 200:
    print("Error:", response.status_code, response.text)
    exit()

result = response.json()

print("\n OBJECT DETECTION:")
for obj in result.get("objectsResult", {}).get("values", []):
    print(f"- {obj['tags'][0]['name']} ({obj['tags'][0]['confidence']:.2f})")

print("\n DENSE CAPTIONS:")
for caption in result.get("denseCaptionsResult", {}).get("values", []):
    print(f"- {caption['text']} ({caption['confidence']:.2f})")
