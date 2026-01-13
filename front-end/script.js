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
