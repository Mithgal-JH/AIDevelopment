const chatBtn = document.getElementById("chat-btn");
const chatWindow = document.getElementById("chat-window");
const messagesContainer = document.getElementById("messages");
const sendBtn = document.getElementById("send-btn");
const emailInput = document.getElementById("email-input");
const chatCloseBtn = document.querySelector(".chat-close");
const chatForm = document.querySelector(".chat-input-area");

// Toggle chat window open/close
function toggleChat(open) {
  if (open === undefined) {
    open = chatWindow.classList.contains("hidden");
  }

  if (open) {
    chatWindow.classList.remove("hidden");
    chatBtn.setAttribute("aria-expanded", "true");
    emailInput.focus();
  } else {
    chatWindow.classList.add("hidden");
    chatBtn.setAttribute("aria-expanded", "false");
  }
}

// Open chat when clicking button
chatBtn.addEventListener("click", () => {
  toggleChat();
});

// Close chat when clicking close button
chatCloseBtn.addEventListener("click", () => {
  toggleChat(false);
});

// Add message to chat display
function addMessage(type, content) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message message-${type}`;
  messageDiv.innerHTML = content;
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Handle form submission
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const text = emailInput.value.trim();

  if (!text) {
    addMessage(
      "error",
      "<strong>Error:</strong> Please type a message first."
    );
    return;
  }

  // Add user message to chat
  addMessage("user", `<strong>You:</strong> ${text}`);
  emailInput.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Checking...";

  try {
    const response = await fetch("/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Classification failed.");
    }

    const resultHTML = `
      <div><strong>Bot:</strong></div>
      <div><strong>Final Prediction:</strong> ${data.final_prediction}</div>
      <div><strong>Cosine Similarity:</strong> ${data.cosine_similarity}</div>
      <div><strong>Naive Bayes:</strong> ${data.naive_bayes}</div>
      <div><strong>Logistic Regression:</strong> ${data.logistic_regression}</div>
    `;
    addMessage("bot", resultHTML);
  } catch (error) {
    addMessage("error", `<strong>Error:</strong> ${error.message}`);
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Classify";
  }
});
