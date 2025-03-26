// Main application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const onboardingScreen = document.getElementById('onboarding-screen');
    const chatScreen = document.getElementById('chat-screen');
    const reviewScreen = document.getElementById('review-screen');
    const setupForm = document.getElementById('setup-form');
    const messageForm = document.getElementById('message-form');
    const userMessageInput = document.getElementById('user-message');
    const chatMessages = document.getElementById('chat-messages');
    const mistakeFeedback = document.getElementById('mistake-feedback');
    const languageBadge = document.getElementById('language-badge');
    const scenarioBadge = document.getElementById('scenario-badge');
    const endSessionBtn = document.getElementById('end-session-btn');
    const newSessionBtn = document.getElementById('new-session-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // App state
    let currentStep = 1;
    let selectedScenario = '';
    let sessionActive = false;
    
    // Step navigation
    document.querySelectorAll('.next-btn').forEach(button => {
        button.addEventListener('click', function() {
            const nextStepId = this.getAttribute('data-next');
            showStep(nextStepId);
        });
    });
    
    document.querySelectorAll('.back-btn').forEach(button => {
        button.addEventListener('click', function() {
            const prevStepId = this.getAttribute('data-prev');
            showStep(prevStepId);
        });
    });
    
    function showStep(stepId) {
        // Hide all steps
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show the target step
        document.getElementById(stepId).classList.add('active');
    }
    
    // Scenario selection
    document.querySelectorAll('.scenario-card').forEach(card => {
        card.addEventListener('click', function() {
            // Remove selection from all cards
            document.querySelectorAll('.scenario-card').forEach(c => {
                c.classList.remove('selected');
            });
            
            // Select this card
            this.classList.add('selected');
            selectedScenario = this.getAttribute('data-scenario');
        });
    });
    
    // Form submission
    setupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!selectedScenario) {
            alert('Please select a conversation scenario');
            return;
        }
        
        const formData = {
            username: document.getElementById('username').value,
            native_language: document.getElementById('native-language').value,
            learning_language: document.getElementById('learning-language').value,
            proficiency_level: document.getElementById('proficiency-level').value,
            selected_scene: selectedScenario
        };
        
        // Show loading overlay
        loadingOverlay.classList.add('active');
        
        // Start session
        fetch('/api/start-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                sessionActive = true;
                
                // Update UI with selected language and scenario
                languageBadge.textContent = formData.learning_language;
                scenarioBadge.textContent = formData.selected_scene
                    .split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                
                // Show chat screen
                onboardingScreen.classList.remove('active');
                chatScreen.classList.add('active');
                
                // Send initial message to get conversation started
                sendInitialMessage();
            } else {
                alert('Error starting session: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        })
        .finally(() => {
            loadingOverlay.classList.remove('active');
        });
    });
    
    // Send initial message to start conversation
    function sendInitialMessage() {
        const initialMessage = {
            message: "Hello, I'm here to practice. Let's start the conversation."
        };
        
        loadingOverlay.classList.add('active');
        
        fetch('/api/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(initialMessage)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Add bot's response to chat
                addMessage(data.message, 'bot');
            } else {
                console.error('Error:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            loadingOverlay.classList.remove('active');
        });
    }
    
    // Message submission
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const userMessage = userMessageInput.value.trim();
        
        if (!userMessage || !sessionActive) return;
        
        // Add user message to chat
        addMessage(userMessage, 'user');
        
        // Clear input
        userMessageInput.value = '';
        
        // Hide previous mistake feedback
        mistakeFeedback.innerHTML = '';
        mistakeFeedback.classList.remove('active');
        
        // Show loading overlay
        loadingOverlay.classList.add('active');
        
        // Send message to API
        fetch('/api/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Add bot's response to chat
                addMessage(data.message, 'bot');
                
                // Check if user made mistakes
                if (data.has_mistakes && data.mistakes.length > 0) {
                    showMistakeFeedback(data.mistakes);
                }
            } else {
                console.error('Error:', data.message);
                addSystemMessage('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addSystemMessage('An error occurred. Please try again.');
        })
        .finally(() => {
            loadingOverlay.classList.remove('active');
            
            // Scroll to bottom of chat
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    });
    
    // End session button
    endSessionBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to end this session? You will see a review of your performance.')) {
            loadingOverlay.classList.add('active');
            
            // Get review
            fetch('/api/get-review')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        displayReview(data);
                        
                        // End the session
                        fetch('/api/end-session', {
                            method: 'POST'
                        })
                        .then(() => {
                            sessionActive = false;
                        })
                        .catch(error => {
                            console.error('Error ending session:', error);
                        });
                        
                        // Show review screen
                        chatScreen.classList.remove('active');
                        reviewScreen.classList.add('active');
                    } else {
                        alert('Error getting review: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while getting your review.');
                })
                .finally(() => {
                    loadingOverlay.classList.remove('active');
                });
        }
    });
    
    // New session button
    newSessionBtn.addEventListener('click', function() {
        // Reset form
        setupForm.reset();
        document.querySelectorAll('.scenario-card').forEach(card => {
            card.classList.remove('selected');
        });
        selectedScenario = '';
        
        // Clear chat
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h3>Ready to practice!</h3>
                <p>Start chatting in your learning language. The assistant will respond and provide feedback on your messages.</p>
            </div>
        `;
        
        // Show first step
        showStep('step1');
        
        // Show onboarding screen
        reviewScreen.classList.remove('active');
        onboardingScreen.classList.add('active');
    });
    
    // Helper functions
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender + '-message');
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        
        // Process newlines and format text
        const formattedMessage = message.replace(/\n/g, '<br>');
        contentDiv.innerHTML = `<p>${formattedMessage}</p>`;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('system-message');
        messageDiv.innerHTML = message;
        chatMessages.appendChild(messageDiv);
    }
    
    function showMistakeFeedback(mistakes) {
        mistakeFeedback.innerHTML = '';
        
        const mistakeTitle = document.createElement('h5');
        mistakeTitle.textContent = 'Feedback on your message:';
        mistakeFeedback.appendChild(mistakeTitle);
        
        mistakes.forEach(mistake => {
            const mistakeItem = document.createElement('div');
            mistakeItem.classList.add('mistake-item');
            
            mistakeItem.innerHTML = `
                <h5>${mistake.category.charAt(0).toUpperCase() + mistake.category.slice(1)} Mistake</h5>
                <div class="mistake-text">"${mistake.mistake}"</div>
                <div class="mistake-correction">Correction: "${mistake.correction}"</div>
                <div class="mistake-explanation">${mistake.explanation}</div>
            `;
            
            mistakeFeedback.appendChild(mistakeItem);
        });
        
        mistakeFeedback.classList.add('active');
    }
    
    function displayReview(data) {
        const noMistakesMessage = document.getElementById('no-mistakes-message');
        const mistakesReview = document.getElementById('mistakes-review');
        const categoriesSummary = document.getElementById('categories-summary');
        const mistakesList = document.getElementById('mistakes-list');
        const improvementSuggestions = document.getElementById('improvement-suggestions');
        
        // Clear previous content
        categoriesSummary.innerHTML = '';
        mistakesList.innerHTML = '<h4>Mistakes Made</h4>';
        improvementSuggestions.innerHTML = '<h4>Suggestions for Improvement</h4>';
        
        if (data.no_mistakes) {
            // Show "no mistakes" message
            noMistakesMessage.style.display = 'block';
            mistakesReview.style.display = 'none';
        } else {
            // Hide "no mistakes" message
            noMistakesMessage.style.display = 'none';
            mistakesReview.style.display = 'block';
            
            // Display category summary
            for (const [category, count] of Object.entries(data.categories)) {
                const categoryItem = document.createElement('div');
                categoryItem.classList.add('category-item');
                categoryItem.innerHTML = `
                    <div class="category-count">${count}</div>
                    <div class="category-name">${category.charAt(0).toUpperCase() + category.slice(1)}</div>
                `;
                categoriesSummary.appendChild(categoryItem);
            }
            
            // Display mistakes list
            data.mistakes.forEach((mistake, index) => {
                const mistakeItem = document.createElement('div');
                mistakeItem.classList.add('review-mistake-item');
                mistakeItem.innerHTML = `
                    <h5>${index + 1}. ${mistake.category.charAt(0).toUpperCase() + mistake.category.slice(1)} Mistake</h5>
                    <div class="review-mistake-text">You said: "${mistake.mistake}"</div>
                    <div class="review-mistake-correction">Correction: "${mistake.correction}"</div>
                    <div class="review-mistake-explanation">Explanation: ${mistake.explanation}</div>
                `;
                mistakesList.appendChild(mistakeItem);
            });
            
            // Display improvement suggestions
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.classList.add('improvement-content');
            suggestionsDiv.textContent = data.suggestions;
            improvementSuggestions.appendChild(suggestionsDiv);
        }
    }
}); 