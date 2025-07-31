document.addEventListener('DOMContentLoaded', (event) => {
    const socket = io();
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && chatInput.value.trim()) {
            socket.emit('message', { message: chatInput.value });
            chatInput.value = '';
        }
    });

    socket.on('message', (data) => {
        const messageDiv = document.createElement('div');
        messageDiv.innerHTML = `<p class="text-gray-800"><strong>${data.username}</strong>: ${data.message}</p><p class="text-sm text-gray-500">${new Date().toLocaleTimeString()}</p>`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    socket.on('visitor_count', (data) => {
        console.log(`Nombre de visiteurs : ${data.count}`);
    });
});