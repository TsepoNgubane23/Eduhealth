# 🎓 EduHealth - AI-Powered Personalized Learning & Wellness Platform

[![GitHub Pages](https://img.shields.io/badge/demo-live-brightgreen)](https://tseponngubane23.github.io/Eduhealth/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.3.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Transform your learning journey with AI-powered personalized education and wellness tracking**

EduHealth is a revolutionary platform that seamlessly integrates quality education with mental and physical wellness initiatives. Using cutting-edge AI technology powered by Groq, it provides personalized learning recommendations, wellness tracking, and an intelligent assistant to guide users toward holistic personal development.

## 🌟 Key Features

### 🤖 AI-Powered Intelligence
- **Groq AI Integration**: Advanced language models for personalized recommendations
- **Smart Learning Assistant**: Interactive chatbot for educational and wellness support
- **Adaptive Learning Paths**: AI-driven course recommendations based on learning patterns
- **Intelligent Analytics**: Learning pattern analysis and progress optimization

### 💳 Secure Payment Processing
- **Paystack Integration**: Secure payment processing with ZAR currency support
- **Multiple Payment Methods**: Cards, bank transfers, and mobile money
- **Subscription Management**: Flexible monthly and annual premium plans
- **Redirect Payment Flow**: Secure hosted payment pages for enhanced security

### 🎯 Comprehensive Wellness Tracking
- **Mental Health Exercises**: Daily mindfulness activities and stress management
- **Physical Activity Tracking**: Step counting and fitness goal monitoring
- **Sleep Quality Analysis**: Sleep pattern tracking and recommendations
- **Holistic Progress Dashboard**: Combined learning and wellness metrics

### 📱 Modern User Experience
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Interactive Dashboard**: Real-time progress tracking with beautiful visualizations
- **Seamless Authentication**: Secure user registration and login system
- **Intuitive Interface**: Clean, modern UI with smooth animations

## 🛠️ Technology Stack

### Backend Architecture
- **Framework**: Python Flask 2.3.3 with SQLAlchemy ORM
- **Database**: 
  - **Production**: Supabase (PostgreSQL) with real-time capabilities
  - **Development**: SQLite for local development
- **Authentication**: Flask-Login with bcrypt password hashing
- **Payment Processing**: Paystack API with webhook support
- **AI Integration**: Groq AI API for chat and recommendations

### Frontend Technologies
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with CSS Grid and Flexbox
- **Icons**: Font Awesome 6.4.0 integration
- **Animations**: CSS transitions and transforms
- **Payment UI**: Paystack JavaScript SDK

### Database Design
```sql
-- Core Tables
Users (id, email, password_hash, subscription_type, created_at)
Courses (id, title, description, difficulty_level, category)
LearningProgress (id, user_id, course_id, progress_percentage, last_accessed)
WellnessLogs (id, user_id, activity_type, duration, mood_rating, date)
AIInteractions (id, user_id, message, response, interaction_type, timestamp)
PaymentTransactions (id, user_id, amount, currency, status, paystack_reference)
```

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.8+ installed
- Git for version control
- Code editor (VS Code recommended)

### 🔧 Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/TsepoNgubane23/Eduhealth.git
   cd Eduhealth
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   # Flask Configuration
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=development
   
   # Supabase Configuration (Production)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   SUPABASE_DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
   
   # Paystack Configuration
   PAYSTACK_PUBLIC_KEY=pk_test_your-public-key
   PAYSTACK_SECRET_KEY=sk_test_your-secret-key
   
   # Groq AI Configuration
   GROQ_API_KEY=gsk_your-groq-api-key
   ```

5. **Initialize Database**
   ```bash
   python database_config.py
   ```

6. **Launch Application**
   ```bash
   python app.py
   ```

🌐 **Access the app**: http://127.0.0.1:5000

## 🎯 Project Overview

### The Challenge
Modern learners struggle to balance educational goals with mental and physical wellness, often leading to burnout and ineffective learning outcomes.

### Our Solution
EduHealth addresses this by:
- **Integrating AI-powered personalization** for optimal learning paths
- **Combining education with wellness tracking** for holistic development
- **Providing real-time feedback** through intelligent analytics
- **Offering flexible subscription models** accessible to diverse users

### Target Market
- **Students**: University and high school students seeking balanced learning
- **Professionals**: Working adults pursuing skill development
- **Corporations**: Companies investing in employee wellness and training
- **Educational Institutions**: Schools looking for comprehensive learning platforms

## 📡 API Documentation

### 🔐 Authentication Endpoints
```http
POST /api/register          # User registration
POST /api/login             # User login  
POST /api/logout            # User logout
```

### 📚 Learning & Progress
```http
GET  /api/courses           # Get available courses
POST /api/learning/progress # Update learning progress
GET  /api/learning/progress # Get user progress
```

### 🧘 Wellness Tracking
```http
POST /api/wellness/log      # Log wellness activity
GET  /api/wellness/summary  # Get wellness summary
```

### 🤖 AI Features (Groq-Powered)
```http
POST /api/ai/chat              # AI chat interaction
GET  /api/ai/recommendations   # Get personalized recommendations
POST /api/ai/study-plan        # Generate personalized study plan
GET  /api/ai/learning-analysis # Get learning pattern analysis
```

### 💳 Payment Processing (Paystack)
```http
POST /api/payment/initialize   # Initialize payment transaction
GET  /api/payment/verify/:ref  # Verify payment by reference
POST /api/payment/webhook      # Payment webhook handler
GET  /payment/success          # Payment success callback
```

## 🔧 Advanced Configuration

### Groq AI Models
```python
# Current model configuration in groq_integration.py
MODELS = {
    "fast": "llama-3.1-8b-instant",      # Quick responses
    "balanced": "llama-3.1-70b-versatile", # Balanced performance
    "creative": "llama-3.1-8b-instant"   # Creative tasks
}
```

### Paystack Integration Features
- **Currency Support**: South African Rand (ZAR)
- **Payment Methods**: Cards, bank transfers, mobile money
- **Security**: PCI DSS compliant processing
- **Webhooks**: Real-time payment verification
- **Redirect Flow**: Secure hosted payment pages

### Database Fallback System
```python
# Automatic fallback from Supabase to SQLite
try:
    # Attempt Supabase connection
    supabase_client = create_client(supabase_url, supabase_key)
    app.config['SQLALCHEMY_DATABASE_URI'] = supabase_db_url
except Exception:
    # Fallback to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduhealth.db'
```

## 🚀 Deployment Options

### 🌐 GitHub Pages (Static Demo)
**Live Demo**: [https://tseponngubane23.github.io/Eduhealth/](https://tseponngubane23.github.io/Eduhealth/)

The static demo showcases the frontend design and user interface without backend functionality.

### ☁️ Production Deployment

#### Recommended Platforms:
1. **Heroku** - Easy Flask deployment
2. **Railway** - Modern Python hosting
3. **Render** - Free tier with GitHub integration
4. **PythonAnywhere** - Python-focused hosting

#### Deployment Steps:
```bash
# 1. Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key

# 2. Install production server
pip install gunicorn

# 3. Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Docker Deployment:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 💰 Business Model

### 💳 Subscription Pricing (ZAR)
- **Free Tier**: R 0 - Basic features, limited access
- **Premium**: R 179/month - Full access, AI recommendations
- **Annual**: R 1,799/year - Premium features with 2 months free

### 📈 Revenue Streams
- **B2C Subscriptions**: Individual premium memberships
- **B2B Corporate**: Employee wellness and training programs
- **Educational Partnerships**: Institutional licensing
- **Premium Content**: Specialized courses and coaching sessions

## 🔒 Security & Privacy

### 🛡️ Security Measures
- **Password Security**: bcrypt hashing with salt
- **Session Management**: Flask-Login secure sessions
- **Payment Security**: PCI DSS compliant Paystack integration
- **Data Protection**: SQLAlchemy ORM prevents SQL injection
- **API Security**: Environment-based configuration

### 🔐 Privacy Features
- **Data Encryption**: Sensitive data encrypted at rest
- **Secure Communications**: HTTPS in production
- **User Control**: Data export and deletion options
- **Compliance**: GDPR-ready privacy controls

## 🧪 Testing & Quality Assurance

### ✅ Test Coverage
```bash
# Run local testing
python -m pytest tests/

# Test specific features
python app.py  # Start development server
```

### 🔍 Key Test Areas
1. **Authentication Flow** - Registration, login, logout
2. **Payment Processing** - Paystack integration testing
3. **AI Interactions** - Groq API responses
4. **Database Operations** - CRUD operations
5. **Responsive Design** - Cross-device compatibility

## 🔮 Future Roadmap

### 📱 Phase 1: Mobile Experience
- Progressive Web App (PWA) implementation
- Mobile-optimized UI/UX improvements
- Offline functionality for core features

### 🤖 Phase 2: Advanced AI
- Multi-modal AI interactions (voice, image)
- Predictive learning analytics
- Personalized wellness recommendations

### 🌍 Phase 3: Platform Expansion
- Multi-language support (Afrikaans, Zulu, Xhosa)
- Integration with popular learning platforms
- Social learning and community features

### 🏢 Phase 4: Enterprise Features
- Corporate dashboards and analytics
- Bulk user management
- Custom branding options

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### 📝 Contribution Guidelines
- Follow PEP 8 Python style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure responsive design compatibility

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

### 🆘 Get Help
- **GitHub Issues**: [Report bugs or request features](https://github.com/TsepoNgubane23/Eduhealth/issues)
- **Email**: support@eduhealth.com
- **Documentation**: Comprehensive guides in `/docs`

### 👥 Community
- **Discussions**: Join our GitHub Discussions
- **Updates**: Follow development progress
- **Feedback**: Share your experience and suggestions

## 🙏 Acknowledgments

### 🛠️ Technology Partners
- **Groq AI** - Advanced language model capabilities
- **Paystack** - Secure payment processing for African markets
- **Supabase** - Real-time database and authentication
- **Flask Community** - Excellent framework and documentation

### 🎨 Design & Assets
- **Font Awesome** - Beautiful iconography
- **CSS Grid & Flexbox** - Modern responsive layouts
- **Color Palette** - Carefully chosen for accessibility

### 👨‍💻 Development
Built with ❤️ by developers passionate about education and wellness technology.

---

## 🌟 Project Vision

**EduHealth** represents the future of personalized learning - where education meets wellness, powered by AI, and designed for the modern learner. Our mission is to transform how people learn and grow, creating a more balanced and effective approach to personal development.

### 🎯 Impact Goals
- **10,000+ Users** in the first year
- **Improved Learning Outcomes** through AI personalization
- **Better Work-Life Balance** via integrated wellness tracking
- **Accessible Education** across diverse communities

**Join us in revolutionizing education and wellness! 🚀**
