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
