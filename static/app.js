import { login, setAuthToken } from "./api.js";
import { loadProfile } from "./components/profile.js";
import { loadReleases } from "./components/releases.js";
import { loadAdmin } from "./components/admin.js";
import { loadHelp } from "./components/help.js";

document.addEventListener("DOMContentLoaded", () => {
    const app = document.getElementById("app");

    // Проверка авторизации
    const token = localStorage.getItem("authToken");
    if (token) {
        setAuthToken(token);
        app.innerHTML = "<p>Welcome back! Choose an option from the menu.</p>";
    } else {
        showLoginForm();
    }

    document.getElementById("nav-profile").addEventListener("click", loadProfile);
    document.getElementById("nav-releases").addEventListener("click", loadReleases);
    document.getElementById("nav-admin").addEventListener("click", loadAdmin);
    document.getElementById("nav-help").addEventListener("click", loadHelp);
});

function showLoginForm() {
    const app = document.getElementById("app");
    app.innerHTML = `
        <h2>Login</h2>
        <form id="login-form">
            <label for="username">Username:</label>
            <input type="text" id="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" required>
            <button type="submit">Login</button>
        </form>
    `;
    document.getElementById("login-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;
        try {
            const response = await login(username, password);
            localStorage.setItem("authToken", response.access_token);
            setAuthToken(response.access_token);
            alert("Login successful!");
            location.reload();
        } catch (error) {
            alert(`Login failed: ${error.message}`);
        }
    });
}
