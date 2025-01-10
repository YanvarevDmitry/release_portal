const API_BASE = "http://127.0.0.1:8000";

async function apiRequest(endpoint, method = "GET", body = null, token = null) {
    const headers = {
        "Content-Type": "application/json",
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "API request failed");
    }
    return await response.json();
}
import { loadProfile } from "./components/profile.js";
import { loadReleases } from "./components/releases.js";
import { loadAdmin } from "./components/admin.js";
import { loadHelp } from "./components/help.js";

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("nav-profile").addEventListener("click", loadProfile);
    document.getElementById("nav-releases").addEventListener("click", loadReleases);
    document.getElementById("nav-admin").addEventListener("click", loadAdmin);
    document.getElementById("nav-help").addEventListener("click", loadHelp);
});
import { apiRequest } from "../api.js";

export async function loadProfile() {
    const app = document.getElementById("app");
    app.innerHTML = "<p>Loading profile...</p>";

    try {
        const profile = await apiRequest("/profile/");
        app.innerHTML = `
            <h2>Profile</h2>
            <p>Username: ${profile.username}</p>
            <p>Email: ${profile.email}</p>
            <p>Role: ${profile.role}</p>
            <button id="edit-profile">Edit Profile</button>
        `;
        document.getElementById("edit-profile").addEventListener("click", () => {
            app.innerHTML = `
                <h2>Edit Profile</h2>
                <form id="profile-form">
                    <label for="email">Email:</label>
                    <input type="email" id="email" value="${profile.email}" required>
                    <button type="submit">Save</button>
                </form>
            `;
            document.getElementById("profile-form").addEventListener("submit", async (e) => {
                e.preventDefault();
                const newEmail = document.getElementById("email").value;
                await apiRequest("/profile/", "PUT", { email: newEmail });
                alert("Profile updated!");
                loadProfile();
            });
        });
    } catch (error) {
        app.innerHTML = `<p>Error loading profile: ${error.message}</p>`;
    }
}
import { apiRequest } from "../api.js";

export async function loadReleases() {
    const app = document.getElementById("app");
    app.innerHTML = "<p>Loading releases...</p>";

    try {
        const releases = await apiRequest("/release_stages/");
        app.innerHTML = `
            <h2>Releases</h2>
            <ul>
                ${releases.map(release => `<li>${release.name} (${release.start_date} - ${release.end_date})</li>`).join("")}
            </ul>
        `;
    } catch (error) {
        app.innerHTML = `<p>Error loading releases: ${error.message}</p>`;
    }
}
import { apiRequest } from "../api.js";

export async function loadAdmin() {
    const app = document.getElementById("app");
    app.innerHTML = "<p>Loading admin panel...</p>";

    try {
        const users = await apiRequest("/users/");
        app.innerHTML = `
            <h2>Admin Panel</h2>
            <ul>
                ${users.map(user => `<li>${user.username} (${user.role.name})</li>`).join("")}
            </ul>
        `;
    } catch (error) {
        app.innerHTML = `<p>Error loading admin panel: ${error.message}</p>`;
    }
}
export function loadHelp() {
    const app = document.getElementById("app");
    app.innerHTML = `
        <h2>Help</h2>
        <p>Welcome to the Release Management Platform!</p>
        <ul>
            <li>Profile: Manage your personal information.</li>
            <li>Releases: View and manage release stages.</li>
            <li>Admin Panel: Available to administrators for user management.</li>
        </ul>
    `;
}
let authToken = null;

export function setAuthToken(token) {
    authToken = token;
}

export async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = {
        "Content-Type": "application/json",
    };
    if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

    const response = await fetch(`${API_BASE}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "API request failed");
    }
    return await response.json();
}

export async function login(username, password) {
    const response = await apiRequest("/auth/login", "POST", { username, password });
    setAuthToken(response.access_token);
    return response;
}
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
