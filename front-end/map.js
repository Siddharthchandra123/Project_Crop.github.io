const map = L.map('map').setView([22.5, 78.9], 5);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

fetch("http://127.0.0.1:5000/api/lands/map/1")
.then(res => res.json())
.then(lands => {
    lands.forEach(land => {
        L.marker([land.latitude, land.longitude])
        .addTo(map)
        .bindPopup(`<b>${land.land_name}</b><br>Land ID: ${land.land_id}`);
    });
});
