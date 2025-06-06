document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    
    // Add welcome message
    if (chatMessages && !chatMessages.hasChildNodes()) {
        addBotMessage("Hello! I'm your health assistant. Please describe your symptoms, and I'll try to help you.");
    }
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addUserMessage(message);
            
            // Clear input
            chatInput.value = '';
            
            // Show thinking indicator
            const thinkingIndicator = document.createElement('div');
            thinkingIndicator.className = 'message bot-message thinking';
            thinkingIndicator.innerHTML = '<div class="loader"></div> Thinking...';
            chatMessages.appendChild(thinkingIndicator);
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Send message to backend
            fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                // Remove thinking indicator
                const thinking = document.querySelector('.thinking');
                if (thinking) thinking.remove();
                
                if (data.answer) {
                    addBotMessage(data.answer);
                } else {
                    addBotMessage("I'm sorry, but I couldn't process your request at this time. Please try again later.");
                }
            })
            .catch(error => {
                console.error('Error during chat:', error);
                
                // Remove thinking indicator
                const thinking = document.querySelector('.thinking');
                if (thinking) thinking.remove();
                
                addBotMessage("I'm sorry, but there was an error processing your request. Please try again later.");
            });
        });
    }
    
    // Function to add user message to chat
    function addUserMessage(text) {
        if (!chatMessages) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to add bot message to chat
    function addBotMessage(text) {
        if (!chatMessages) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';
        
        // Check if message contains HTML
        if (text.includes('<') && text.includes('>')) {
            messageElement.innerHTML = text;
        } else {
            // Process text for line breaks and formatting
            const formattedText = text.replace(/\n/g, '<br>');
            messageElement.innerHTML = formattedText;
        }
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Quick symptom buttons
    const quickSymptomButtons = document.querySelectorAll('.quick-symptom');
    if (quickSymptomButtons) {
        quickSymptomButtons.forEach(button => {
            button.addEventListener('click', function() {
                const symptom = this.textContent.trim();
                if (chatInput) {
                    chatInput.value = `I have ${symptom}`;
                    chatInput.focus();
                }
            });
        });
    }
    
    // Voice input functionality (if supported by browser)
    const voiceInputBtn = document.getElementById('voice-input');
    if (voiceInputBtn && 'webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        let isListening = false;
        
        voiceInputBtn.addEventListener('click', function() {
            if (!isListening) {
                // Start listening
                recognition.start();
                voiceInputBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                voiceInputBtn.classList.add('listening');
                isListening = true;
            } else {
                // Stop listening
                recognition.stop();
                voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                voiceInputBtn.classList.remove('listening');
                isListening = false;
            }
        });
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            
            // Stop listening
            recognition.stop();
            voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceInputBtn.classList.remove('listening');
            isListening = false;
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            
            // Stop listening
            voiceInputBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceInputBtn.classList.remove('listening');
            isListening = false;
            
            if (event.error === 'not-allowed') {
                addBotMessage("I need microphone permission to use voice input. Please allow microphone access.");
            } else {
                addBotMessage("Sorry, I couldn't understand your voice input. Please try again or type your symptoms.");
            }
        };
    } else if (voiceInputBtn) {
        // Hide button if not supported
        voiceInputBtn.style.display = 'none';
    }
});