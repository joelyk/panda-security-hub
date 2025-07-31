document.addEventListener('DOMContentLoaded', (event) => {
    const socket = io();
    const chatBox = document.getElementById('chat-box');
    const chatInput = document.getElementById('chat-input');
    const toggleChat = document.getElementById('toggle-chat');

    // Emojis support
    const emojiMap = {
        ":)": "😊",
        ":(": "😞",
        ":D": "😃",
        ":P": "😛",
        ":O": "😮",
        ";)": "😉",
        "<3": "❤️",
        ":thumbsup:": "👍",
        ":wave:": "👋",
        ":lightbulb:": "💡",
        ":computer:": "💻",
        ":lock:": "🔒",
        ":shield:": "🛡️",
        ":panda:": "🐼",
        ":rocket:": "🚀"
    };

    function replaceEmojis(text) {
        return text.replace(/:\)|:\(|:D|:P|:O|;\)|<3|:thumbsup:|:wave:|:lightbulb:|:computer:|:lock:|:shield:|:panda:|:rocket:/g, 
            match => emojiMap[match]);
    }

    // Send message on Enter
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && chatInput.value.trim()) {
            const messageWithEmojis = replaceEmojis(chatInput.value);
            socket.emit('message', { 
                message: messageWithEmojis,
                username: "{{ current_user.username if current_user.is_authenticated else 'Invité' }}"
            });
            chatInput.value = '';
        }
    });

    // Receive messages
    socket.on('message', (data) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'bg-white p-3 rounded-lg shadow-sm mb-2';
        messageDiv.innerHTML = `
            <p class="font-semibold text-green-600">${data.username}</p>
            <p class="text-gray-800">${data.message}</p>
            <p class="text-xs text-gray-500 mt-1">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} ⌚</p>
        `;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // Visitor count
    socket.on('visitor_count', (data) => {
        console.log(`👥 Nombre de visiteurs : ${data.count}`);
    });

    // Connection status
    socket.on('connect', () => {
        console.log('🔌 Connecté au chat en direct');
    });

    socket.on('disconnect', () => {
        console.log('❌ Déconnecté du chat');
    });

    // Welcome message
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'bg-blue-50 p-3 rounded-lg mb-2 text-center';
    welcomeDiv.innerHTML = `
        <p class="text-sm text-blue-800">Bienvenue sur le chat PandaSecurityHub! 🐼💬</p>
        <p class="text-xs text-blue-600 mt-1">Envoyez vos questions ici.</p>
    `;
    chatBox.appendChild(welcomeDiv);
});