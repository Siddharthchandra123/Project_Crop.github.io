from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from torchvision import transforms
from PIL import Image

from model import ResNet9   # ← YOUR MODEL

app = Flask(__name__)
CORS(app)

# -------- CONFIG --------
IMAGE_SIZE = 256
NUM_CLASSES = 38  # change to your number
CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___healthy',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___healthy',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___healthy',
    'Potato___Late_blight',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___healthy',
    'Strawberry___Leaf_scorch',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___healthy',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
]


# -------- LOAD MODEL --------
device = torch.device("cpu")

model = ResNet9(in_channels=3, num_diseases=NUM_CLASSES)
model.load_state_dict(torch.load(r"C:\Users\Dell\Downloads\project\Project_Crop\back-end\plant_disease_model.pth", map_location=device))
model.eval()

# -------- IMAGE TRANSFORM --------
transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor()
])

# -------- API ENDPOINT --------
@app.route("/predict-disease", methods=["POST"])
def predict_disease():
    try:
        if "image" not in request.files or request.files["image"].filename == "":
            return jsonify({"error": "No image uploaded"}), 400

        image = Image.open(request.files["image"]).convert("RGB")
        image = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(image)
            probs = torch.softmax(outputs, dim=1)
            confidence, pred_index = torch.max(probs, dim=1)

        confidence = confidence.item()
        pred_index = pred_index.item()

        if confidence < 0.6:
            return jsonify({
                "prediction": "Image cannot be recognized",
                "confidence": round(confidence, 3)
            })

        return jsonify({
            "prediction": CLASS_NAMES[pred_index],
            "confidence": round(confidence, 3)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import requests
import numpy as np
import pickle
WEATHER_API_KEY = "dde2b9fb075e41d4b8082159261401"
def get_weather(city):
    url = (
        f"https://api.weatherapi.com/v1/current.json"
        f"?key={WEATHER_API_KEY}&q={city}&aqi=no"
    )

    response = requests.get(url)
    print("WeatherAPI status:", response.status_code)
    print("WeatherAPI response:", response.text)

    if response.status_code != 200:
        raise Exception(response.json().get("error", {}).get("message", "Weather API error"))

    data = response.json()

    temperature = data["current"]["temp_c"]
    humidity = data["current"]["humidity"]
    
    return temperature, humidity

def get_weather_by_coords(lat, lon):
    url = (
        f"https://api.weatherapi.com/v1/current.json"
        f"?key={WEATHER_API_KEY}&q={lat},{lon}&aqi=no"
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(response.json().get("error", {}).get("message"))

    data = response.json()

    weather = {
        "temp_c": data["current"]["temp_c"],
        "humidity": data["current"]["humidity"],
        "wind_kph": data["current"]["wind_kph"],
        "gust_kph": data["current"]["gust_kph"],
        "precip_mm": data["current"]["precip_mm"],
        "condition": data["current"]["condition"]["text"]
    }

    alerts = analyze_weather_alerts(weather)

    return weather, alerts

# -------- LOAD FERTILIZER MODEL --------
with open(r"C:\Users\Dell\Downloads\project\Project_Crop\back-end\fertilizer.pkl", "rb") as f:
    fertilizer_model = pickle.load(f)

@app.route("/predict-fertilizer", methods=["POST"])
def predict_fertilizer():
    try:
        data = request.json

        N = float(data["nitrogen"])
        P = float(data["phosphorus"])
        K = float(data["potassium"])
        lat = float(data["lat"])
        lon = float(data["lon"])

        weather, alerts = get_weather_by_coords(lat, lon)

        temperature = weather["temp_c"]
        humidity = weather["humidity"]
        rainfall = weather["precip_mm"]
        ph = float(data.get("ph", 6.5))

        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        prediction = fertilizer_model.predict(features)[0]

        return jsonify({
            "fertilizer": prediction,
            "weather": {
                "temperature": temperature,
                "humidity": humidity,
                "rainfall": rainfall
            },
            "alerts": alerts
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def analyze_weather_alerts(weather):
    alerts = []

    if weather["wind_kph"] > 35:
        alerts.append("⚠️ High wind alert: Avoid spraying fertilizers or pesticides.")

    if "thunder" in weather["condition"].lower():
        alerts.append("⛈️ Thunderstorm alert: Field work not recommended.")

    if weather["precip_mm"] > 10:
        alerts.append("🌧️ Heavy rain alert: Risk of fertilizer runoff.")

    if weather["temp_c"] > 38:
        alerts.append("🌡️ Heat stress alert: Irrigation recommended.")

    return alerts
# -------- MANDI PRICES ENDPOINT --------

Mandi_API_KEY = "579b464db66ec23bdd000001b9ba6983c18e4a91786d500232dd472d"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

@app.route("/api/mandi-prices")
def mandi_prices():
    state = request.args.get("state", "")
    commodity = request.args.get("commodity", "")

    url = "https://api.data.gov.in/resource/" + RESOURCE_ID

    params = {
        "api-key": Mandi_API_KEY,
        "format": "json",
        "limit": 50,
    }

    if state:
        params["filters[state.keyword]"] = state
    if commodity:
        params["filters[commodity.keyword]"] = commodity

    r = requests.get(url, params=params)
    raw = r.json()

    markets = []
    for rec in raw.get("records", []):
        markets.append({
            "state": rec.get("state"),
            "mandi": rec.get("market"),
            "commodity": rec.get("commodity"),
            "price": int(rec.get("modal_price", 0)),
            "avg7d": int(rec.get("modal_price", 0)),  # can compute later
            "trend": []  # optional (historical fetch)
        })

    return jsonify({
        "lastUpdated": raw.get("updated_date"),
        "markets": markets
    })
from db import get_db, get_all_crops, get_last_crop
@app.route("/api/rotation/add", methods=["POST"])
def add_rotation():
    data = request.json
    db = get_db()          # 🔓 open
    cur = db.cursor()

    cur.execute("""
        INSERT INTO crop_rotation_history
        (land_id, crop_id, season_id, year, sowing_date, harvest_date)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        data["land_id"], data["crop_id"],
        data["season_id"], data["year"],
        data["sowing_date"], data["harvest_date"]
    ))

    db.commit()

    cur.close()            # 🔒 CLOSE cursor
    db.close()             # 🔒 CLOSE database

    return jsonify({"status": "success"})

@app.route("/api/rotation/<int:land_id>")
def rotation_history(land_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT c.crop_name, s.season_name, r.year
        FROM crop_rotation_history r
        JOIN crops c ON r.crop_id = c.crop_id
        JOIN seasons s ON r.season_id = s.season_id
        WHERE land_id=%s
        ORDER BY year DESC
    """, (land_id,))

    return jsonify(cur.fetchall())
from ai_rotation import rotation_score
import requests

def get_soil_data(lat, lon):
    try:
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        params = {
            "lat": lat,
            "lon": lon,
            "property": ["nitrogen", "phh2o"]
        }
        res = requests.get(url, params=params, timeout=10).json()

        return {
            "nitrogen": res["properties"]["nitrogen"]["mean"],
            "ph": res["properties"]["phh2o"]["mean"]
        }
    except Exception:
        # SAFE FALLBACK
        return {"nitrogen": 0.5, "ph": 7.0}

from db import get_land_location
@app.route("/api/recommend/<int:land_id>")
def recommend_crop(land_id):
    land = get_land_location(land_id)

    if not land or not land["latitude"] or not land["longitude"]:
        return jsonify({"error": "Land location missing"}), 400

    soil = get_soil_data(land["latitude"], land["longitude"])
    last_crop = get_last_crop(land_id)

    recommendations = []
    for crop in get_all_crops():
        score = rotation_score(last_crop, crop, soil)
        recommendations.append({
            "crop": crop["crop_name"],
            "score": score
        })

    return jsonify(sorted(recommendations, key=lambda x: x["score"], reverse=True))
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY
    }
    return requests.get(url, params=params).json()
@app.route("/api/lands/map/<int:farmer_id>")
def lands_map(farmer_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT land_id, land_name, latitude, longitude
        FROM lands
        WHERE farmer_id = %s
    """, (farmer_id,))

    data = cur.fetchall()
    cur.close()
    db.close()
    return jsonify(data)
from db import get_land_location
@app.route("/api/debug/<int:land_id>")
def debug(land_id):
    return jsonify({
        "land": get_land_location(land_id),
        "crops_count": len(get_all_crops()),
        "last_crop": get_last_crop(land_id)
    })

# -------- RUN SERVER --------
if __name__ == "__main__":
    app.run(debug=True)
