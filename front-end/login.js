function toggleForm() {
  document.getElementById("loginForm").classList.toggle("active");
  document.getElementById("registerForm").classList.toggle("active");
}

/* Example submit handlers */
document.getElementById("loginForm").addEventListener("submit", e => {
  e.preventDefault();
  alert("Login clicked – connect to backend");
});

document.getElementById("registerForm").addEventListener("submit", e => {
  e.preventDefault();
  alert("Register clicked – connect to backend");
});
function googleLogin() {
  window.location.href = "http://localhost:5000/login/google";
}

function microsoftLogin() {
  window.location.href = "http://localhost:5000/login/microsoft";
}
