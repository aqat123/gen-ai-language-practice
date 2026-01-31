// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global State
let authToken = null;
let currentUser = null;
let currentPlacementTest = null;
let currentTestQuestion = null;
let currentFlashcard = null;
let currentConversationId = null;
let currentGrammarQuestion = null;
let currentTargetPhrase = "";
let mediaRecorder = null;
let audioChunks = [];
let audioBlob = null;
let nextFlashcardPromise = null;

// Utility Functions
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

function showError(message) {
    alert('Error: ' + message);
}

// Authentication Functions
function saveAuthToken(token) {
    authToken = token;
    localStorage.setItem('authToken', token);
}

function loadAuthToken() {
    authToken = localStorage.getItem('authToken');
    return authToken;
}

function clearAuthToken() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
}

function getAuthHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
    };
}

function checkAuth() {
    const token = loadAuthToken();
    if (!token) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Password Visibility Toggle
function togglePasswordVisibility(inputId, event) {
    event.preventDefault();
    const input = document.getElementById(inputId);
    const button = event.currentTarget;
    const eyeIcon = button.querySelector('.eye-icon');
    const eyeClosedIcon = button.querySelector('.eye-closed-icon');
    
    if (input.type === 'password') {
        input.type = 'text';
        eyeIcon.classList.add('hidden');
        eyeClosedIcon.classList.remove('hidden');
    } else {
        input.type = 'password';
        eyeIcon.classList.remove('hidden');
        eyeClosedIcon.classList.add('hidden');
    }
}

// Initialize app on page load
async function initializeApp() {
    const token = loadAuthToken();
    if (token) {
        // Try to get current user
        try {
            const response = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: getAuthHeaders()
            });

            if (response.ok) {
                currentUser = await response.json();
                updateUserDisplay();

                // Route user based on their status
                if (!currentUser.target_language) {
                    showSection('language-selection-section');
                } else if (!currentUser.level && !currentUser.placement_test_completed) {
                    showSection('level-selection-section');
                } else {
                    showSection('module-section');
                }
            } else {
                // Token invalid, clear it
                clearAuthToken();
                showSection('login-section');
            }
        } catch (error) {
            console.error('Error checking auth:', error);
            clearAuthToken();
            showSection('login-section');
        }
    } else {
        showSection('login-section');
    }
}

function updateUserDisplay() {
    if (currentUser) {
        const displayText = `${currentUser.username} | ${currentUser.target_language || '?'} (${currentUser.level || '?'})`;
        document.getElementById('user-display').textContent = displayText;
        document.getElementById('user-info').classList.remove('hidden');
    }
}

function showLogin() {
    showSection('login-section');
}

function showRegister() {
    showSection('register-section');
}

function handleLoginKeyPress(event) {
    if (event.key === 'Enter') {
        loginUser();
    }
}

async function loginUser() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    console.log('Attempting login for:', username);

    if (!username || !password) {
        showError('Please enter username and password');
        return;
    }

    try {
        console.log('Sending login request...');
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        console.log('Login response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Login successful:', data);
            saveAuthToken(data.access_token);
            currentUser = data.user;
            updateUserDisplay();

            // Route user based on their status
            if (!currentUser.target_language) {
                showSection('language-selection-section');
            } else if (!currentUser.level && !currentUser.placement_test_completed) {
                showSection('level-selection-section');
            } else {
                showSection('module-section');
            }

            // Clear form
            document.getElementById('login-username').value = '';
            document.getElementById('login-password').value = '';
        } else {
            const error = await response.json();
            console.error('Login failed:', error);
            showError(error.detail || 'Invalid username or password');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Failed to login. Please try again.');
    }
}

// User Registration (New Auth System)
async function registerUser() {
    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;
    const fullName = document.getElementById('register-fullname').value.trim();

    console.log('Attempting registration for:', username);

    if (!username || !password) {
        showError('Please enter username and password');
        return;
    }

    if (username.length < 3 || username.length > 30) {
        showError('Username must be 3-30 characters');
        return;
    }

    if (password.length < 8) {
        showError('Password must be at least 8 characters');
        return;
    }

    try {
        console.log('Sending registration request...');
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                password,
                full_name: fullName || null
            })
        });

        console.log('Registration response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Registration successful:', data);
            saveAuthToken(data.access_token);
            currentUser = data.user;
            updateUserDisplay();

            // Show language selection
            showSection('language-selection-section');

            // Clear form
            document.getElementById('register-username').value = '';
            document.getElementById('register-password').value = '';
            document.getElementById('register-fullname').value = '';
        } else {
            const error = await response.json();
            console.error('Registration failed:', error);
            showError(error.detail || 'Failed to register');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showError('Failed to register. Please try again.');
    }
}

async function logoutUser() {
    clearAuthToken();
    currentFlashcard = null;
    currentConversationId = null;
    currentGrammarQuestion = null;
    currentPlacementTest = null;
    document.getElementById('user-info').classList.add('hidden');
    showSection('login-section');
}

async function selectLanguage(language) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me/language`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({ target_language: language })
        });

        if (response.ok) {
            currentUser = await response.json();
            updateUserDisplay();
            showSection('level-selection-section');
        } else if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
        } else {
            showError('Failed to update language');
        }
    } catch (error) {
        console.error('Language selection error:', error);
        showError('Failed to update language');
    }
}

async function selectLevel(level) {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me/level`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify({ level })
        });

        if (response.ok) {
            currentUser = await response.json();
            updateUserDisplay();
            showSection('module-section');
        } else if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
        } else {
            showError('Failed to update level');
        }
    } catch (error) {
        console.error('Level selection error:', error);
        showError('Failed to update level');
    }
}

// Placement Test Functions
async function startPlacementTest() {
    if (!currentUser || !currentUser.target_language) {
        showError('Please select a language first');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/placement-test/start`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ target_language: currentUser.target_language })
        });

        if (response.ok) {
            const data = await response.json();
            currentPlacementTest = {
                test_id: data.test_id,
                total_questions: data.total_questions,
                current_question: 0
            };

            showSection('placement-test-section');
            await loadNextTestQuestion();
        } else if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
        } else {
            showError('Failed to start placement test');
        }
    } catch (error) {
        console.error('Start test error:', error);
        showError('Failed to start placement test');
    }
}

async function loadNextTestQuestion() {
    console.log('loadNextTestQuestion called');

    try {
        const url = `${API_BASE_URL}/placement-test/${currentPlacementTest.test_id}/question`;
        console.log('Fetching next question from:', url);

        const response = await fetch(url, { headers: getAuthHeaders() });

        console.log('Load question response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Next question data:', data);

            currentTestQuestion = data.question;
            currentPlacementTest.current_question = data.current_question_number;
            currentPlacementTest.has_next = data.has_next;

            displayTestQuestion();
            updateTestProgress();
        } else if (response.status === 404) {
            // No more questions, complete the test
            console.log('No more questions (404), completing test');
            await completeTest();
        } else if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
        } else {
            const errorText = await response.text();
            console.error('Failed to load question:', response.status, errorText);
            showError('Failed to load question');
        }
    } catch (error) {
        console.error('Load question error:', error);
        showError('Failed to load question: ' + error.message);
    }
}

function displayTestQuestion() {
    console.log('Displaying test question:', currentTestQuestion.question_number, currentTestQuestion.question_text);

    const container = document.getElementById('test-question-container');
    const optionsContainer = document.getElementById('test-options-container');

    // Display question
    let questionHTML = '<div class="question-text">';
    if (currentTestQuestion.passage) {
        questionHTML += `<div class="reading-passage" style="background: #f5f7fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;"><em>${currentTestQuestion.passage}</em></div>`;
    }
    questionHTML += `<p style="font-size: 1.1rem; font-weight: 600;">${currentTestQuestion.question_text}</p>`;
    questionHTML += '</div>';
    container.innerHTML = questionHTML;

    // Display options
    optionsContainer.innerHTML = '';
    optionsContainer.classList.remove('hidden');

    currentTestQuestion.options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'option';
        button.textContent = option;
        button.onclick = () => {
            console.log('Test option clicked:', index);
            submitTestAnswer(index);
        };
        optionsContainer.appendChild(button);
    });

    console.log('Test question displayed with', currentTestQuestion.options.length, 'options');
}

function updateTestProgress() {
    const progressPercent = (currentPlacementTest.current_question / currentPlacementTest.total_questions) * 100;
    document.getElementById('test-progress-fill').style.width = `${progressPercent}%`;
    document.getElementById('test-progress-text').textContent =
        `Question ${currentPlacementTest.current_question} of ${currentPlacementTest.total_questions}`;
}

async function submitTestAnswer(selectedOption) {
    console.log('submitTestAnswer called with option:', selectedOption);
    console.log('Current test:', currentPlacementTest);
    console.log('Current question:', currentTestQuestion);

    try {
        const requestBody = {
            question_number: currentTestQuestion.question_number,
            selected_option: selectedOption
        };

        console.log('Submitting answer:', requestBody);

        const response = await fetch(
            `${API_BASE_URL}/placement-test/${currentPlacementTest.test_id}/answer`,
            {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(requestBody)
            }
        );

        console.log('Submit answer response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Submit answer response:', data);

            if (data.has_next) {
                // Load next question
                console.log('Loading next question...');
                await loadNextTestQuestion();
            } else {
                // Test complete
                console.log('Test complete, showing results...');
                await completeTest();
            }
        } else if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
        } else {
            const errorText = await response.text();
            console.error('Failed to submit answer:', response.status, errorText);
            showError('Failed to submit answer');
        }
    } catch (error) {
        console.error('Submit answer error:', error);
        showError('Failed to submit answer: ' + error.message);
    }
}

async function completeTest() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/placement-test/${currentPlacementTest.test_id}/complete`,
            {
                method: 'POST',
                headers: getAuthHeaders()
            }
        );

        if (response.ok) {
            const results = await response.json();
            displayTestResults(results);
        } else if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
        } else {
            showError('Failed to complete test');
        }
    } catch (error) {
        console.error('Complete test error:', error);
        showError('Failed to complete test');
    }
}

function displayTestResults(results) {
    showSection('test-results-section');

    // Display level badge
    document.getElementById('level-badge').textContent = `Your Level: ${results.determined_level}`;

    // Display section scores
    let scoresHTML = '<h3>Section Breakdown</h3>';
    results.section_scores.forEach(section => {
        scoresHTML += `
            <div class="section-score-item">
                <span class="section-score-label">${section.section}</span>
                <span class="section-score-value">${Math.round(section.score_percentage)}% (${section.correct_answers}/${section.total_questions})</span>
            </div>
        `;
    });
    document.getElementById('section-scores').innerHTML = scoresHTML;

    // Display recommendations
    let recommendationsHTML = '<h4>Recommendations</h4><ul>';
    results.recommendations.forEach(rec => {
        recommendationsHTML += `<li>${rec}</li>`;
    });
    recommendationsHTML += '</ul>';
    document.getElementById('recommendations').innerHTML = recommendationsHTML;

    // Update current user
    currentUser.level = results.determined_level;
    currentUser.placement_test_completed = true;
    updateUserDisplay();
}

function completeSetup() {
    showSection('module-section');
}

async function retakePlacementTest() {
    await startPlacementTest();
}

// User Registration (Legacy - keep for compatibility)
async function registerUserLegacy() {
    const userId = document.getElementById('user-id').value.trim();
    const language = document.getElementById('language').value;
    const level = document.getElementById('level').value;

    if (!userId) {
        showError('Please enter your name');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                external_id: userId,
                target_language: language,
                level: level
            })
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = {
                id: userId,
                language: language,
                level: level
            };

            document.getElementById('user-display').textContent =
                `${userId} | ${language} (${level})`;
            document.getElementById('user-info').classList.remove('hidden');

            showSection('module-section');
        } else if (response.status === 400) {
            currentUser = {
                id: userId,
                language: language,
                level: level
            };
            document.getElementById('user-display').textContent =
                `${userId} | ${language} (${level})`;
            document.getElementById('user-info').classList.remove('hidden');
            showSection('module-section');
        } else {
            throw new Error('Failed to register user');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Module Navigation
function backToModules() {
    showSection('module-section');
}

// Vocabulary Module
async function startVocabulary() {
    showSection('vocabulary-section');
    document.getElementById('flashcard').innerHTML = '<div class="loading">Loading flashcard...</div>';
    document.getElementById('options-container').classList.add('hidden');
    document.getElementById('feedback').classList.add('hidden');

    try {
        const response = await fetch(
            `${API_BASE_URL}/vocabulary/next`,
            { headers: getAuthHeaders() }
        );

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }
        if (!response.ok) throw new Error('Failed to load flashcard');

        currentFlashcard = await response.json();
        displayFlashcard();

        // see if you can preload the next flashcard
        preloadNextFlashcard();

    } catch (error) {
        document.getElementById('flashcard').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

function displayFlashcard() {
    console.log('Displaying flashcard:', currentFlashcard.word);

    let imageHtml = '';
    if (currentFlashcard.image_data) {
        imageHtml = `
            <div class="flashcard-image" style="margin-top: 20px; text-align: center;">
                <img
                    src="data:image/jpeg;base64,${currentFlashcard.image_data}"
                    alt="${currentFlashcard.word}"
                    style="max-width: 100%; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                >
            </div>
        `;
    }

    const flashcardHtml = `
        <div class="word">${currentFlashcard.word}</div>
        <div class="example">"${currentFlashcard.example_sentence}"</div>
        <div class="definition-label">What does this mean?</div>
        ${imageHtml}
    `;
    document.getElementById('flashcard').innerHTML = flashcardHtml;

    const optionsHtml = currentFlashcard.options.map((option, index) => `
        <div class="option" onclick="selectOption(${index})">
            ${option}
        </div>
    `).join('');

    document.getElementById('options-container').innerHTML = optionsHtml;
    document.getElementById('options-container').classList.remove('hidden');

    // Re-enable option clicks
    const options = document.querySelectorAll('.option');
    options.forEach(opt => opt.style.pointerEvents = 'auto');
}

function preloadNextFlashcard() {
    // Start the fetch request immediately and store the word
    nextFlashcardPromise = fetch(
        `${API_BASE_URL}/vocabulary/next`,
        { headers: getAuthHeaders() }
    )
    .then(response => {
        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return null;
        }
        if (!response.ok) throw new Error('Failed to load flashcard');
        return response.json();
    })
    .catch(error => {
        console.error("Preload error:", error);
        return null;
    });
}

async function loadNextWord() {
    console.log('loadNextWord() called');

    // Reset UI state
    document.getElementById('options-container').classList.add('hidden');
    document.getElementById('feedback').classList.add('hidden');
    document.getElementById('flashcard').innerHTML = '<div class="loading">Loading next word...</div>';

    try {
        let nextCardData = null;

        // Check if we have a pre-loaded word
        if (nextFlashcardPromise) {
            console.log('Using pre-loaded flashcard');
            // Wait for the pre-load to finish
            nextCardData = await nextFlashcardPromise;
            // Reset the promise after consuming it
            nextFlashcardPromise = null;
        }

        // If pre-load failed or didn't exist, fetch normally
        if (!nextCardData) {
            console.log('Fetching new flashcard');
            const response = await fetch(
                `${API_BASE_URL}/vocabulary/next`,
                { headers: getAuthHeaders() }
            );
            if (response.status === 401) {
                showError('Session expired. Please login again.');
                logoutUser();
                return;
            }
            if (!response.ok) {
                throw new Error('Failed to load next flashcard');
            }
            nextCardData = await response.json();
        }

        console.log('Next flashcard loaded:', nextCardData.word);

        // Swap Data
        currentFlashcard = nextCardData;
        displayFlashcard();

        // Trigger the next pre-fetch too for max efficiency
        preloadNextFlashcard();

    } catch (error) {
        console.error('Error loading next word:', error);
        document.getElementById('flashcard').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

async function selectOption(selectedIndex) {
    console.log('Option selected:', selectedIndex);

    const options = document.querySelectorAll('.option');
    const correctIndex = currentFlashcard.correct_option_index;

    options.forEach(opt => opt.style.pointerEvents = 'none');

    // allow correctness check immediately
    const isCorrect = (selectedIndex === correctIndex);

    options[selectedIndex].classList.add('selected');
    options[correctIndex].classList.add('correct');

    if (selectedIndex !== correctIndex) {
        options[selectedIndex].classList.add('incorrect');
    }

    // Show the Feedback placeholder before the api call
    const feedbackDiv = document.getElementById('feedback');
    feedbackDiv.className = 'feedback ' + (isCorrect ? 'correct' : 'incorrect');
    feedbackDiv.innerHTML = `
        <div class="feedback-text">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</div>
        <div class="feedback-explanation">
            <em>Loading explanation...</em>
        </div>
        <button onclick="loadNextWord()" class="btn btn-primary" style="margin-top: 15px;">Next Word</button>
    `;
    feedbackDiv.classList.remove('hidden');

    console.log('Feedback displayed, Next Word button added');

    try {
        const response = await fetch(`${API_BASE_URL}/vocabulary/answer`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                word: currentFlashcard.word,
                selected_option_index: selectedIndex,
                correct_option_index: correctIndex
            })
        });

        if (!response.ok) {
            throw new Error('Failed to submit answer');
        }

        const result = await response.json();

        // fill feedback explanation now
        const explanationEl = feedbackDiv.querySelector('.feedback-explanation');
        if (explanationEl) {
            explanationEl.innerHTML = result.explanation;
        }

        console.log('Explanation loaded');

    } catch (error) {
        console.error('Error submitting answer:', error);
        showError(error.message);
    }
}

// Conversation Module
async function startConversation() {
    showSection('conversation-section');
    document.getElementById('chat-container').innerHTML = '<div class="loading">Starting conversation...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/conversation/start`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ topic: null })
        });

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }
        if (!response.ok) throw new Error('Failed to start conversation');

        const data = await response.json();
        currentConversationId = data.session_id;

        document.getElementById('chat-container').innerHTML = `
            <div class="chat-message ai">${data.opening_message}</div>
        `;
    } catch (error) {
        document.getElementById('chat-container').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// TODO: add a loading indicator when waiting for AI response
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML += `<div class="chat-message user">${message}</div>`;
    input.value = '';

    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const response = await fetch(
            `${API_BASE_URL}/conversation/${currentConversationId}/message`,
            {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ message: message })
            }
        );

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }
        if (!response.ok) throw new Error('Failed to send message');

        const data = await response.json();

        chatContainer.innerHTML += `<div class="chat-message ai">${data.reply}</div>`;

        // start of change
        const hasCorrection = data.corrected_user_message && data.corrected_user_message !== message && data.corrected_user_message !== "null";
        const hasTips = data.tips && data.tips !== "null";

        if (hasCorrection || hasTips) {
            let feedbackHtml = `
                <div class="chat-message ai" style="background: #fff3e0; font-size: 0.9rem; border-left: 4px solid #ffca28; color: #5d4037;">
            `;

            if (hasCorrection) {
                feedbackHtml += `<div style="margin-bottom: 6px;"><strong>💡 Correction:</strong> "${data.corrected_user_message}"</div>`;
            }

            if (hasTips) {
                feedbackHtml += `<div style="font-style: italic; font-size: 0.85rem; color: #795548;">👉 ${data.tips}</div>`;
            }

            feedbackHtml += `</div>`;
            chatContainer.innerHTML += feedbackHtml;
        }
        // end of change

        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
        showError(error.message);
    }
}

// Grammar Module
async function startGrammar() {
    showSection('grammar-section');
    document.getElementById('grammar-question').innerHTML = '<div class="loading">Loading question...</div>';
    document.getElementById('grammar-options').classList.add('hidden');
    document.getElementById('grammar-feedback').classList.add('hidden');

    try {
        const response = await fetch(
            `${API_BASE_URL}/grammar/question?topic=general`,
            { headers: getAuthHeaders() }
        );

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }
        if (!response.ok) throw new Error('Failed to load grammar question');

        currentGrammarQuestion = await response.json();
        displayGrammarQuestion();
    } catch (error) {
        document.getElementById('grammar-question').innerHTML =
            `<div class="loading">Error: ${error.message}</div>`;
    }
}

function displayGrammarQuestion() {
    document.getElementById('grammar-question').innerHTML = `
        <div style="font-size: 1.5rem; margin-bottom: 20px;">${currentGrammarQuestion.question_text}</div>
    `;

    const optionsHtml = currentGrammarQuestion.options.map((option, index) => `
        <div class="option" onclick="selectGrammarOption(${index})">
            ${option}
        </div>
    `).join('');

    document.getElementById('grammar-options').innerHTML = optionsHtml;
    document.getElementById('grammar-options').classList.remove('hidden');
}

async function selectGrammarOption(selectedIndex) {
    const options = document.querySelectorAll('#grammar-options .option');
    const correctIndex = currentGrammarQuestion.correct_option_index;

    options.forEach(opt => opt.style.pointerEvents = 'none');

    options[selectedIndex].classList.add('selected');
    options[correctIndex].classList.add('correct');

    if (selectedIndex !== correctIndex) {
        options[selectedIndex].classList.add('incorrect');
    }

    const feedbackDiv = document.getElementById('grammar-feedback');
    const isCorrect = selectedIndex === correctIndex;
    feedbackDiv.className = 'feedback ' + (isCorrect ? 'correct' : 'incorrect');
    feedbackDiv.innerHTML = `
        <div class="feedback-text">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</div>
        <div class="feedback-explanation">${currentGrammarQuestion.explanation}</div>
        <button onclick="startGrammar()" class="btn btn-primary" style="margin-top: 15px;">Next Question</button>
    `;
    feedbackDiv.classList.remove('hidden');

    // Submit answer to backend to track progress
    try {
        await fetch(`${API_BASE_URL}/grammar/answer`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                question_id: currentGrammarQuestion.question_id,
                selected_option_index: selectedIndex,
                correct_option_index: correctIndex,
                explanation: currentGrammarQuestion.explanation
            })
        });
    } catch (error) {
        console.error('Error submitting grammar answer:', error);
        // Don't show error to user - progress tracking failure shouldn't interrupt UX
    }
}

// Writing Module
// TODO: add loading indicators, currently you have no idea if something is happening after you click submit
function startWriting() {
    showSection('writing-section');
    document.getElementById('writing-language').textContent = currentUser.target_language || 'your target language';
    document.getElementById('writing-text').value = '';
    document.getElementById('writing-feedback').classList.add('hidden');
    // Reset loading indicator
    const loadingDiv = document.getElementById('writing-loading');
    loadingDiv.classList.add('hidden');
    loadingDiv.textContent = 'Processing your feedback';
    loadingDiv.style.color = '#333';
}

async function submitWriting() {
    const text = document.getElementById('writing-text').value.trim();

    if (!text) {
        showError('Please write something first');
        return;
    }

    // Show loading indicator and disable button
    const loadingDiv = document.getElementById('writing-loading');
    const submitBtn = document.getElementById('submit-writing-btn');
    const feedbackDiv = document.getElementById('writing-feedback');
    
    loadingDiv.classList.remove('hidden');
    loadingDiv.textContent = 'Processing your feedback';
    submitBtn.disabled = true;
    feedbackDiv.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/writing/feedback`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ text: text })
        });

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }
        if (!response.ok) {
            // Display error in loading div instead of popup for rate limit errors
            loadingDiv.textContent = 'Error: Processing your feedback';
            loadingDiv.style.color = '#333';
            return;
        }

        const data = await response.json();

        feedbackDiv.innerHTML = `
            <div class="corrected-text">
                <h3>✅ Corrected Text:</h3>
                <p style="font-size: 1.2rem; margin-top: 10px;">${data.corrected_text}</p>
            </div>
            <div class="feedback-comment">
                <h3>💬 Feedback:</h3>
                <p style="margin-top: 10px;">${data.overall_comment}</p>
                ${data.inline_explanation ? `<p style="margin-top: 10px; font-size: 0.9rem; color: #666;">${data.inline_explanation}</p>` : ''}
            </div>
            ${data.score ? `<div class="score">Score: ${data.score}%</div>` : ''}
            <button onclick="startWriting()" class="btn btn-primary">Try Another</button>
        `;
        feedbackDiv.classList.remove('hidden');
        loadingDiv.classList.add('hidden');
    } catch (error) {
        // Display error in loading div instead of popup
        loadingDiv.textContent = 'Error: Processing your feedback';
        loadingDiv.style.color = '#333';
    } finally {
        // Re-enable button
        submitBtn.disabled = false;
    }
}

// Phonetics Module
async function startPhonetics() {
    showSection('phonetics-section');

    // Reset UI
    document.getElementById('target-phrase').innerHTML = '<div class="loading">Generating phrase...</div>';
    document.getElementById('phonetics-feedback').classList.add('hidden');
    document.getElementById('validate-btn').disabled = true;
    document.getElementById('audio-preview').style.display = 'none';
    document.getElementById('record-status').textContent = "Tap to Record";
    document.getElementById('record-btn').style.backgroundColor = "#e74c3c"; // Red
    document.getElementById('record-btn').innerHTML = "🎙️";

    // Reset Audio State
    audioBlob = null;
    audioChunks = [];

    try {
        // Fetch new phrase from Backend
        const response = await fetch(
            `${API_BASE_URL}/phonetics/phrase`,
            { headers: getAuthHeaders() }
        );

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }
        if (!response.ok) throw new Error('Failed to load phrase');

        const data = await response.json();
        currentTargetPhrase = data.target_phrase;

        document.getElementById('target-phrase').textContent = currentTargetPhrase;

    } catch (error) {
        document.getElementById('target-phrase').innerHTML = `<div style="color:red">Error: ${error.message}</div>`;
    }
}

// Recording Audio
async function toggleRecording() {
    const recordBtn = document.getElementById('record-btn');
    const statusText = document.getElementById('record-status');

    // If already recording, STOP it
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.style.backgroundColor = "#e74c3c"; // Back to Red
        recordBtn.innerHTML = "🎙️";
        statusText.textContent = "Recording saved. Ready to validate.";
        return;
    }

    // START Recording
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            // Create Blob when stopped
            audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

            // Enable Validate Button
            document.getElementById('validate-btn').disabled = false;

            // Show Preview Player
            const audioUrl = URL.createObjectURL(audioBlob);
            const audioPreview = document.getElementById('audio-preview');
            audioPreview.src = audioUrl;
            audioPreview.style.display = 'block';
        };

        mediaRecorder.start();
        recordBtn.style.backgroundColor = "#f1c40f"; // Yellow/Orange for active recording
        recordBtn.innerHTML = "⏹️"; // Stop icon
        statusText.textContent = "Recording... Tap to stop";

    } catch (err) {
        showError("Microphone access denied: " + err.message);
    }
}

// Validate Pronunciation
async function validatePronunciation() {
    if (!audioBlob) {
        showError("Please record something first!");
        return;
    }

    const validateBtn = document.getElementById('validate-btn');
    validateBtn.disabled = true;
    validateBtn.textContent = "Analyzing...";

    // Prepare Form Data
    const formData = new FormData();
    formData.append("target_phrase", currentTargetPhrase);
    // Send file with correct extension
    formData.append("audio_file", audioBlob, "recording.webm");

    try {
        const response = await fetch(`${API_BASE_URL}/phonetics/evaluate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData // No Content-Type header needed (browser sets it for FormData)
        });

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }
        if (!response.ok) throw new Error('Analysis failed');

        const result = await response.json();
        displayPhoneticsFeedback(result);

    } catch (error) {
        showError(error.message);
    } finally {
        validateBtn.disabled = false;
        validateBtn.textContent = "Validate Pronunciation";
    }
}

// Display the feedback
function displayPhoneticsFeedback(result) {
    const feedbackContainer = document.getElementById('phonetics-feedback');
    const mainFeedback = document.getElementById('phonetics-main-feedback');
    const wordFeedback = document.getElementById('phonetics-word-feedback');

    // 1. Main Feedback (Score & General)
    const isGood = result.score > 70;
    mainFeedback.className = 'feedback ' + (isGood ? 'correct' : 'incorrect');
    mainFeedback.innerHTML = `
        <div class="feedback-text">Score: ${result.score}/100</div>
        <div class="feedback-explanation">
            <strong>Heard:</strong> "${result.transcript}"<br><br>
            ${result.feedback}
        </div>
    `;

    // 2. Word-Level Feedback (Yellow Bubbles)
    let wordHtml = '';
    if (result.word_level_feedback && result.word_level_feedback.length > 0) {
        wordHtml += `<div style="margin-top: 15px; font-weight: bold; color: #555;">Specific Issues:</div>`;

        result.word_level_feedback.forEach(issue => {
            wordHtml += `
                <div style="background: #fff3e0; border-left: 4px solid #ffca28; padding: 10px; margin-top: 10px; border-radius: 4px; color: #5d4037;">
                    <div><strong>Word:</strong> "${issue.word}"</div>
                    <div><strong>Issue:</strong> ${issue.issue}</div>
                    <div style="font-style: italic; font-size: 0.9rem; margin-top: 4px;">👉 Tip: ${issue.tip}</div>
                </div>
            `;
        });
    } else if (result.score < 100) {
         wordHtml = `<div style="margin-top: 10px; color: #666; font-style: italic;">No specific word errors detected. Work on overall flow!</div>`;
    }

    wordFeedback.innerHTML = wordHtml;
    feedbackContainer.classList.remove('hidden');
}

// ============================================
// PROGRESS TRACKING & LEVEL ADVANCEMENT
// ============================================

async function loadProgressDashboard() {
    console.log('[Progress] Starting to load dashboard...');
    try {
        console.log('[Progress] Fetching from:', `${API_BASE_URL}/progress/summary`);
        console.log('[Progress] Auth headers:', getAuthHeaders());

        const response = await fetch(`${API_BASE_URL}/progress/summary`, {
            headers: getAuthHeaders()
        });

        console.log('[Progress] Response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Progress] API error:', response.status, errorText);
            showError(`Failed to load progress data (HTTP ${response.status})`);
            return;
        }

        const data = await response.json();
        console.log('[Progress] Data loaded successfully:', data);

        // Display the data - catch any display errors separately
        try {
            displayProgressSummary(data);
            console.log('[Progress] Summary displayed successfully');
        } catch (displayError) {
            console.error('[Progress] Display error (data was loaded):', displayError);
            console.error('[Progress] Stack:', displayError.stack);
            // Don't show alert - data was received, just some UI elements might be missing
        }
    } catch (error) {
        console.error('[Progress] Fatal error:', error);
        console.error('[Progress] Stack:', error.stack);
        showError('Failed to load progress data: ' + error.message);
    }
}

function displayProgressSummary(data) {
    // Update header stats
    const levelBadge = document.getElementById('current-level-badge');
    const timeAtLevel = document.getElementById('time-at-level');
    const totalXp = document.getElementById('total-xp');

    if (levelBadge) levelBadge.textContent = data.current_level;
    if (timeAtLevel) timeAtLevel.textContent = `${data.time_at_current_level} days`;
    if (totalXp) totalXp.textContent = `${data.total_xp} XP`;

    // Show/hide advancement banner
    const banner = document.getElementById('advancement-banner');
    if (banner) {
        if (data.can_advance && data.next_level) {
            banner.classList.remove('hidden');
            const nextLevelText = document.getElementById('next-level-text');
            if (nextLevelText) nextLevelText.textContent = data.next_level;
        } else {
            banner.classList.add('hidden');
        }
    }

    // Update overall progress
    const overallProgress = Math.min(data.overall_progress, 100);
    const progressBar = document.getElementById('overall-progress-bar');
    const percentage = document.getElementById('overall-percentage');

    if (progressBar) progressBar.style.width = `${overallProgress}%`;
    if (percentage) percentage.textContent = `${Math.round(overallProgress)}%`;

    // Update advancement status
    const statusElement = document.getElementById('advancement-status');
    if (statusElement) {
        if (data.can_advance) {
            statusElement.textContent = '✓ Ready to advance!';
            statusElement.style.color = '#10b981';
        } else if (data.advancement_reason) {
            statusElement.textContent = data.advancement_reason;
            statusElement.style.color = '#f59e0b';
        }
    }

    // Update module cards
    if (data.modules && Array.isArray(data.modules)) {
        data.modules.forEach(module => {
            updateModuleCard(module);
        });
    }

    // Update conversation engagement
    if (data.conversation_engagement) {
        updateConversationCard(data.conversation_engagement);
    }
}

function updateModuleCard(module) {
    const card = document.querySelector(`.module-card[data-module="${module.module}"]`);
    if (!card) return;

    const score = module.score || 0;
    const totalAttempts = module.total_attempts || 0;
    const minimumAttempts = 10;

    // Calculate completion progress (attempts toward minimum 10)
    const completionProgress = Math.min((totalAttempts / minimumAttempts) * 100, 100);

    const progressBar = card.querySelector('.progress-bar');
    const percentage = card.querySelector('.percentage');
    const statusBadge = card.querySelector('.status-badge');
    const statsContainer = card.querySelector('.module-stats');
    const statusMessage = card.querySelector('.status-message');

    // Guard against missing elements
    if (!progressBar || !percentage || !statusBadge || !statsContainer || !statusMessage) {
        console.warn(`Missing DOM elements in module card for ${module.module}`);
        return;
    }

    // Update progress bar to show completion progress (not accuracy)
    progressBar.style.width = `${completionProgress}%`;
    percentage.textContent = `${totalAttempts}/${minimumAttempts}`;

    // Update stats - show both attempts and accuracy
    if (module.module === 'vocabulary' || module.module === 'grammar') {
        statsContainer.innerHTML = `
            <span class="attempts">${module.total_attempts} attempts</span>
            <span class="correct">Accuracy: ${Math.round(score)}%</span>
        `;
    } else {
        statsContainer.innerHTML = `
            <span class="attempts">${module.total_attempts} attempts</span>
            <span class="score-avg">Score: ${Math.round(score)}%</span>
        `;
    }

    // Update status badge
    if (module.meets_threshold && module.meets_minimum_attempts) {
        statusBadge.textContent = '✓ Ready';
        statusBadge.className = 'status-badge status-ready';
        statusMessage.textContent = 'Ready to advance!';
        statusMessage.style.color = '#10b981';
    } else {
        statusBadge.textContent = 'Not Ready';
        statusBadge.className = 'status-badge status-pending';

        if (!module.meets_minimum_attempts) {
            statusMessage.textContent = `Need ${10 - module.total_attempts} more attempts`;
        } else if (!module.meets_threshold) {
            statusMessage.textContent = `Need ${Math.round(85 - score)}% more`;
        } else {
            statusMessage.textContent = 'Keep practicing!';
        }
        statusMessage.style.color = '#f59e0b';
    }
}

function updateConversationCard(engagement) {
    const card = document.querySelector('.module-card[data-module="conversation"]');
    if (!card) return;

    const countValue = card.querySelector('.count-value');
    const progressBar = card.querySelector('.progress-bar');
    const percentage = card.querySelector('.percentage');
    const statusBadge = card.querySelector('.status-badge');
    const statusMessage = card.querySelector('.status-message');

    // Guard against missing elements
    if (!countValue || !progressBar || !percentage || !statusBadge || !statusMessage) {
        console.warn('Missing DOM elements in conversation card');
        return;
    }

    countValue.textContent = engagement.total_messages;

    const progressPercent = Math.min((engagement.total_messages / 20) * 100, 100);
    progressBar.style.width = `${progressPercent}%`;
    percentage.textContent = `${engagement.total_messages}/20`;

    if (engagement.meets_threshold) {
        statusBadge.textContent = '✓ Ready';
        statusBadge.className = 'status-badge status-ready';
        statusMessage.textContent = 'Ready to advance!';
        statusMessage.style.color = '#10b981';
    } else {
        statusBadge.textContent = 'Not Ready';
        statusBadge.className = 'status-badge status-pending';
        statusMessage.textContent = `Need ${20 - engagement.total_messages} more messages`;
        statusMessage.style.color = '#f59e0b';
    }
}

async function triggerLevelAdvancement() {
    if (!confirm('Are you ready to advance to the next level? Your progress will be archived and reset.')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/progress/advance`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to advance level');
        }

        const result = await response.json();
        showCelebrationModal(result);
    } catch (error) {
        console.error('Error advancing level:', error);
        showError(error.message);
    }
}

function showCelebrationModal(result) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('celebration-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'celebration-modal';
        modal.className = 'modal';
        document.body.appendChild(modal);
    }

    modal.innerHTML = `
        <div class="modal-content celebration">
            <div class="confetti-container"></div>
            <h2>🎉 CONGRATULATIONS! 🎉</h2>
            <div class="level-transition">
                <span class="level-badge">${result.old_level}</span>
                <span class="arrow">→</span>
                <span class="level-badge highlight">${result.new_level}</span>
            </div>
            <div class="achievement-summary">
                <h3>Your Achievement Summary</h3>
                <div class="scores-grid">
                    ${Object.entries(result.module_scores).map(([module, score]) => `
                        <div class="score-item">
                            <span class="module-name">${module}</span>
                            <span class="score-value">${score ? Math.round(score) + '%' : 'N/A'}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="xp-earned">+${result.xp_earned} XP</div>
            </div>
            <p class="celebration-message">${result.celebration_message}</p>
            <button onclick="closeAdvancementModal()" class="btn btn-primary btn-large">
                Start Learning at ${result.new_level}
            </button>
        </div>
    `;

    modal.classList.remove('hidden');
    modal.style.display = 'flex';

    // Add confetti animation
    createConfetti();
}

function createConfetti() {
    const container = document.querySelector('.confetti-container');
    if (!container) return;

    const colors = ['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444'];

    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 3 + 's';
        confetti.style.animationDuration = Math.random() * 3 + 2 + 's';
        container.appendChild(confetti);
    }
}

function closeAdvancementModal() {
    const modal = document.getElementById('celebration-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    }
    // Reload progress dashboard
    loadProgressDashboard();
    loadLevelHistory();
}

async function loadLevelHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/progress/history`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to load level history');
        }

        const history = await response.json();
        displayHistoryTimeline(history);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistoryTimeline(history) {
    const container = document.getElementById('level-history-container');
    if (!container) return;

    if (!history || history.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No completed levels yet. Keep practicing to advance!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="timeline">
            ${history.map((item, index) => `
                <div class="timeline-item">
                    <div class="timeline-marker">${index + 1}</div>
                    <div class="timeline-content">
                        <div class="timeline-header">
                            <span class="level-badge">${item.level}</span>
                            <span class="days-spent">${item.days_at_level} days</span>
                        </div>
                        <div class="timeline-dates">
                            ${new Date(item.started_at).toLocaleDateString()} -
                            ${new Date(item.completed_at).toLocaleDateString()}
                        </div>
                        <div class="timeline-scores">
                            <span>Weighted Score: ${Math.round(item.weighted_score)}%</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

async function checkAdvancementEligibility() {
    // Called after each module activity to update banner if newly eligible
    try {
        const response = await fetch(`${API_BASE_URL}/progress/summary`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) return;

        const data = await response.json();

        // If on progress page, update display
        if (window.location.pathname.includes('progress.html')) {
            displayProgressSummary(data);
        }

        // Show notification if newly eligible
        if (data.can_advance && data.next_level) {
            // Could show a toast notification here
            console.log('User is now eligible to advance!');
        }
    } catch (error) {
        console.error('Error checking advancement:', error);
    }
}

// ============================================
// CHEAT CODE FOR DEMO
// ============================================

function toggleCheatCode() {
    const container = document.getElementById('cheat-code-container');
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
    } else {
        container.classList.add('hidden');
    }
}

async function applyCheatCode() {
    const code = document.getElementById('cheat-code-input').value.trim();
    const feedback = document.getElementById('cheat-code-feedback');

    if (!code) {
        feedback.style.color = '#e74c3c';
        feedback.textContent = 'Please enter a code';
        return;
    }

    feedback.style.color = '#666';
    feedback.textContent = 'Applying code...';

    try {
        const response = await fetch(`${API_BASE_URL}/progress/cheat-code`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ code: code })
        });

        if (response.status === 401) {
            showError('Session expired. Please login again.');
            logoutUser();
            return;
        }

        if (response.ok) {
            const data = await response.json();
            feedback.style.color = '#10b981';
            feedback.textContent = '✅ ' + data.message;
            document.getElementById('cheat-code-input').value = '';

            // Show celebration after a short delay
            setTimeout(() => {
                alert('🎉 Demo mode activated! All progress set to 95%. Check "My Progress" to advance to the next level!');
            }, 500);
        } else {
            const error = await response.json();
            feedback.style.color = '#e74c3c';
            feedback.textContent = '❌ ' + (error.detail || 'Invalid code');
        }
    } catch (error) {
        console.error('Error applying cheat code:', error);
        feedback.style.color = '#e74c3c';
        feedback.textContent = '❌ Failed to apply code';
    }
}

// Initialize app on page load (only on index.html)
window.addEventListener('DOMContentLoaded', function() {
    // Only run initializeApp on index.html (main page)
    // Other pages like progress.html have their own initialization
    const isMainPage = document.getElementById('login-section') !== null;
    if (isMainPage) {
        initializeApp();
    }
});
