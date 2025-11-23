let sessionId = 'session_' + Date.now();
let isWaitingForResponse = false;
let voiceModeEnabled = false;
let recognition = null;
let synthesis = window.speechSynthesis;
let isListening = false;

// Initialize when DOM is ready
function initializeApp() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const resetBtn = document.getElementById('resetBtn');
    const progressInfo = document.getElementById('progressInfo');

    if (!chatMessages || !userInput || !sendButton || !resetBtn || !progressInfo) {
        console.error('Required DOM elements not found');
        return;
    }

    // Store references globally for use in functions
    window.chatMessages = chatMessages;
    window.userInput = userInput;
    window.sendButton = sendButton;
    window.progressInfo = progressInfo;

    // Initialize voice mode
    initializeVoiceMode();

    // Initialize event listeners
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendButton.addEventListener('click', sendMessage);
    resetBtn.addEventListener('click', resetSession);

    // Quick action buttons
    document.querySelectorAll('.quick-btn[data-role]').forEach(btn => {
        btn.addEventListener('click', () => {
            const role = btn.getAttribute('data-role');
            let roleText = '';
            switch(role) {
                case 'engineer':
                    roleText = 'engineer';
                    break;
                case 'sales':
                    roleText = 'sales';
                    break;
                case 'retail':
                    roleText = 'retail';
                    break;
            }
            userInput.value = roleText;
            sendMessage();
        });
    });
    
    // Focus input on load
    userInput.focus();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

async function sendMessage() {
    const userInput = window.userInput || document.getElementById('userInput');
    const sendButton = window.sendButton || document.getElementById('sendButton');
    const chatMessages = window.chatMessages || document.getElementById('chatMessages');
    const progressInfo = window.progressInfo || document.getElementById('progressInfo');
    
    if (!userInput || !sendButton || !chatMessages) {
        console.error('Required elements not found');
        return;
    }
    
    const message = userInput.value.trim();
    
    if (!message || isWaitingForResponse) {
        return;
    }

    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    isWaitingForResponse = true;
    sendButton.disabled = true;

    // Show typing indicator
    const typingId = showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (data.response) {
            addMessage(data.response, 'bot');
            
            // Read question aloud if voice mode is enabled
            if (voiceModeEnabled && isQuestion(data.response)) {
                speakText(data.response);
            }
            
            // Update progress info
            if (data.role && progressInfo) {
                const questionNum = data.question_number || 1;
                const totalQuestions = data.total_questions || 10;
                updateProgress(data.role, questionNum, totalQuestions);
            }
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator(typingId);
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
        isWaitingForResponse = false;
        if (sendButton) sendButton.disabled = false;
        if (userInput) userInput.focus();
    }
}

function addMessage(text, type) {
    const chatMessages = window.chatMessages || document.getElementById('chatMessages');
    if (!chatMessages) {
        console.error('Chat messages container not found');
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format text with line breaks and preserve formatting
    const formattedText = formatMessage(text);
    contentDiv.innerHTML = formattedText;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 10);
}

function formatMessage(text) {
    // Replace newlines with <br>
    let formatted = text.replace(/\n/g, '<br>');
    
    // Format lists and sections
    formatted = formatted.replace(/<br>• /g, '<br>• ');
    formatted = formatted.replace(/<br>Strengths:/g, '<br><strong>Strengths:</strong>');
    formatted = formatted.replace(/<br>Areas for Improvement:/g, '<br><strong>Areas for Improvement:</strong>');
    
    // Format headers (lines with =)
    formatted = formatted.replace(/^(.+)$/gm, (match) => {
        if (match.includes('=') && match.length > 20 && !match.includes('<br>')) {
            return `<strong>${match}</strong>`;
        }
        return match;
    });
    
    // Remove any remaining emojis that might have slipped through
    formatted = formatted.replace(/[\u{1F300}-\u{1F9FF}]/gu, '');
    formatted = formatted.replace(/[\u{2600}-\u{26FF}]/gu, '');
    formatted = formatted.replace(/[\u{2700}-\u{27BF}]/gu, '');
    
    return formatted;
}

function showTypingIndicator() {
    const chatMessages = window.chatMessages || document.getElementById('chatMessages');
    if (!chatMessages) return null;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    contentDiv.appendChild(typingDiv);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 10);
    
    return 'typing-indicator';
}

function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

function updateProgress(role, questionNum, totalQuestions) {
    const progressInfo = window.progressInfo || document.getElementById('progressInfo');
    if (!progressInfo) return;
    
    const roleNames = {
        'engineer': 'Software Engineer',
        'sales': 'Sales Representative',
        'retail': 'Retail Associate'
    };
    
    // Ensure we have valid numbers
    const num = questionNum || 1;
    const total = totalQuestions || 10;
    
    progressInfo.innerHTML = `
        <p><strong>Role:</strong> ${roleNames[role] || role}</p>
        <p><strong>Progress:</strong> Question ${num} of ${total}</p>
    `;
}

async function resetSession() {
    const chatMessages = window.chatMessages || document.getElementById('chatMessages');
    const progressInfo = window.progressInfo || document.getElementById('progressInfo');
    const userInput = window.userInput || document.getElementById('userInput');
    
    if (!chatMessages || !progressInfo) {
        console.error('Required elements not found for reset');
        return;
    }
    
    if (confirm('Are you sure you want to reset the interview? This will start a new session.')) {
        try {
            // Stop any ongoing speech or recognition
            if (synthesis.speaking) synthesis.cancel();
            if (recognition && isListening) recognition.stop();
            
            await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
            
            sessionId = 'session_' + Date.now();
            chatMessages.innerHTML = `
                <div class="message bot-message">
                    <div class="message-content">
                        <p>Hello. I'm your interview practice partner. I can help you prepare for job interviews by conducting mock interviews.</p>
                        <p><strong>Available roles:</strong></p>
                        <ul>
                            <li>Software Engineer</li>
                            <li>Sales Representative</li>
                            <li>Retail Associate</li>
                        </ul>
                        <p>Type the role name to get started, or specify which position you'd like to practice for.</p>
                    </div>
                </div>
            `;
            progressInfo.innerHTML = '<p>Select a role to begin</p>';
            if (userInput) userInput.focus();
        } catch (error) {
            console.error('Error resetting:', error);
        }
    }
}

// Voice Mode Functions
function initializeVoiceMode() {
    const voiceToggle = document.getElementById('voiceModeToggle');
    const micButton = document.getElementById('micButton');
    
    if (!voiceToggle || !micButton) {
        console.warn('Voice controls not found');
        return;
    }
    
    // Check browser support
    if (!('speechSynthesis' in window)) {
        voiceToggle.disabled = true;
        voiceToggle.title = 'Text-to-speech not supported in this browser';
        return;
    }
    
    // Initialize Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;  // Enable interim results for better UX
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';
            
            // Process all results
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            const userInput = window.userInput || document.getElementById('userInput');
            if (userInput) {
                // Show interim results in real-time
                if (interimTranscript) {
                    userInput.value = interimTranscript;
                    userInput.style.borderColor = '#4a9eff';
                }
                
                // When we have final results, use them
                if (finalTranscript) {
                    finalTranscript = finalTranscript.trim();
                    console.log('Final speech recognized:', finalTranscript);
                    userInput.value = finalTranscript;
                    userInput.style.borderColor = '#4a9eff';
                    userInput.style.backgroundColor = 'rgba(74, 158, 255, 0.1)';
                    
                    updateMicStatus('Transcribed. Sending...', false);
                    
                    // Auto-send after brief delay
                    setTimeout(() => {
                        userInput.style.borderColor = '';
                        userInput.style.backgroundColor = '';
                        if (finalTranscript && finalTranscript.length > 0) {
                            sendMessage();
                        }
                    }, 800);
                }
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            isListening = false;
            if (event.error === 'no-speech') {
                updateMicStatus('No speech detected. Click to try again.', false);
            } else if (event.error === 'audio-capture') {
                updateMicStatus('No microphone found. Check your settings.', false);
            } else {
                updateMicStatus('Error: ' + event.error + '. Click to try again.', false);
            }
        };
        
        recognition.onend = () => {
            isListening = false;
            if (voiceModeEnabled) {
                updateMicStatus('Click to speak', false);
            }
        };
        
        recognition.onstart = () => {
            isListening = true;
            updateMicStatus('Listening...', true);
        };
    } else {
        micButton.disabled = true;
        micButton.title = 'Speech recognition not supported in this browser';
    }
    
    // Voice mode toggle
    voiceToggle.addEventListener('click', () => {
        voiceModeEnabled = !voiceModeEnabled;
        voiceToggle.classList.toggle('active', voiceModeEnabled);
        micButton.disabled = !voiceModeEnabled;
        
        const voiceStatus = document.getElementById('voiceStatus');
        const voiceIcon = document.getElementById('voiceIcon');
        if (voiceStatus) {
            voiceStatus.textContent = `Voice Mode: ${voiceModeEnabled ? 'On' : 'Off'}`;
        }
        if (voiceIcon) {
            voiceIcon.textContent = voiceModeEnabled ? '🔊' : '🎤';
        }
        
        if (!voiceModeEnabled && isListening && recognition) {
            recognition.stop();
        }
    });
    
    // Microphone button
    micButton.addEventListener('click', () => {
        if (!voiceModeEnabled) {
            alert('Please enable Voice Mode first');
            return;
        }
        
        if (isListening && recognition) {
            recognition.stop();
            isListening = false;
            updateMicStatus('Stopped. Click to speak', false);
        } else if (recognition) {
            try {
                // Clear any previous input
                const userInput = window.userInput || document.getElementById('userInput');
                if (userInput) {
                    userInput.value = '';
                }
                
                recognition.start();
                // Status will be updated by onstart event
            } catch (e) {
                console.error('Error starting recognition:', e);
                if (e.message && e.message.includes('already started')) {
                    recognition.stop();
                    setTimeout(() => {
                        try {
                            recognition.start();
                        } catch (e2) {
                            updateMicStatus('Error. Click to try again', false);
                        }
                    }, 100);
                } else {
                    updateMicStatus('Error. Click to try again', false);
                }
            }
        } else {
            alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
        }
    });
}

function updateMicStatus(text, active) {
    const micStatus = document.getElementById('micStatus');
    const micButton = document.getElementById('micButton');
    if (micStatus) micStatus.textContent = text;
    if (micButton) {
        micButton.classList.toggle('active', active);
    }
}

function speakText(text) {
    if (!voiceModeEnabled || !synthesis) return;
    
    // Stop any ongoing speech
    if (synthesis.speaking) {
        synthesis.cancel();
    }
    
    // Clean text for speech (remove markdown, etc.)
    const cleanText = text
        .replace(/\*\*/g, '')
        .replace(/\*/g, '')
        .replace(/\[.*?\]/g, '')
        .replace(/\(.*?\)/g, '')
        .replace(/\n/g, '. ')
        .trim();
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    utterance.onend = () => {
        // Auto-start listening after question is read (only if voice mode is on)
        if (voiceModeEnabled && recognition && !isListening) {
            setTimeout(() => {
                try {
                    const micButton = document.getElementById('micButton');
                    if (micButton && !micButton.disabled) {
                        recognition.start();
                        // Status will be updated by onstart event
                    }
                } catch (e) {
                    console.error('Error starting recognition after speech:', e);
                    // Don't show error if recognition is already running
                    if (!e.message || !e.message.includes('already started')) {
                        updateMicStatus('Click to speak', false);
                    }
                }
            }, 800);
        }
    };
    
    synthesis.speak(utterance);
}

function isQuestion(text) {
    // Check if the text is likely a question
    const questionIndicators = ['?', 'Tell me', 'Describe', 'How', 'What', 'Why', 'When', 'Where', 'Explain'];
    return questionIndicators.some(indicator => text.includes(indicator));
}

