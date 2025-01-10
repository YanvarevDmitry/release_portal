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
