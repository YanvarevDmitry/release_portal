const API_URL = "http://localhost:8000"; // URL вашего API

// Получение всех этапов релиза
async function fetchReleaseStages() {
    const response = await fetch(`${API_URL}/release_stages/`);
    const stages = await response.json();
    const stagesList = document.getElementById("releaseStagesList");
    stagesList.innerHTML = "";
    stages.forEach(stage => {
        const li = document.createElement("li");
        li.textContent = `${stage.name} - ${stage.responsible_person}`;
        stagesList.appendChild(li);
    });
}

// Создание нового этапа релиза
document.getElementById("releaseForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const newStage = {
        name: document.getElementById("name").value,
        description: document.getElementById("description").value,
        start_date: document.getElementById("start_date").value,
        end_date: document.getElementById("end_date").value,
        responsible_person: document.getElementById("responsible_person").value,
    };

    const response = await fetch(`${API_URL}/release_stages/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(newStage),
    });

    if (response.ok) {
        fetchReleaseStages();  // Обновить список
    } else {
        alert("Failed to create release stage.");
    }
});

// Инициализация
fetchReleaseStages();
