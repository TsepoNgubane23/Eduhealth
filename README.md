# EduHealth - AI-Powered Personalized Learning & Wellness Platform

EduHealth is a comprehensive platform that combines quality education with mental and physical wellness initiatives, offering a holistic approach to personal development through AI-powered personalized recommendations.

## Features

### Core Features
- **Personalized Learning**: AI-driven course recommendations based on learning patterns
- **Wellness Integration**: Mental health exercises and physical activity tracking
- **Progress Analytics**: Comprehensive tracking of learning and wellness progress
- **AI Assistant**: Interactive chatbot powered by Groq AI for educational and wellness support
- **Premium Subscriptions**: Advanced features with flexible pricing plans

### User Experience
- Responsive web design optimized for all devices
- Intuitive dashboard with real-time progress tracking
- Seamless user registration and authentication
- Interactive modals for enhanced user engagement

## Technology Stack

### Backend
- **Framework**: Python Flask 2.3.3
- **Database**: Supabase (PostgreSQL) for production, SQLite for development
- **Authentication**: Flask-Login with bcrypt password hashing
- **Payment Processing**: Paystack API integration
- **AI Integration**: Groq AI for chat, recommendations, and analytics

### Frontend
- **Languages**: HTML5, CSS3, JavaScript (ES6+)
- **Design**: Responsive CSS Grid and Flexbox
- **Icons**: Font Awesome integration
- **Animations**: CSS transitions and transforms
- **Payment UI**: Paystack JavaScript SDK

### Database Schema
- **Users**: Authentication and subscription management (UUID primary keys)
- **Courses**: Educational content and metadata
- **Learning Progress**: User progress tracking
- **Wellness Logs**: Activity and mood tracking
- **AI Interactions**: Chat history and recommendations
- **Payment Transactions**: Subscription and payment records

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Supabase account (for production database)
- Paystack account (for payment processing)
- Groq API key (for AI features)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd eduhealth
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual API keys and credentials:
   # - Supabase URL, keys, and database URL
   # - Paystack public and secret keys
   # - Groq API key
   # - Flask secret key
   ```

5. **Initialize Supabase database**
   ```bash
   # Run the database setup script
   python database_config.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://127.0.0.1:5000`

## Environment Configuration

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development

# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_DATABASE_URL=postgresql://postgres:password@db.your-project-ref.supabase.co:5432/postgres

# Paystack Configuration
PAYSTACK_PUBLIC_KEY=pk_test_your-public-key
PAYSTACK_SECRET_KEY=sk_test_your-secret-key

# Groq Configuration
GROQ_API_KEY=gsk_your-groq-api-key
```

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Learning & Progress
- `GET /api/courses` - Get available courses
- `POST /api/learning/progress` - Update learning progress
- `GET /api/learning/progress` - Get user progress

### Wellness
- `POST /api/wellness/log` - Log wellness activity
- `GET /api/wellness/summary` - Get wellness summary

### AI Features (Groq-powered)
- `POST /api/ai/chat` - AI chat interaction
- `GET /api/ai/recommendations` - Get personalized recommendations
- `POST /api/ai/study-plan` - Generate personalized study plan
- `GET /api/ai/learning-analysis` - Get learning pattern analysis

### Payments (Paystack)
- `POST /api/payment/initialize` - Initialize payment
- `POST /api/payment/verify` - Verify payment
- `POST /api/payment/webhook` - Payment webhook
- `POST /api/payment/create-plan` - Create subscription plan

## New Integrations

EduHealth integrates with IntaSend for secure payment processing:

### Supported Payment Methods
- Credit/Debit Cards (Visa, Mastercard)
- Mobile Money (M-PESA, Airtel Money)
- Bank transfers

### Security Features
- PCI DSS compliant payment processing
- Secure webhook handling
- Encrypted payment data transmission

## 🤖 AI Integration

### Current Implementation
- Simulated AI responses for demonstration
- Context-aware recommendations based on user activity
- Learning and wellness interaction categorization

### Production Integration
Replace the `get_ai_recommendation()` function in `app.py` with:

```python
import openai

def get_ai_recommendation(user_data, request_type):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    prompt = f"Generate a {request_type} recommendation for user with data: {user_data}"
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    
    return response.choices[0].text.strip()
```

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   export DATABASE_URL=your-production-database-url
   ```

2. **Database Migration**
   ```bash
   # For MySQL/PostgreSQL
   pip install mysql-connector-python  # or psycopg2-binary
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 Revenue Model

### Subscription Tiers
- **Free**: $0 - Basic features, limited access
- **Premium**: $9.99/month - Full access, AI recommendations
- **Annual**: $99.99/year - Premium features with discount

### Additional Revenue Streams
- Corporate wellness partnerships (B2B)
- Specialized course purchases
- Premium coaching sessions

## 🔒 Security Features

- Password hashing with bcrypt
- Session management with Flask-Login
- CSRF protection
- SQL injection prevention with SQLAlchemy ORM
- Secure payment processing with IntaSend

## 🧪 Testing

Run the application locally and test:

1. **User Registration/Login**
2. **Course Progress Tracking**
3. **Wellness Activity Logging**
4. **AI Chat Functionality**
5. **Payment Processing** (test mode)

## 📈 Future Enhancements

- Mobile app development (React Native/Flutter)
- Advanced AI personalization
- Social learning features
- Gamification elements
- Integration with fitness trackers
- Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and inquiries:
- Email: support@eduhealth.com
- Phone: +1 (234) 567-890
- Documentation: [Link to full documentation]

## 🙏 Acknowledgments

- Flask community for excellent documentation
- IntaSend for payment processing capabilities
- OpenAI for AI integration possibilities
- Font Awesome for icons
- All beta testers and early users

---

**EduHealth** - Transforming lives through personalized learning and wellness! 🌟
