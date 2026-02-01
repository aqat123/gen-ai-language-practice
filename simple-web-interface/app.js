// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
//const API_BASE_URL = 'https://language-app-469l.onrender.com/api/v1';

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

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.innerHTML = theme === 'light'
            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>'
            : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    }
}

// Text-to-Speech for Vocabulary
function speakText(text, language) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        // Map language to speech synthesis language codes
        const languageMap = {
            'Spanish': 'es-ES',
            'French': 'fr-FR',
            'German': 'de-DE',
            'Italian': 'it-IT',
            'Portuguese': 'pt-PT',
            'Japanese': 'ja-JP',
            'Korean': 'ko-KR',
            'Chinese': 'zh-CN'
        };

        utterance.lang = languageMap[language] || 'en-US';
        utterance.rate = 0.9; // Slightly slower for learning
        utterance.pitch = 1.0;

        window.speechSynthesis.speak(utterance);
    } else {
        console.warn('Text-to-speech not supported in this browser');
    }
}

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
    // Initialize theme
    initializeTheme();

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
        // Show achievements button
        document.getElementById('achievements-toggle').classList.remove('hidden');
        // Load achievements data
        loadAchievements();
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
    // Hide achievements button
    document.getElementById('achievements-toggle').classList.add('hidden');
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
async function loadSRSStats() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/vocabulary/review-stats`,
            { headers: getAuthHeaders() }
        );

        if (response.ok) {
            const stats = await response.json();
            document.getElementById('due-count').textContent = stats.due;
            document.getElementById('learning-count').textContent = stats.learning;
            document.getElementById('mastered-count').textContent = stats.mastered;
        }
    } catch (error) {
        console.error('Failed to load SRS stats:', error);
        // Set defaults on error
        document.getElementById('due-count').textContent = '0';
        document.getElementById('learning-count').textContent = '0';
        document.getElementById('mastered-count').textContent = '0';
    }
}

async function startVocabulary() {
    showSection('vocabulary-section');
    document.getElementById('flashcard').innerHTML = '<div class="loading">Loading flashcard...</div>';
    document.getElementById('options-container').classList.add('hidden');
    document.getElementById('feedback').classList.add('hidden');

    // Load SRS stats
    await loadSRSStats();

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

        // Don't preload yet - wait until user answers to avoid showing same card twice
        // preloadNextFlashcard();

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
        <button class="audio-btn" onclick="speakText('${currentFlashcard.word.replace(/'/g, "\\'")}', '${currentUser.target_language}')" title="Listen to pronunciation">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
        </button>
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

        // Safety check: If we got the same card again (shouldn't happen with FIFO, but just in case)
        // Fetch a different one
        if (currentFlashcard && nextCardData.word === currentFlashcard.word &&
            nextCardData.definition === currentFlashcard.definition) {
            console.warn('Got same card again, fetching a new one...');
            const response = await fetch(
                `${API_BASE_URL}/vocabulary/next`,
                { headers: getAuthHeaders() }
            );
            if (response.ok) {
                nextCardData = await response.json();
                console.log('Fetched replacement card:', nextCardData.word);
            }
        }

        // Swap Data
        currentFlashcard = nextCardData;
        displayFlashcard();

        // Don't preload here - it will be preloaded after the user answers
        // preloadNextFlashcard();

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
        // Calculate quality rating for SRS reviews
        const requestBody = {
            word: currentFlashcard.word,
            selected_option_index: selectedIndex,
            correct_option_index: correctIndex
        };

        // If this is a review, include review_id and quality
        if (currentFlashcard.is_review && currentFlashcard.review_id) {
            requestBody.review_id = currentFlashcard.review_id;
            // Quality rating: 5 = perfect, 4 = correct after hesitation, 2 = incorrect
            requestBody.quality = isCorrect ? 5 : 2;
        }

        const response = await fetch(`${API_BASE_URL}/vocabulary/answer`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error('Failed to submit answer');
        }

        const result = await response.json();

        // fill feedback explanation now
        const explanationEl = feedbackDiv.querySelector('.feedback-explanation');
        if (explanationEl) {
            let explanation = result.explanation;
            // Add review indicator if it was a review
            if (currentFlashcard.is_review) {
                explanation += '<br><small style="color: #667eea; font-weight: 600;">📖 Review Card</small>';
            }
            explanationEl.innerHTML = explanation;
        }

        console.log('Explanation loaded');

        // Reload SRS stats after every flashcard (both new and review)
        // New cards get added to SRS, so Learning count should increase
        loadSRSStats();

        // Check for newly unlocked achievements
        checkForNewAchievements();

        // Now preload the next flashcard AFTER the answer has been submitted and processed
        // This ensures the database has been updated and we won't get the same card again
        // Use a longer delay to ensure database commit completes
        setTimeout(() => {
            preloadNextFlashcard();
        }, 300);

    } catch (error) {
        console.error('Error submitting answer:', error);
        showError(error.message);
    }
}

// Helper function to check for new achievements
async function checkForNewAchievements() {
    try {
        const oldData = achievementsData;
        await loadAchievements();

        // Compare to find newly unlocked
        if (oldData && achievementsData) {
            const oldUnlockedIds = new Set(oldData.unlocked.map(a => a.id));
            const newlyUnlocked = achievementsData.unlocked.filter(a => !oldUnlockedIds.has(a.id));

            // Show toasts for newly unlocked achievements
            newlyUnlocked.forEach(achievement => {
                showAchievementToast(achievement);
            });
        }
    } catch (error) {
        console.error('Error checking achievements:', error);
    }
}

// Conversation Module
function startConversation() {
    showSection('conversation-section');

    // Show topic selector
    document.getElementById('topic-selector').classList.remove('hidden');
    document.getElementById('chat-area').classList.add('hidden');
}

async function startConversationWithTopic(topic) {
    // Hide topic selector, show chat area
    document.getElementById('topic-selector').classList.add('hidden');
    document.getElementById('chat-area').classList.remove('hidden');

    // Display selected topic
    if (topic !== 'random') {
        const topicNames = {
            'travel': '✈️ Travel',
            'food': '🍽️ Food & Dining',
            'hobbies': '🎨 Hobbies',
            'work': '💼 Work & Career',
            'culture': '🎭 Culture',
            'daily_life': '🏠 Daily Life',
            'education': '📚 Education'
        };
        document.getElementById('topic-name').textContent = `Topic: ${topicNames[topic]}`;
        document.getElementById('current-topic-display').classList.remove('hidden');
    } else {
        document.getElementById('current-topic-display').classList.add('hidden');
    }

    document.getElementById('chat-container').innerHTML = '<div class="loading">Starting conversation...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/conversation/start`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ topic: topic === 'random' ? null : topic })
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

function changeTopic() {
    document.getElementById('topic-selector').classList.remove('hidden');
    document.getElementById('chat-area').classList.add('hidden');
    currentConversationId = null;
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
async function startWriting() {
    showSection('writing-section');
    document.getElementById('writing-language').textContent = currentUser.target_language || 'your target language';
    document.getElementById('writing-text').value = '';
    document.getElementById('writing-feedback').classList.add('hidden');

    // Reset loading indicator
    const loadingDiv = document.getElementById('writing-loading');
    loadingDiv.classList.add('hidden');
    loadingDiv.textContent = 'Processing your feedback';
    loadingDiv.style.color = '#333';

    // Show prompt selector
    await loadWritingPrompts();
}

async function loadWritingPrompts() {
    try {
        const response = await fetch(`${API_BASE_URL}/writing/prompts`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) throw new Error('Failed to load prompts');

        const prompts = await response.json();
        displayPromptSelector(prompts);
    } catch (error) {
        console.error('Error loading prompts:', error);
        // Fallback to default prompts (client-side)
        const fallbackPrompts = [
            {
                title: "My Daily Routine",
                prompt: "Describe your typical day. What time do you wake up? What do you eat for breakfast? What do you do in the evening?"
            },
            {
                title: "My Family",
                prompt: "Write about your family. Who are the members of your family? What do they do? What do they look like?"
            },
            {
                title: "My Favorite Food",
                prompt: "What is your favorite food? Describe it. Why do you like it? When do you usually eat it?"
            },
            {
                title: "A Memorable Trip",
                prompt: "Write about a trip you took. Where did you go? What did you see? What was the most interesting thing you did?"
            },
            {
                title: "My Hobbies",
                prompt: "What do you like to do in your free time? Do you have any hobbies? How often do you do them?"
            },
            {
                title: "My Hometown",
                prompt: "Describe your hometown or city. What is it famous for? What do you like or dislike about it?"
            },
            {
                title: "Learning Languages",
                prompt: "Why are you learning this language? What do you find easy or difficult? How do you practice?"
            },
            {
                title: "My Goals",
                prompt: "What are your goals for the future? What do you want to achieve? How will you get there?"
            }
        ];
        displayPromptSelector(fallbackPrompts);
    }
}

function displayPromptSelector(prompts) {
    const grid = document.getElementById('prompts-grid');
    grid.innerHTML = prompts.map(prompt => `
        <div class="prompt-card" onclick='selectPrompt(${JSON.stringify(prompt).replace(/'/g, "&apos;")})'>
            <h4>${prompt.title}</h4>
            <p>${prompt.prompt}</p>
        </div>
    `).join('');

    document.getElementById('writing-prompt-selector').classList.remove('hidden');
    document.getElementById('writing-input-area').classList.add('hidden');
}

function selectPrompt(prompt) {
    document.getElementById('prompt-title').textContent = prompt.title;
    document.getElementById('prompt-text').textContent = prompt.prompt;
    document.getElementById('selected-prompt-display').classList.remove('hidden');

    document.getElementById('writing-prompt-selector').classList.add('hidden');
    document.getElementById('writing-input-area').classList.remove('hidden');
}

function showPromptSelector() {
    loadWritingPrompts();
}

function writeFreeForm() {
    document.getElementById('selected-prompt-display').classList.add('hidden');
    document.getElementById('writing-prompt-selector').classList.add('hidden');
    document.getElementById('writing-input-area').classList.remove('hidden');
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

// Mascot Helper Messages
const mascotMessages = [
    "Practice daily for best results! 💪",
    "Don't forget to review your vocabulary! 📚",
    "Great job learning! Keep it up! ⭐",
    "Try the conversation module to improve speaking! 💬",
    "Consistency is key to mastering a language! 🔑",
    "Challenge yourself with harder exercises! 🚀",
    "Take breaks when needed, learning should be fun! 😊",
    "Review your progress regularly! 📊"
];

let mascotMessageIndex = 0;

// Toggle Mascot Speech Bubble
function toggleMascotMessage() {
    const bubble = document.getElementById('mascot-bubble');
    const messageEl = document.getElementById('mascot-message');

    if (!bubble || !messageEl) return;

    if (bubble.classList.contains('hidden')) {
        // Show bubble with random message
        mascotMessageIndex = Math.floor(Math.random() * mascotMessages.length);
        messageEl.textContent = mascotMessages[mascotMessageIndex];
        bubble.classList.remove('hidden');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            bubble.classList.add('hidden');
        }, 5000);
    } else {
        bubble.classList.add('hidden');
    }
}

// Initialize mascot helper
function initMascotHelper() {
    const mascot = document.getElementById('floating-mascot');
    if (mascot) {
        mascot.addEventListener('click', toggleMascotMessage);

        // Show welcome message after 2 seconds
        setTimeout(() => {
            toggleMascotMessage();
        }, 2000);
    }
}

// ============================================
// PROGRESS CHARTS FUNCTIONS
// ============================================

let activityChart = null;
let scoresChart = null;
let levelChart = null;

async function loadProgressCharts() {
    try {
        const response = await fetch(`${API_BASE_URL}/progress/charts`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            console.error('Failed to load charts data');
            return;
        }

        const data = await response.json();

        // Render each chart
        renderActivityChart(data.activity_over_time);
        renderScoresChart(data.module_scores);
        renderLevelChart(data.level_progression);

    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

function renderActivityChart(data) {
    const ctx = document.getElementById('activityChart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (activityChart) {
        activityChart.destroy();
    }

    const chartData = {
        labels: data.dates.map(d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
        datasets: [
            {
                label: 'Vocabulary',
                data: data.vocabulary,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Grammar',
                data: data.grammar,
                borderColor: '#f093fb',
                backgroundColor: 'rgba(240, 147, 251, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Writing',
                data: data.writing,
                borderColor: '#4facfe',
                backgroundColor: 'rgba(79, 172, 254, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Phonetics',
                data: data.phonetics,
                borderColor: '#43e97b',
                backgroundColor: 'rgba(67, 233, 123, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Conversation',
                data: data.conversation,
                borderColor: '#fa709a',
                backgroundColor: 'rgba(250, 112, 154, 0.1)',
                tension: 0.4,
                fill: true
            }
        ]
    };

    activityChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function renderScoresChart(data) {
    const ctx = document.getElementById('scoresChart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (scoresChart) {
        scoresChart.destroy();
    }

    if (!data.modules || data.modules.length === 0) {
        ctx.getContext('2d').font = '16px Inter';
        ctx.getContext('2d').fillText('No data yet - complete some activities!', 10, 50);
        return;
    }

    const chartData = {
        labels: data.modules,
        datasets: [{
            label: 'Score (%)',
            data: data.scores,
            backgroundColor: [
                'rgba(102, 126, 234, 0.8)',
                'rgba(240, 147, 251, 0.8)',
                'rgba(79, 172, 254, 0.8)',
                'rgba(67, 233, 123, 0.8)',
                'rgba(250, 112, 154, 0.8)'
            ],
            borderColor: [
                '#667eea',
                '#f093fb',
                '#4facfe',
                '#43e97b',
                '#fa709a'
            ],
            borderWidth: 2
        }]
    };

    scoresChart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

function renderLevelChart(data) {
    const ctx = document.getElementById('levelChart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (levelChart) {
        levelChart.destroy();
    }

    if (!data.levels || data.levels.length === 0) {
        ctx.getContext('2d').font = '16px Inter';
        ctx.getContext('2d').fillText('No level history yet', 10, 50);
        return;
    }

    const chartData = {
        labels: data.levels,
        datasets: [{
            label: 'Weighted Score',
            data: data.scores,
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.2)',
            tension: 0.4,
            fill: true,
            pointRadius: 6,
            pointBackgroundColor: '#667eea',
            pointBorderColor: '#fff',
            pointBorderWidth: 2
        }]
    };

    levelChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// ============================================
// ACHIEVEMENTS FUNCTIONS
// ============================================

let achievementsData = null;

async function loadAchievements() {
    try {
        const response = await fetch(`${API_BASE_URL}/achievements/`, {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            console.error('Failed to load achievements:', response.status);
            return;
        }

        achievementsData = await response.json();
        console.log('Achievements loaded:', achievementsData);
        console.log('Unlocked:', achievementsData.unlocked.length, 'Locked:', achievementsData.locked.length);
        updateAchievementsBadge();

    } catch (error) {
        console.error('Error loading achievements:', error);
    }
}

function updateAchievementsBadge() {
    const badge = document.getElementById('achievements-new-badge');
    if (!badge) return;

    if (achievementsData && achievementsData.new_count > 0) {
        badge.textContent = achievementsData.new_count;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function showAchievements() {
    if (!achievementsData) {
        console.log('Loading achievements...');
        loadAchievements().then(() => {
            if (achievementsData) {
                displayAchievementsModal();
            }
        });
    } else {
        displayAchievementsModal();
    }
}

function displayAchievementsModal() {
    const modal = document.getElementById('achievements-modal');
    modal.classList.remove('hidden');

    // Update counts
    document.getElementById('unlocked-count').textContent = achievementsData.unlocked.length;
    document.getElementById('locked-count').textContent = achievementsData.locked.length;

    // Display unlocked achievements
    displayAchievementsList('unlocked', achievementsData.unlocked);
    displayAchievementsList('locked', achievementsData.locked);

    // Mark achievements as viewed
    markAchievementsViewed();
}

function displayAchievementsList(type, achievements) {
    const container = document.getElementById(`${type}-achievements`);
    console.log(`Displaying ${type} achievements:`, achievements.length, 'items');

    if (achievements.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>' +
            (type === 'unlocked' ? 'Complete activities to unlock achievements!' : 'All achievements unlocked! 🎉') +
            '</p></div>';
        return;
    }

    container.innerHTML = achievements.map(ach => {
        const tierClass = `tier-${ach.tier}`;
        const cardClass = type === 'locked' ? 'achievement-card locked' : 'achievement-card';

        let content = `
            <div class="${cardClass}">
                ${ach.is_new ? '<span class="achievement-new-badge">NEW</span>' : ''}
                <span class="achievement-tier ${tierClass}">${ach.tier}</span>
                <span class="achievement-icon">${ach.icon || '🏆'}</span>
                <div class="achievement-name">${ach.name}</div>
                <div class="achievement-description">${ach.description}</div>
                <div class="achievement-xp">+${ach.xp_reward} XP</div>
        `;

        if (type === 'locked') {
            content += `
                <div class="achievement-progress">
                    <div class="progress-bar-container-small">
                        <div class="progress-bar-small" style="width: ${ach.progress}%"></div>
                    </div>
                    <div class="progress-text">${ach.progress}% Complete</div>
                </div>
            `;
        } else if (ach.unlocked_at) {
            const date = new Date(ach.unlocked_at).toLocaleDateString();
            content += `<div class="achievement-unlocked-date">Unlocked on ${date}</div>`;
        }

        content += '</div>';
        return content;
    }).join('');
}

function switchAchievementsTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.tab-btn').classList.add('active');

    // Update tab content
    document.getElementById('unlocked-tab').classList.toggle('hidden', tab !== 'unlocked');
    document.getElementById('locked-tab').classList.toggle('hidden', tab !== 'locked');
}

function closeAchievementsModal() {
    document.getElementById('achievements-modal').classList.add('hidden');
}

async function markAchievementsViewed() {
    try {
        await fetch(`${API_BASE_URL}/achievements/mark-viewed`, {
            method: 'POST',
            headers: getAuthHeaders()
        });

        // Update local data
        if (achievementsData && achievementsData.unlocked) {
            achievementsData.unlocked.forEach(ach => {
                ach.is_new = false;
            });
            achievementsData.new_count = 0;
            updateAchievementsBadge();
        }
    } catch (error) {
        console.error('Error marking achievements as viewed:', error);
    }
}

function showAchievementToast(achievement) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <div class="toast-icon">${achievement.icon || '🏆'}</div>
        <div class="toast-content">
            <div class="toast-title">Achievement Unlocked!</div>
            <div class="toast-message">${achievement.name}</div>
            <div class="toast-xp">+${achievement.xp_reward} XP</div>
        </div>
    `;

    container.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.4s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 5000);

    // Reload achievements data to update badge
    loadAchievements();
}

// Initialize app on page load (only on index.html)
window.addEventListener('DOMContentLoaded', function() {
    // Only run initializeApp on index.html (main page)
    // Other pages like progress.html have their own initialization
    const isMainPage = document.getElementById('login-section') !== null;
    if (isMainPage) {
        initializeApp();
        initMascotHelper();
        // Load achievements for badge count
        if (authToken) {
            setTimeout(loadAchievements, 1000);
        }
    }

    // Load charts on progress page
    if (window.location.pathname.includes('progress.html')) {
        // Wait a bit for the page to load progress data first
        setTimeout(loadProgressCharts, 1000);
    }
});
