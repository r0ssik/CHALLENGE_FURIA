const form = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const chat = document.getElementById('chat');
const loading = document.getElementById('loading');

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    appendMessage('Você', userMessage);
    messageInput.value = '';

    loading.style.display = 'block';

    try {
      const response = await fetch('https://challenge-furia.onrender.com/chat', {
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
}

function appendMessage(sender, text) {
  const container = document.createElement('div');
  const message = document.createElement('div');
  const avatar = document.createElement('img');

  const isUser = sender === 'Você';
  container.className = 'message-container ' + (isUser ? 'user-container' : 'bot-container');
  message.className = isUser ? 'user-message' : 'bot-message';

  message.innerText = text;

  avatar.src = isUser ? 'user-avatar.png' : 'image.png'; 
  avatar.className = 'avatar';

  container.appendChild(avatar);
  container.appendChild(message);

  chat.appendChild(container);
  chat.scrollTop = chat.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname;

  if (currentPage.includes("unanswered.html")) {
    loadUnanswered();
  } else if (currentPage.includes("metrics.html")) {
    loadMetrics();
  } else {
    
    appendMessage('FURIOSO', 'Oii, eu sou o FURIOSO, ajudante da FURIA, com o que posso ajudar? pergunte sobre o time, os jogadores, jogadores especificos do time, calendário, contatos da fúria e sobre as partidas, estou aqui para ajudar!');
  }
});



async function loadMetrics() {
  const loading = document.getElementById('loading-metrics');
  const ctx = document.getElementById('metricsChart').getContext('2d');

  try {
    loading.style.display = 'block';

    const response = await fetch('https://challenge-furia.onrender.com/metrics');
    const data = await response.json();

    const labels = data.map(q => q.name_question);
    const dia = data.map(q => q.X_DIA);
    const mes = data.map(q => q.X_MES);
    const ano = data.map(q => q.X_ANO);
    const geral = data.map(q => q.X_GERAL);

    new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Dia",
            data: dia,
            backgroundColor: "rgba(75, 192, 192, 0.6)"
          },
          {
            label: "Mês",
            data: mes,
            backgroundColor: "rgba(153, 102, 255, 0.6)"
          },
          {
            label: "Ano",
            data: ano,
            backgroundColor: "rgba(255, 159, 64, 0.6)"
          },
          {
            label: "Geral",
            data: geral,
            backgroundColor: "rgba(255, 99, 132, 0.6)"
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "top" },
          title: { display: true, text: "Comparativo de Perguntas" }
        }
      }
    });
  } catch (error) {
    console.error('Erro ao carregar métricas', error);
  } finally {
    loading.style.display = 'none';
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const backgroundContainer = document.querySelector('.background-logos');

  if (backgroundContainer) {
    for (let i = 0; i < 100; i++) {
      const img = document.createElement('img');
      img.src = 'image.png';

      let top, left;

      do {
        top = Math.random() * 95;
        left = Math.random() * 95;
      } while (top > 30 && top < 70 && left > 30 && left < 70);

      img.style.top = top + '%';
      img.style.left = left + '%';
      img.style.transform = `rotate(${Math.random() * 360}deg) scale(${0.4 + Math.random() * 0.6})`;
      backgroundContainer.appendChild(img);
    }
  }
});
