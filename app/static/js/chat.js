const socket = io();

socket.on('connect', () => {
    console.log('Connected to WebSocket');
});

socket.on('message', (data) => {
    const chatBox = document.getElementById('chat-box');
    const message = document.createElement('div');
    message.textContent = `💬 ${data.username}: ${data.message}`;
    message.className = 'mb-3 text-sm p-2 bg-gray-100 rounded-lg';
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
});

socket.on('visitor_count', (data) => {
    document.getElementById('visitor-count').textContent = `Visiteurs : ${data.count} 👀`;
});

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value;
    if (message && currentUser !== 'Anonyme') {
        socket.emit('message', { username: currentUser, message });
        input.value = '';
    } else if (currentUser === 'Anonyme') {
        alert('Connectez-vous pour envoyer un message. 🔐');
    }
}