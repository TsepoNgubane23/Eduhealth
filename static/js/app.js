// EduHealth Frontend JavaScript
class EduHealthApp {
    constructor() {
        this.apiBase = '/api';
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
    }

    setupEventListeners() {
        // Modal functionality
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });

        // Form submissions
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }
        
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Dashboard interactions
        this.setupDashboardListeners();
    }

    setupDashboardListeners() {
        // AI Chat functionality
        const chatInput = document.querySelector('#ai-assistant-tab input[type="text"]');
        const sendButton = document.querySelector('#ai-assistant-tab .btn-primary');
        
        if (chatInput && sendButton) {
            sendButton.addEventListener('click', () => this.sendAIMessage());
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendAIMessage();
                }
            });
        }

        // Wellness logging
        const wellnessButton = document.querySelector('#wellness-tab .btn-success');
        if (wellnessButton) {
            wellnessButton.addEventListener('click', () => this.openWellnessModal());
        }
    }

    async checkAuthStatus() {
        try {
            const response = await fetch(`${this.apiBase}/user/profile`);
            if (response.ok) {
                this.currentUser = await response.json();
                this.updateUIForLoggedInUser();
            }
        } catch (error) {
            console.log('User not authenticated');
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch(`${this.apiBase}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.get('email') || document.getElementById('loginEmail').value,
                    password: formData.get('password') || document.getElementById('loginPassword').value
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.currentUser = data.user;
                this.closeModal('loginModal');
                this.updateUIForLoggedInUser();
                this.showNotification('Login successful!', 'success');
                this.loadDashboardData();
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Login failed. Please try again.', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('registerConfirmPassword').value;
        
        if (password !== confirmPassword) {
            this.showNotification('Passwords do not match', 'error');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: document.getElementById('registerName').value,
                    email: document.getElementById('registerEmail').value,
                    password: password
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.closeModal('registerModal');
                this.showNotification('Registration successful! Welcome to EduHealth!', 'success');
                this.checkAuthStatus();
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Registration failed. Please try again.', 'error');
        }
    }

    async loadDashboardData() {
        if (!this.currentUser) return;

        try {
            // Load learning progress
            const progressResponse = await fetch(`${this.apiBase}/progress`);
            if (progressResponse.ok) {
                const progressData = await progressResponse.json();
                this.updateLearningTab(progressData);
            }

            // Load wellness summary
            const wellnessResponse = await fetch(`${this.apiBase}/wellness/summary`);
            if (wellnessResponse.ok) {
                const wellnessData = await wellnessResponse.json();
                this.updateWellnessTab(wellnessData);
            }

            // Load AI recommendations for premium users
            if (this.currentUser.subscription_type === 'premium') {
                const aiResponse = await fetch(`${this.apiBase}/ai/recommendations`);
                if (aiResponse.ok) {
                    const aiData = await aiResponse.json();
                    this.updateAIRecommendations(aiData);
                }
            }
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    updateLearningTab(progressData) {
        const learningTab = document.getElementById('learning-tab');
        if (!learningTab || !progressData.length) return;

        const progressContainer = learningTab.querySelector('.progress-container').parentNode;
        progressContainer.innerHTML = '<h3>Your Learning Progress</h3>';

        progressData.forEach(progress => {
            const progressDiv = document.createElement('div');
            progressDiv.className = 'progress-container';
            progressDiv.innerHTML = `
                <p>${progress.course_title}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress.progress_percentage}%"></div>
                </div>
                <p>${Math.round(progress.progress_percentage)}% Complete</p>
            `;
            progressContainer.appendChild(progressDiv);
        });

        const continueBtn = document.createElement('a');
        continueBtn.href = '#';
        continueBtn.className = 'btn btn-primary';
        continueBtn.textContent = 'Continue Learning';
        progressContainer.appendChild(continueBtn);
    }

    updateWellnessTab(wellnessData) {
        const wellnessTab = document.getElementById('wellness-tab');
        if (!wellnessTab) return;

        const summaryDiv = document.createElement('div');
        summaryDiv.innerHTML = `
            <h4>This Week's Summary</h4>
            <p>${wellnessData.week_summary}</p>
            <p>Total Activities: ${wellnessData.total_activities}</p>
            <p>Total Minutes: ${wellnessData.total_minutes}</p>
        `;
        
        const wellnessGrid = wellnessTab.querySelector('.wellness-grid');
        if (wellnessGrid) {
            wellnessGrid.parentNode.insertBefore(summaryDiv, wellnessGrid);
        }
    }

    async sendAIMessage() {
        const input = document.querySelector('#ai-assistant-tab input[type="text"]');
        const message = input.value.trim();
        
        if (!message) return;

        // Show typing indicator
        this.addChatMessage('Thinking...', 'ai-typing');

        try {
            const response = await fetch(`${this.apiBase}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Remove typing indicator
            const typingMessage = document.querySelector('.ai-typing');
            if (typingMessage) {
                typingMessage.remove();
            }
            
            if (response.ok) {
                this.addChatMessage(message, 'user');
                this.addChatMessage(data.response, 'ai');
                input.value = '';
                
                // Show interaction type badge
                if (data.interaction_type !== 'general') {
                    this.showNotification(`AI detected: ${data.interaction_type} query`, 'info');
                }
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            // Remove typing indicator on error
            const typingMessage = document.querySelector('.ai-typing');
            if (typingMessage) {
                typingMessage.remove();
            }
            this.showNotification('Failed to send message', 'error');
        }
    }

    addChatMessage(message, sender) {
        const chatContainer = document.querySelector('.chat-container');
        if (!chatContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        
        if (sender === 'ai-typing') {
            messageDiv.innerHTML = `<p><i class="fas fa-spinner fa-spin"></i> ${message}</p>`;
        } else {
            messageDiv.innerHTML = `<p>${message}</p>`;
        }
        
        const inputGroup = chatContainer.querySelector('.form-group');
        chatContainer.insertBefore(messageDiv, inputGroup);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async processPayment() {
        const planType = document.getElementById('planSelect').value;
        
        try {
            const response = await fetch('/api/payment/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    plan_type: planType,
                    callback_url: window.location.origin + '/payment/success'
                })
            });
            
            const data = await response.json();
            
            if (data.status && data.data && data.data.authorization_url) {
                // Redirect to Paystack payment page
                window.location.href = data.data.authorization_url;
            } else {
                this.showNotification('Payment initialization failed: ' + (data.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Payment error:', error);
            this.showNotification('Payment initialization failed', 'error');
        }
    }

    async verifyPayment(reference) {
        try {
            const response = await fetch(`${this.apiBase}/payment/verify/${reference}`);
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Payment successful! Welcome to Premium!', 'success');
                this.currentUser.subscription_type = 'premium';
                this.updateUIForLoggedInUser();
                this.loadDashboardData();
            } else {
                this.showNotification(data.error || 'Payment verification failed', 'error');
            }
        } catch (error) {
            this.showNotification('Payment verification failed', 'error');
        }
    }

    updateUIForLoggedInUser() {
        // Update navigation
        const navLinks = document.querySelector('.nav-links');
        const signUpBtn = document.querySelector('.btn-outline');
        
        if (navLinks && signUpBtn) {
            const premiumFeatures = this.currentUser.subscription_type === 'premium' ? 
                '<li><a href="#" onclick="app.showAIFeatures()">AI Features</a></li>' : '';
            
            navLinks.innerHTML = `
                <li><a href="#features">Features</a></li>
                <li><a href="#dashboard">Dashboard</a></li>
                <li><a href="#pricing">Pricing</a></li>
                ${premiumFeatures}
                <li><span style="color: white;">Welcome, ${this.currentUser.name}!</span></li>
            `;
            
            signUpBtn.textContent = 'Logout';
            signUpBtn.onclick = () => this.logout();
        }

        // Show premium badge if applicable
        if (this.currentUser.subscription_type === 'premium') {
            this.addPremiumBadge();
        }
    }

    showAIFeatures() {
        // Create AI features modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'aiFeaturesModal';
        modal.style.display = 'flex';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <span class="close-modal" onclick="app.closeModal('aiFeaturesModal')">&times;</span>
                <h2>🤖 AI-Powered Features</h2>
                <div style="margin: 20px 0;">
                    <h3>📚 Personalized Study Plan</h3>
                    <p>Get a custom study plan based on your goals and available time.</p>
                    <button class="btn btn-primary" onclick="app.generateStudyPlan()">Generate Study Plan</button>
                </div>
                <div style="margin: 20px 0;">
                    <h3>📊 Learning Analytics</h3>
                    <p>AI analysis of your learning patterns and progress.</p>
                    <button class="btn btn-success" onclick="app.getLearningAnalysis()">View Analysis</button>
                </div>
                <div style="margin: 20px 0;">
                    <h3>💬 Enhanced AI Chat</h3>
                    <p>Advanced conversational AI with context awareness.</p>
                    <button class="btn btn-primary" onclick="app.closeModal('aiFeaturesModal'); app.switchTab('ai-assistant')">Open AI Chat</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async generateStudyPlan() {
        const goals = prompt('What are your learning goals?');
        const time = prompt('How many hours per week can you dedicate to learning?');
        
        if (!goals || !time) return;
        
        try {
            const response = await fetch(`${this.apiBase}/ai/study-plan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    goals: goals,
                    available_time: parseInt(time),
                    difficulty_level: 'intermediate'
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showStudyPlanModal(data);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Failed to generate study plan', 'error');
        }
    }

    async getLearningAnalysis() {
        try {
            const response = await fetch(`${this.apiBase}/ai/learning-analysis`);
            const data = await response.json();
            
            if (response.ok) {
                this.showAnalysisModal(data);
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            this.showNotification('Failed to get learning analysis', 'error');
        }
    }

    showStudyPlanModal(plan) {
        this.closeModal('aiFeaturesModal');
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'studyPlanModal';
        modal.style.display = 'flex';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px; max-height: 80vh; overflow-y: auto;">
                <span class="close-modal" onclick="app.closeModal('studyPlanModal')">&times;</span>
                <h2>📚 Your Personalized Study Plan</h2>
                <div style="margin: 20px 0;">
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; white-space: pre-wrap;">${JSON.stringify(plan, null, 2)}</pre>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    showAnalysisModal(analysis) {
        this.closeModal('aiFeaturesModal');
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'analysisModal';
        modal.style.display = 'flex';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px; max-height: 80vh; overflow-y: auto;">
                <span class="close-modal" onclick="app.closeModal('analysisModal')">&times;</span>
                <h2>📊 Learning Analytics Report</h2>
                <div style="margin: 20px 0;">
                    <h3>📈 Key Insights</h3>
                    <p><strong>Learning Streak:</strong> ${analysis.learning_streak}</p>
                    <p><strong>Most Active Time:</strong> ${analysis.most_active_time}</p>
                    <p><strong>Completion Rate:</strong> ${analysis.completion_rate}</p>
                    
                    <h3>💪 Strengths</h3>
                    <ul>${analysis.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
                    
                    <h3>🎯 Recommendations</h3>
                    <ul>${analysis.recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    addPremiumBadge() {
        const logo = document.querySelector('.logo');
        if (logo && !logo.querySelector('.premium-badge')) {
            const badge = document.createElement('span');
            badge.className = 'premium-badge';
            badge.style.cssText = `
                background: gold;
                color: black;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.7rem;
                margin-left: 10px;
                font-weight: bold;
            `;
            badge.textContent = 'PREMIUM';
            logo.appendChild(badge);
        }
    }

    async logout() {
        try {
            await fetch(`${this.apiBase}/logout`, { method: 'POST' });
            this.currentUser = null;
            location.reload();
        } catch (error) {
            console.error('Logout failed:', error);
        }
    }

    openModal(modalId) {
        document.getElementById(modalId).style.display = 'flex';
    }

    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.dashboard-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        event.currentTarget.classList.add('active');
        
        // Show active content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName + '-tab').classList.add('active');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            z-index: 10000;
            max-width: 300px;
            font-weight: 500;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        
        // Set background color based on type
        const colors = {
            success: '#4cc9f0',
            error: '#ef476f',
            info: '#4361ee',
            warning: '#ffd166'
        };
        
        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    openPaymentModal() {
        if (!this.currentUser) {
            this.openModal('loginModal');
            return;
        }
        this.openModal('paymentModal');
    }

    openWellnessModal() {
        // Create wellness logging modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'wellnessModal';
        modal.style.display = 'flex';
        
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close-modal" onclick="app.closeModal('wellnessModal')">&times;</span>
                <h2>Log Wellness Activity</h2>
                <form id="wellnessForm">
                    <div class="form-group">
                        <label for="activityType">Activity Type</label>
                        <select id="activityType" required>
                            <option value="">Select activity</option>
                            <option value="meditation">Meditation</option>
                            <option value="exercise">Exercise</option>
                            <option value="sleep">Sleep</option>
                            <option value="breathing">Breathing Exercise</option>
                            <option value="walk">Walk</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="duration">Duration (minutes)</label>
                        <input type="number" id="duration" min="1" required>
                    </div>
                    <div class="form-group">
                        <label for="intensity">Intensity</label>
                        <select id="intensity">
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="notes">Notes (optional)</label>
                        <textarea id="notes" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Log Activity</button>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Handle form submission
        document.getElementById('wellnessForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const response = await fetch(`${this.apiBase}/wellness/log`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        activity_type: document.getElementById('activityType').value,
                        duration_minutes: parseInt(document.getElementById('duration').value),
                        intensity: document.getElementById('intensity').value,
                        notes: document.getElementById('notes').value
                    })
                });

                if (response.ok) {
                    this.closeModal('wellnessModal');
                    this.showNotification('Wellness activity logged successfully!', 'success');
                    this.loadDashboardData();
                } else {
                    const data = await response.json();
                    this.showNotification(data.error, 'error');
                }
            } catch (error) {
                this.showNotification('Failed to log activity', 'error');
            }
        });
    }
}

// Initialize the app
const app = new EduHealthApp();

// Global functions for HTML onclick handlers
function openModal(modalId) {
    app.openModal(modalId);
}

function closeModal(modalId) {
    app.closeModal(modalId);
}

function switchToRegister() {
    app.closeModal('loginModal');
    app.openModal('registerModal');
}

function switchToLogin() {
    app.closeModal('registerModal');
    app.openModal('loginModal');
}

function switchTab(tabName) {
    app.switchTab(tabName);
}

function processPayment() {
    app.processPayment();
}

function openPaymentModal() {
    app.openPaymentModal();
}
