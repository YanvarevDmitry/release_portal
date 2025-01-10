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
