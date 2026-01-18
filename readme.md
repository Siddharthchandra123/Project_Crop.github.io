🌱 AgroAI – Smart Farming Intelligence Platform

AgroAI is an AI-powered smart farming platform designed to help farmers make data-driven agricultural decisions. It integrates machine learning, real-time data, and interactive dashboards to improve crop productivity, reduce losses, and support sustainable farming.

🚀 Features

🌾 Crop Disease Detection

Upload leaf images and detect crop diseases using deep learning (CNN).

🌦️ Weather Alerts & Farmer Notifications

Real-time weather alerts for rainfall, heatwaves, frost, and storms.

🧪 Soil Analysis & Soil Map Integration

Interactive India soil map with soil type and region-wise data.

💰 Live Mandi Price Dashboard

State-wise and crop-wise mandi prices with visual charts.

🔁 Crop Rotation Tracker

Track land usage and suggest crop rotation for soil health.

🤖 AI Chatbot for Farmers

Fixed-position chatbot for instant farming guidance.

🔐 Login & Registration System

Secure authentication for farmers and users.

🛠️ Tech Stack
Frontend

HTML5, CSS3, JavaScript

AOS (Animate on Scroll)

Chart.js

SVG (Interactive India Map)

Backend

Python (Flask)

Flask-CORS

REST APIs

Machine Learning

PyTorch

Custom CNN / ResNet-based model

Image preprocessing with PIL & TorchVision

Database

MySQL

APIs Used

Weather API

Mandi Price (Government Open Data)

Soil Data (SoilGrids API)

📂 Project Structure
AgroAI/
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── css/
│   └── js/
│
├── backend/
│   ├── app.py
│   ├── model.py
│   ├── routes/
│   └── utils/
│
├── ml_model/
│   ├── trained_model.pth
│   └── dataset/
│
├── database/
│   └── schema.sql
│
├── README.md
└── requirements.txt

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/AgroAI.git
cd AgroAI

2️⃣ Backend Setup
pip install -r requirements.txt
python app.py

3️⃣ Frontend

Open index.html in your browser
OR

Serve using Live Server (VS Code recommended)

🧠 ML Model Details

Input Image Size: 256 x 256

Framework: PyTorch

Model: CNN / ResNet-based architecture

Output: Disease classification with confidence score

📊 Use Cases

Farmers checking real-time crop prices

Early disease detection to prevent losses

Understanding soil suitability

Planning crops using weather & rotation data

Government & Agri-Tech demonstrations

🔮 Future Enhancements

🌍 Multilingual support (Hindi & regional languages)

📱 Mobile App (Flutter / React Native)

📡 IoT sensor integration

📈 Yield prediction using historical data

🧾 Government scheme recommendations

🤝 Contribution

Contributions are welcome!

Fork the repo

Create a new branch

Commit your changes

Open a Pull Request

📜 License

This project is licensed under the MIT License.

👨‍💻 Author

Siddharth Chandra
B.Tech | AI & Web Development
AgroAI – Smart Agriculture Initiative 🌾