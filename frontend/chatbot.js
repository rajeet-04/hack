function sendMessage() {
    const userInput = document.getElementById("userInput").value;
    if (!userInput.trim()) return;  // Do not send empty messages

    // Display user message
    displayUserMessage(userInput);

    // Show typing indicator
    showTypingIndicator(true);

    // Send the query to the backend (Flask server)
    fetch('http://127.0.0.1:5000/query', {  // Adjust the URL if necessary
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: userInput })
    })
        .then(response => response.json())
        .then(data => {
            showTypingIndicator(false);
            // Display bot response
            displayBotMessage(data.response);
        })
        .catch(error => {
            showTypingIndicator(false);
            console.error('Error:', error);
            displayBotMessage("Sorry, I couldn't get a response.");
        });
}

function displayUserMessage(message) {
    const chatlogs = document.getElementById("chatlogs");
    const userMessageDiv = document.createElement("div");
    userMessageDiv.classList.add("message", "user");
    userMessageDiv.textContent = message;
    chatlogs.appendChild(userMessageDiv);
}

function displayBotMessage(message) {
    const chatlogs = document.getElementById("chatlogs");
    const botMessageDiv = document.createElement("div");
    botMessageDiv.classList.add("message", "bot");
    botMessageDiv.textContent = message;
    chatlogs.appendChild(botMessageDiv);
}

function showTypingIndicator(show) {
    const typingIndicator = document.getElementById("typingIndicator");
    typingIndicator.style.display = show ? 'inline-block' : 'none';
}

// Handle Enter key press to trigger sendMessage function
function handleEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}
