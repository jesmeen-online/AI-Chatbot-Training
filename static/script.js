function sendMessage() {
    const message = document.getElementById("message").value.trim();
    if (message === "") return;

    // Display user message
    displayMessage("You: " + message, "user-message");

    // Clear the input field
    document.getElementById("message").value = "";

    // Send message to server
    fetch("/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "message=" + encodeURIComponent(message)
    })
    .then(response => response.json())
    .then(data => {
        // Display bot response
        displayMessage("Bot: " + data.response, "bot-message");
    });
}

function displayMessage(text, className) {
    const chatBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");
    messageElement.className = className;
    messageElement.innerText = text;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}
