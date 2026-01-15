function predictDisease() {
    const image = document.getElementById("cropImage").files[0];
    let formData = new FormData();
    formData.append("image", image);

    fetch("http://127.0.0.1:5000/predict-disease", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("diseaseResult").innerText =
            "🦠 Disease: " + data.prediction;
    })
    .catch(err => {
        alert("API Error");
    });
}
function previewImage(event) {
    const preview = document.getElementById("imagePreview");
    const file = event.target.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function () {
        preview.src = reader.result;
        preview.classList.remove("hidden");
    };

    reader.readAsDataURL(file);
}
function predictFertilizer() {
    if (!window.selectedLat || !window.selectedLon) {
        document.getElementById("fertilizerResult").innerText =
            "⚠️ Please select a location on the map";
        return;
    }

    fetch("http://127.0.0.1:5000/predict-fertilizer", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            nitrogen: nitrogen.value,
            phosphorus: phosphorus.value,
            potassium: potassium.value,
            lat: window.selectedLat,
            lon: window.selectedLon
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("fertilizerResult").innerHTML =
            `🌱 <b>Recommended:</b> ${data.fertilizer}<br>
             🌡️ Temp: ${data.weather.temperature} °C<br>
             💧 Humidity: ${data.weather.humidity}%`;
    })
    .catch(() => {
        document.getElementById("fertilizerResult").innerText =
            "❌ Prediction failed";
    });
}

if (document.getElementById("map")) {
  let map = L.map('map').setView([20.5937, 78.9629], 5);
  // rest of Leaflet code
let marker;

// OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

// Click on map to select location
map.on('click', async function (e) {
    const { lat, lng } = e.latlng;

    if (marker) {
        marker.setLatLng([lat, lng]);
    } else {
        marker = L.marker([lat, lng]).addTo(map);
    }

    marker.bindPopup(
        `📍 Selected Location<br>Lat: ${lat.toFixed(4)}<br>Lon: ${lng.toFixed(4)}`
    ).openPopup();

    // Save coordinates globally
    window.selectedLat = lat;
    window.selectedLon = lng;

    // 🔥 Convert coords → city
    const cityName = await getCityFromCoords(lat, lng);

    if (cityName) {
        document.getElementById("city").value = cityName;
    }
});

async function getCityFromCoords(lat, lon) {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;

    const res = await fetch(url);
    const data = await res.json();

    if (data.address) {
        return (
            data.address.city ||
            data.address.town ||
            data.address.village ||
            data.address.county ||
            ""
        );
    }
    return "";
}
}
document.addEventListener("DOMContentLoaded", () => {

  const bubbleArea = document.getElementById("bubbleArea");
  if (!bubbleArea) return; // prevents crash on other pages

  const mainBubbles = [
    { text: "🌿 Crop Disease", action: "disease" },
    { text: "🧪 Fertilizer", action: "fertilizer" },
    { text: "🌦️ Weather", action: "weather" },
    { text: "🌾 Farming Tips", action: "tips" }
  ];

  loadBubbles(mainBubbles);

  function loadBubbles(bubbles) {
    bubbleArea.innerHTML = "";
    bubbles.forEach(b => createBubble(b.text, b.action));
  }

  function createBubble(text, action) {
    const div = document.createElement("div");
    div.className = "bubble";
    div.innerText = text;

    div.onclick = () => popBubble(div, action);
    bubbleArea.appendChild(div);
  }

  function popBubble(bubble, action) {
    bubble.classList.add("pop");

    setTimeout(() => {
      showNext(action);
    }, 350);
  }

function showNext(action) {

  // 🌿 Disease flow
  if (action === "disease") {
    loadBubbles([
      { text: "📸 Upload Leaf Image", action: "upload" },
      { text: "📖 Disease Info", action: "info" }
    ]);
  }

  else if (action === "upload") {
    addBotMessage("📸 Please upload a clear leaf image.");

    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";

    input.onchange = () => {
      sendDiseaseImage(input.files[0]);
    };

    input.click();
  }

  // 🧪 Fertilizer flow
  else if (action === "fertilizer") {
    loadBubbles([
      { text: "🧪 Enter NPK Values", action: "npk" },
      { text: "📍 Use Location", action: "location" }
    ]);
  }

else if (action === "npk") {
  addBotMessage("🧪 Enter N, P, K values (e.g. 10,20,30)");

  addInputBubble("N,P,K", (value) => {
    addUserMessage(value);

    const parts = value.split(",").map(Number);
    if (parts.length !== 3 || parts.some(isNaN)) {
      addBotMessage("❌ Invalid format. Please enter like 10,20,30");
      return;
    }

    const [N, P, K] = parts;

    addBotMessage("🌾 Processing fertilizer recommendation...");
    sendFertilizer(N, P, K, window.selectedLat, window.selectedLon);
  });
}
    else if (action === "location") {
  detectLocation();
}


  // 🌦️ Weather flow
else if (action === "weather") {
  const status = showStatusBubble("📍 Detecting your location...");

  detectLocation(async (lat, lon, city) => {
    status.innerText = `📍 ${city} detected`;

    setTimeout(async () => {
      status.innerText = "☁️ Fetching live weather...";

      const weather = await getWeatherByCoords(lat, lon);
      status.remove();

      showWeatherResult(weather);
    }, 1200);
  });
}


  // 🔁 Back to main
  else {
    loadBubbles(mainBubbles);
  }
}


});
function addBotMessage(text) {
  const msg = document.createElement("div");
  msg.className = "bot-message";
  msg.innerHTML = text;
  document.querySelector(".bubble-bot").appendChild(msg);
}

function addUserMessage(text) {
  const msg = document.createElement("div");
  msg.className = "user-message";
  msg.innerText = text;
  document.querySelector(".bubble-bot").appendChild(msg);
}

async function sendDiseaseImage(file) {
  showTypingBubble();
setTimeout(() => {
  removeTypingBubble();
  addBotMessage("🔍 Analyzing leaf image...");
}, 800);


  const formData = new FormData();
  formData.append("image", file);

  const res = await fetch("http://127.0.0.1:5000/predict-disease", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  if (data.prediction) {
    addBotMessage(
  `🌿 <b>Disease:</b> ${data.prediction}\n` +
  `📊 <b>Confidence:</b> ${Math.round(data.confidence * 100)}%`
);

  } else {
    addBotMessage("❌ Unable to analyze image.");
  }
  document.getElementById("backBtn").style.display = "block";

}
async function sendFertilizer(N, P, K, lat, lon) {
  addBotMessage("🌾 Calculating best fertilizer...");

  const res = await fetch("http://127.0.0.1:5000/predict-fertilizer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nitrogen: N,
      phosphorus: P,
      potassium: K,
      lat: lat,
      lon: lon
    })
  });

  const data = await res.json();

  if (data.fertilizer) {
    addBotMessage(
      `🧪 Recommended Crop/Fertilizer: ${data.fertilizer}\n` +
      `🌡️ Temp: ${data.weather.temperature}°C\n` +
      `💧 Humidity: ${data.weather.humidity}%`
    );

    if (data.alerts && data.alerts.length) {
      data.alerts.forEach(a => addBotMessage(a));
    }
  } else {
    addBotMessage("❌ Could not generate recommendation.");
  }
  document.getElementById("backBtn").style.display = "block";

}
function addInputBubble(placeholder, onSubmit) {
  const wrapper = document.createElement("div");
  wrapper.className = "input-bubble";

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = placeholder;

  const btn = document.createElement("button");
  btn.innerText = "OK";

  btn.onclick = () => {
    if (!input.value.trim()) return;
    wrapper.remove();
    onSubmit(input.value.trim());
  };

  wrapper.appendChild(input);
  wrapper.appendChild(btn);

  document.querySelector(".bubble-bot").appendChild(wrapper);
}

function detectLocation(callback) {
  if (!navigator.geolocation) {
    addBotMessage("❌ Geolocation not supported.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;

      window.selectedLat = lat;
      window.selectedLon = lon;

      const city = await reverseGeocode(lat, lon);

      if (callback) callback(lat, lon, city);
    },
    () => addBotMessage("❌ Location access denied.")
  );
}

async function reverseGeocode(lat, lon) {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`
    );
    const data = await res.json();

    return (
      data.address.city ||
      data.address.town ||
      data.address.village ||
      data.address.county ||
      ""
    );
  } catch {
    return "";
  }
}
function showStatusBubble(text) {
  const bubble = document.createElement("div");
  bubble.className = "status-bubble";
  bubble.innerText = text;

  document.querySelector(".bubble-bot").appendChild(bubble);
  return bubble;
}
function showWeatherResult(weather) {
  const card = document.createElement("div");
  card.className = "weather-card";

  card.innerHTML = `
    <div class="wc-temp">🌡️ ${weather.temp}°C</div>
    <div class="wc-cond">${weather.condition}</div>
    <div class="wc-row">
      💧 Humidity: ${weather.humidity}%
    </div>
    <div class="wc-row">
      🌬️ Wind: ${weather.wind} km/h
    </div>
  `;

  document.querySelector(".bubble-bot").appendChild(card);

  showWeatherAdvice(weather);
  document.getElementById("backBtn").style.display = "block";

}
function showWeatherAdvice(w) {
  let advice = "✅ Weather is suitable for farming today.";

  if (w.temp > 35)
    advice = "🔥 Hot day! Irrigate crops in early morning or evening.";
  else if (w.humidity > 80)
    advice = "⚠️ High humidity. Monitor crops for fungal diseases.";
  else if (w.rain > 5)
    advice = "🌧️ Rain expected. Avoid spraying fertilizers.";

  addBotMessage("🌾 " + advice);
}
async function getWeatherByCoords(lat, lon) {
  const res = await fetch(
    `https://api.weatherapi.com/v1/current.json?key=dde2b9fb075e41d4b8082159261401&q=${lat},${lon}&aqi=no`
  );

  const data = await res.json();

  return {
    temp: data.current.temp_c,
    humidity: data.current.humidity,
    wind: data.current.wind_kph,
    rain: data.current.precip_mm,
    condition: data.current.condition.text
  };
}
function showTypingBubble() {
  const typing = document.createElement("div");
  typing.className = "bot-message typing";
  typing.id = "typingBubble";
  typing.innerText = "AgroAI is typing...";
  document.querySelector(".bubble-bot").appendChild(typing);
  scrollChat();
}

function removeTypingBubble() {
  const t = document.getElementById("typingBubble");
  if (t) t.remove();
}
function scrollChat() {
  const chat = document.querySelector(".bubble-bot");
  chat.scrollTop = chat.scrollHeight;
}
function resetChat() {
  const chat = document.querySelector(".bubble-bot");
  chat.innerHTML = "";

  addBotMessage(
    "👋 Welcome back! What would you like help with?\n\n" +
    "🌿 Disease Detection\n" +
    "🧪 Fertilizer Recommendation\n" +
    "🌦️ Weather Alerts"
  );

  document.getElementById("backBtn").style.display = "none";
}
