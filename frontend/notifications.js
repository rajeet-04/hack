document.addEventListener("DOMContentLoaded", function () {
    checkDeadlines(); // Check deadlines when page loads
});

// Function to check deadlines
function checkDeadlines() {
    const notificationItems = document.getElementById("notificationItems");
    notificationItems.innerHTML = "";

    const currentDate = new Date();
    assignments.forEach((assignment) => {
        const deadlineDate = new Date(assignment.deadline);
        const timeDiff = deadlineDate - currentDate;
        const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));

        if (daysDiff === 2) {
            showNotification(assignment.fileName, daysDiff);
        }
    });
}

// Function to show a local notification
function showNotification(fileName, daysDiff) {
    if ("Notification" in window) {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification("Assignment Reminder", {
                    body: `Deadline for "${fileName}" is in ${daysDiff} days.`,
                });
            }
        });
    } else {
        alert(`Deadline for "${fileName}" is in ${daysDiff} days.`);
    }
}
