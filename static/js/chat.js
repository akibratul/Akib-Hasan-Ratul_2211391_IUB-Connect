// Chat polling-based real-time messaging
document.addEventListener('DOMContentLoaded', () => {
  const chatContainer = document.getElementById('chatMessages');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const userId = document.getElementById('selectedUserId');

  if (!chatContainer || !userId || !userId.value) return;

  let lastMessageId = 0;
  const targetUserId = userId.value;

  function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
  scrollToBottom();

  // Polling for new messages
  function pollMessages() {
    fetch(`/api/messages/${targetUserId}/`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(r => r.json())
      .then(data => {
        const msgs = data.messages || [];
        if (msgs.length === 0) return;

        const latestId = msgs[msgs.length - 1].id;
        if (latestId > lastMessageId) {
          // Re-render messages
          renderMessages(msgs);
          lastMessageId = latestId;
        }
      })
      .catch(console.error);
  }

  function renderMessages(msgs) {
    chatContainer.innerHTML = '';
    let lastDate = '';
    msgs.forEach(msg => {
      const date = new Date(msg.created_at);
      const dateStr = date.toLocaleDateString();
      const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      if (dateStr !== lastDate) {
        lastDate = dateStr;
        chatContainer.innerHTML += `
          <div class="date-divider"><span>${dateStr}</span></div>
        `;
      }

      const isMe = msg.is_mine;
      chatContainer.innerHTML += `
        <div class="msg-row ${isMe ? 'mine' : 'other'}">
          <div class="msg-bubble ${isMe ? 'msg-mine' : 'msg-other'}">${escapeHtml(msg.message)}</div>
          <div class="msg-time">${time}</div>
        </div>
      `;
    });
    scrollToBottom();
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Send message via AJAX
  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch('/chat/send/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
        body: `receiver_id=${targetUserId}&message=${encodeURIComponent(message)}`
      })
        .then(r => r.json())
        .then(() => {
          chatInput.value = '';
          pollMessages();
        })
        .catch(console.error);
    });
  }

  // Initial render using server-rendered messages
  const existingMsgs = chatContainer.querySelectorAll('.msg-row');
  if (existingMsgs.length > 0) {
    const lastEl = existingMsgs[existingMsgs.length - 1];
    const id = lastEl.dataset.msgId;
    if (id) lastMessageId = parseInt(id);
  }

  // Poll every 2 seconds
  setInterval(pollMessages, 2000);
});
