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
    fetch("http://127.0.0.1:5000/predict-fertilizer", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            nitrogen: nitrogen.value,
            phosphorus: phosphorus.value,
            potassium: potassium.value,
            city: city.value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            document.getElementById("fertilizerResult").innerText =
                "❌ " + data.error;
            return;
        }

        document.getElementById("fertilizerResult").innerHTML =
            `🌱 <b>Recommended Fertilizer:</b> ${data.fertilizer}<br>
             🌡️ Temp: ${data.weather.temperature} °C<br>
             💧 Humidity: ${data.weather.humidity}%`;
    })
    .catch(err => {
        document.getElementById("fertilizerResult").innerText =
            "❌ Unable to fetch prediction";
    });
}

