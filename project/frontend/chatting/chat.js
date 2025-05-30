async function ask() {
  const input = document.getElementById('userInput');
  const message = input.value.trim();
  if (!message) return;

  const userChat = document.createElement('div');
  userChat.className = 'chat user';
  userChat.innerText = message;
  document.getElementById('chatHistory').appendChild(userChat);

  input.value = '';

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: message })
    });

    const data = await res.json();
    const botChat = document.createElement('div');
    botChat.className = 'chat bot';
    botChat.innerText = data.answer || JSON.stringify(data, null, 2);
    document.getElementById('chatHistory').appendChild(botChat);
  } catch (err) {
    const errorChat = document.createElement('div');
    errorChat.className = 'chat bot error';
    errorChat.innerText = "❌ 오류 발생: " + err.message;
    document.getElementById('chatHistory').appendChild(errorChat);
  }
}

function resetChat() {
  document.getElementById('chatHistory').innerHTML = '';
}

async function updateStatus() {
  try {
    const res = await fetch('/api/vector_status');
    const data = await res.json();

    document.getElementById("sql-status").innerHTML = `
      <div><strong>SQL</strong></div>
      <div>DB: ${data.sql.loaded ? "✅" : "⚠️"}</div>
      <div>문서수: ${data.sql.doc_count}</div>
    `;

    document.getElementById("manual-status").innerHTML = `
      <div><strong>MANUAL</strong></div>
      <div>DB: ${data.manual.loaded ? "✅" : "⚠️"}</div>
      <div>문서수: ${data.manual.doc_count}</div>
    `;

    document.getElementById("log-status").innerHTML = `
      <div><strong>LOG</strong></div>
      <div>DB: ${data.log.loaded ? "✅" : "⚠️"}</div>
      <div>문서수: ${data.log.doc_count}</div>
    `;
  } catch (e) {
    console.error("상태 확인 실패", e);
    ["sql-status", "manual-status", "log-status"].forEach(id => {
      document.getElementById(id).innerText = "❌ 상태 확인 실패";
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  resetChat();
  updateStatus();
});
