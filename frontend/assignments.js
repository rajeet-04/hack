let assignments = [];

function submitAssignment() {
    const fileInput = document.getElementById("fileInput");
    const deadlineInput = document.getElementById("deadlineInput");

    if (!fileInput.files.length || !deadlineInput.value) {
        alert("Please select a file and enter a deadline.");
        return;
    }

    const assignment = {
        fileName: fileInput.files[0].name,
        deadline: deadlineInput.value
    };

    assignments.push(assignment);
    displayAssignments();
    checkDeadlines();
}

function displayAssignments() {
    const assignmentItems = document.getElementById("assignmentItems");
    assignmentItems.innerHTML = "";

    assignments.forEach((assignment, index) => {
        const li = document.createElement("li");
        li.innerHTML = `
            <span>${assignment.fileName} - Deadline: ${assignment.deadline}</span>
            <button onclick="askAI(${index})">Ask AI</button>
        `;
        assignmentItems.appendChild(li);
    });
}

function askAI(index) {
    alert(`AI will solve: ${assignments[index].fileName}`);
}

function checkDeadlines() {
    const today = new Date();
    assignments.forEach(assignment => {
        const deadline = new Date(assignment.deadline);
        const daysLeft = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));

        if (daysLeft === 2) {
            sendNotification(`Reminder: "${assignment.fileName}" is due in 2 days!`);
        }
    });
}

function sendNotification(message) {
    alert(message);
}
