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

