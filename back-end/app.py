from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
import torch

from authlib.integrations.flask_client import OAuth
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
model.load_state_dict(torch.load(r"C:\Users\Lenovo\Downloads\Project_Crop\back-end\plant_disease_model.pth", map_location=device))
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
with open(r"C:\Users\Lenovo\Downloads\Project_Crop\back-end\fertilizer.pkl", "rb") as f:
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


oauth = OAuth(app)

# GOOGLE
google = oauth.register(
    name='google',
    client_id='GOOGLE_CLIENT_ID',
    client_secret='GOOGLE_CLIENT_SECRET',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'}
)

# MICROSOFT
microsoft = oauth.register(
    name='microsoft',
    client_id='MICROSOFT_CLIENT_ID',
    client_secret='MICROSOFT_CLIENT_SECRET',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    api_base_url='https://graph.microsoft.com/v1.0/',
    client_kwargs={'scope': 'User.Read'}
)
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google')
def google_auth():
    token = google.authorize_access_token()
    user = google.get('userinfo').json()
    print(user)  # email, name, picture
    return redirect("http://localhost:3000/dashboard")
@app.route('/login/microsoft')
def login_microsoft():
    redirect_uri = url_for('microsoft_auth', _external=True)
    return microsoft.authorize_redirect(redirect_uri)

@app.route('/auth/microsoft')
def microsoft_auth():
    token = microsoft.authorize_access_token()
    user = microsoft.get('me').json()
    print(user)
    return redirect("http://localhost:3000/dashboard")

# -------- RUN SERVER --------
if __name__ == "__main__":
    app.run(debug=True)
