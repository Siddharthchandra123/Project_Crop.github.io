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
    print("WeatherAPI status:", response.status_code)
    print("WeatherAPI response:", response.text)

    if response.status_code != 200:
        raise Exception(response.json().get("error", {}).get("message", "Weather API error"))

    data = response.json()

    temperature = data["current"]["temp_c"]
    humidity = data["current"]["humidity"]
    
    return temperature, humidity
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

        temperature, humidity = get_weather_by_coords(lat, lon)

        # 🧪 optional pH (default)
        ph = float(data.get("ph", 6.5))
        rainfall = float(data.get("rainfall", 100))

        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

        prediction = fertilizer_model.predict(features)[0]

        return jsonify({
            "fertilizer": prediction,
            "weather": {
                "temperature": temperature,
                "humidity": humidity
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------- RUN SERVER --------
if __name__ == "__main__":
    app.run(debug=True)
