import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

ENDPOINT_VISION = os.getenv("ENDPOINT_VISION")
APIKEY_VISION = os.getenv("APIKEY_VISION")
ENDPOINT_OPENAI = os.getenv("ENDPOINT_OPENAI")
APIKEY_OPENAI = os.getenv("APIKEY_OPENAI")
APIKEY_USDA = os.getenv("APIKEY_USDA")
DEPLOYMENT = "gpt-4o"


# ==============================
# USDA FUNCTIONS
# ==============================

def search_food(name):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        "query": name,
        "api_key": APIKEY_USDA,
        "pageSize": 1
    }

    res = requests.get(url, params=params)
    data = res.json()

    if data["foods"]:
        return data["foods"][0]["fdcId"]

    return None


def get_macros(fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"

    params = {"api_key": APIKEY_USDA}

    res = requests.get(url, params=params)
    data = res.json()

    nutrients = data["foodNutrients"]

    macros = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }

    for n in nutrients:
        if n["nutrient"]["id"] == 1008:
            macros["calories"] = n["amount"]
        elif n["nutrient"]["id"] == 1003:
            macros["protein"] = n["amount"]
        elif n["nutrient"]["id"] == 1005:
            macros["carbs"] = n["amount"]
        elif n["nutrient"]["id"] == 1004:
            macros["fat"] = n["amount"]

    return macros


# ==============================
# MAIN PIPELINE FUNCTION
# ==============================

def analyze_image_macros(image_bytes):

    # ---------- Computer Vision ----------

    url = f"{ENDPOINT_VISION}/computervision/imageanalysis:analyze?api-version=2024-02-01"

    headers = {
        "Ocp-Apim-Subscription-Key": APIKEY_VISION,
        "Content-Type": "application/octet-stream"
    }

    params = {
        "features": "caption,objects,tags,denseCaptions",
        "language": "en"
    }

    response = requests.post(
        url,
        params=params,
        headers=headers,
        data=image_bytes
    )

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        exit()

    result = response.json()

    caption = result["captionResult"]["text"]

    dense = [
        item["text"]
        for item in result["denseCaptionsResult"]["values"]
        if item["confidence"] > 0.8
    ]

    # ---------- GPT ----------

    prompt = f"""
    You are a nutrition AI assistant.

    Based on the image analysis, identify the ingredients.

    IMPORTANT RULES:

    - Return ONLY ingredients that can be searched in the USDA FoodData API.
    - Convert ALL quantities to grams.
    - Use simple standardized food names (example: "white rice cooked", "egg whole raw", "salmon raw").
    - Do NOT use units like cups, slices, or pieces.
    - If unsure about quantity, estimate reasonably.

    Main description:
    {caption}

    Detailed detections:
    {chr(10).join("- " + d for d in dense)}

    Return ONLY valid JSON:
    {{"ingredients": [{{"name": "string", "grams": number}}]}}
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
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=data)
    result_gpt = response.json()

    ingredients_json = result_gpt["choices"][0]["message"]["content"]
    ingredients_data = json.loads(ingredients_json)
    ingredients = ingredients_data["ingredients"]

    # ---------- USDA ----------

    total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    for ing in ingredients:
        fdc_id = search_food(ing["name"])
        if not fdc_id:
            continue

        macros = get_macros(fdc_id)
        factor = ing["grams"] / 100

        total["calories"] += macros["calories"] * factor
        total["protein"] += macros["protein"] * factor
        total["carbs"] += macros["carbs"] * factor
        total["fat"] += macros["fat"] * factor

    return {
        "caption": caption,
        "ingredients": ingredients,
        "calories": total["calories"],
        "protein": total["protein"],
        "carbs": total["carbs"],
        "fat": total["fat"]
    }
