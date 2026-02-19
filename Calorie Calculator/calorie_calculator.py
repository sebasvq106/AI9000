import requests
import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT_VISION = os.getenv("ENDPOINT_VISION")
APIKEY_VISION = os.getenv("APIKEY_VISION")

IMAGE_PATH = "images/foto2.jpg"  # Change the image path


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

# Show Results
print("\n=== ANALYSIS RESULTS ===\n")

# CAPTION
if "captionResult" in result:
    print("📝 CAPTION:")
    print(f"   {result['captionResult']['text']}")
    print(f"   (confidence: {result['captionResult']['confidence']:.2f})")

# OBJECTS
if "objectsResult" in result and "values" in result["objectsResult"]:
    print("\n🔍 OBJECTS DETECTED:")
    objects = result["objectsResult"]["values"]
    if objects:
        for i, obj in enumerate(objects, 1):
            if 'tags' in obj and obj['tags']:
                main_tag = obj['tags'][0]
                print(f"   {i}. {main_tag['name']} (confidence: {main_tag['confidence']:.2f})")     
    else:
        print("   No objects detected")

# TAGS
if "tagsResult" in result and "values" in result["tagsResult"]:
    print("\n🏷️ TAGS:")
    tags = result["tagsResult"]["values"]
    if tags:
        relevant_tags = [tag for tag in tags if tag['confidence'] > 0.5]
        for tag in relevant_tags[:10]:
            print(f"   - {tag['name']} (confidence: {tag['confidence']:.2f})")
    else:
        print("   No tags detected")

# DENSE CAPTIONS
if "denseCaptionsResult" in result and "values" in result["denseCaptionsResult"]:
    print("\n📑 DENSE CAPTIONS (descripciones detalladas):")
    dense_captions = result["denseCaptionsResult"]["values"]
    if dense_captions:
        for i, caption in enumerate(dense_captions, 1):
            print(f"\n   {i}. {caption['text']}")
            print(f"      Confidence: {caption['confidence']:.2f}")
    else:
        print("   No dense captions detected")
