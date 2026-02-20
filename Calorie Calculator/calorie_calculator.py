import requests
import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT_VISION = os.getenv("ENDPOINT_VISION")
APIKEY_VISION = os.getenv("APIKEY_VISION")
ENDPOINT_OPENAI = os.getenv("ENDPOINT_OPENAI")
APIKEY_OPENAI = os.getenv("APIKEY_OPENAI")
DEPLOYMENT = "gpt-4o"

IMAGE_PATH = "images/foto6.jpg"  # Change the image path


url = f"{ENDPOINT_VISION}/computervision/imageanalysis:analyze?api-version=2024-02-01"

headers = {
    "Ocp-Apim-Subscription-Key": APIKEY_VISION,
    "Content-Type": "application/octet-stream"
}

params = {
    "features": "caption,objects,tags,denseCaptions",
    "language": "en"
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

# Show Computer Vision Results
print("\n=== ANALYSIS RESULTS ===\n")

# CAPTION
if "captionResult" in result:
    print("📝 CAPTION:")
    print(f"   {result['captionResult']['text']}")
    print(f"   (confidence: {result['captionResult']['confidence']:.2f})")

caption = result["captionResult"]["text"]

# DENSE CAPTIONS
if "denseCaptionsResult" in result and "values" in result["denseCaptionsResult"]:
    print("\n📑 DENSE CAPTIONS (descripciones detalladas):")
    dense_captions = result["denseCaptionsResult"]["values"]
    if dense_captions:
        for i, dense_caption in enumerate(dense_captions, 1):
            print(f"\n   {i}. {dense_caption['text']}")
            print(f"      Confidence: {dense_caption['confidence']:.2f}")
    else:
        print("   No dense captions detected")

dense = []
for item in result["denseCaptionsResult"]["values"]:
    if item["confidence"] > 0.8:
        dense.append(item["text"])


prompt = f"""
You are a nutrition assistant.

Based on the following image analysis results, identify the ingredients and estimate quantities.

Main description:
{caption}

Detailed detections:
{chr(10).join("- " + d for d in dense)}

Return ONLY valid JSON:
{{
  "ingredients": [
    {{
      "name": "",
      "quantity": "",
      "unit": ""
    }}
  ]
}}
"""

url = f"{ENDPOINT_OPENAI}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview"

headers = {
    "Content-Type": "application/json",
    "api-key": APIKEY_OPENAI
}

data = {
    "messages": [
        {"role": "system", "content": "You are a helpful AI."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.2
}

response = requests.post(url, headers=headers, json=data)
result_gpt = response.json()

# Show OpenAI results

print("\n=== OpenAI RESULTS ===\n")
print(result_gpt["choices"][0]["message"]["content"])


