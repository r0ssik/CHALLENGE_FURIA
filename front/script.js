// script.js
const form = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const chat = document.getElementById('chat');
const loading = document.getElementById('loading');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const userMessage = messageInput.value.trim();
  if (!userMessage) return;

  appendMessage('Você', userMessage);
  messageInput.value = '';

  loading.style.display = 'block';

  try {
    const response = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: userMessage }),
    });

    const data = await response.json();
    appendMessage('FURIOSO', data.data || data.message || 'Erro ao obter resposta.');
  } catch (error) {
    appendMessage('Erro', 'Não foi possível se conectar ao servidor.');
  } finally {
    loading.style.display = 'none';
  }
});

function appendMessage(sender, text) {
  const messageDiv = document.createElement('div');
  messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chat.appendChild(messageDiv);
  chat.scrollTop = chat.scrollHeight;
}
