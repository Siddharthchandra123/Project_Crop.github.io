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
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image = Image.open(request.files["image"]).convert("RGB")
        image = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(image)
            pred_index = torch.argmax(outputs, dim=1).item()

        return jsonify({
            "class_index": pred_index,
            "prediction": CLASS_NAMES[pred_index]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------- RUN SERVER --------
if __name__ == "__main__":
    app.run(debug=True)
