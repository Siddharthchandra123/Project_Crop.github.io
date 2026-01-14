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
    if (data.prediction === "Image cannot be recognized") {
    result.innerHTML = "❌ Image cannot be recognized. Please upload a clear leaf image.";
} else {
    result.innerHTML = `🌿 Disease: ${data.prediction}<br>Confidence: ${data.confidence * 100}%`;
}
    
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


// Prevent redeclaration
if (!window._agroMapInitialized) {

    window._agroMapInitialized = true;

    var map = L.map('map').setView([20.5937, 78.9629], 5);
    var marker;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    map.on('click', function (e) {
        const lat = e.latlng.lat;
        const lon = e.latlng.lng;

        if (marker) {
            marker.setLatLng([lat, lon]);
        } else {
            marker = L.marker([lat, lon]).addTo(map);
        }

        window.selectedLat = lat;
        window.selectedLon = lon;

        fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`
        )
        .then(res => res.json())
        .then(data => {
            const address = data.address || {};
            const city =
                address.city ||
                address.town ||
                address.village ||
                address.state ||
                "";

            document.getElementById("city").value = city;
        });
    });
}
