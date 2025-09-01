from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import requests
import json
import os
from functools import wraps
from database_config import SupabaseConfig, get_supabase_engine
from paystack_integration import init_paystack_payment, handle_paystack_webhook
from groq_integration import init_groq_ai, get_user_learning_context
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Database configuration - use SQLite for development (Supabase client handles production DB separately)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduhealth.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize integrations
try:
    paystack = init_paystack_payment()
except ValueError as e:
    app.logger.warning(f"Paystack not configured: {e}")
    paystack = None

try:
    groq_ai = init_groq_ai()
except ValueError as e:
    app.logger.warning(f"Groq AI not configured: {e}")
    groq_ai = None

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    subscription_type = db.Column(db.String(20), default='free')
    subscription_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress = db.relationship('LearningProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    wellness_logs = db.relationship('WellnessLog', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_interactions = db.relationship('AIInteraction', backref='user', lazy=True, cascade='all, delete-orphan')
    payment_transactions = db.relationship('PaymentTransaction', backref='user', lazy=True, cascade='all, delete-orphan')

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    difficulty_level = db.Column(db.String(20))
    estimated_hours = db.Column(db.Integer)
    premium_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress = db.relationship('LearningProgress', backref='course', lazy=True, cascade='all, delete-orphan')

class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.String(36), db.ForeignKey('courses.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_user_course'),)

class WellnessLog(db.Model):
    __tablename__ = 'wellness_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # meditation, exercise, sleep, etc.
    duration_minutes = db.Column(db.Integer)
    intensity = db.Column(db.String(20))  # low, medium, high
    notes = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIInteraction(db.Model):
    __tablename__ = 'ai_interactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    interaction_type = db.Column(db.String(50), default='general')  # learning, wellness, general
    model_used = db.Column(db.String(50), default='groq')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    paystack_reference = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='pending')
    plan_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Helper Functions
def premium_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        if current_user.subscription_type == 'free':
            return jsonify({'error': 'Premium subscription required'}), 403
            
        if current_user.subscription_expires and current_user.subscription_expires < datetime.utcnow():
            return jsonify({'error': 'Subscription expired'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def get_ai_recommendation(user_data, request_type):
    """Get AI recommendations using Groq or fallback to simulated responses"""
    if groq_ai:
        try:
            user_context = get_user_learning_context(current_user.id) if current_user.is_authenticated else {}
            
            if request_type == 'learning':
                return groq_ai.generate_learning_recommendation(user_context)
            elif request_type == 'wellness':
                return groq_ai.generate_wellness_recommendation(user_context)
        except Exception as e:
            app.logger.error(f"Groq AI error: {e}")
    
    # Fallback to simulated recommendations
    recommendations = {
        'learning': [
            "Based on your progress in Python, I recommend practicing list comprehensions with real-world examples.",
            "You've been consistent with Data Science fundamentals. Try building a small project to apply your knowledge.",
            "Consider taking a short break - you've been learning for 2 hours straight!"
        ],
        'wellness': [
            "Your stress levels seem elevated. Try a 5-minute breathing exercise.",
            "Great job on your physical activity! Consider adding some stretching to your routine.",
            "Your sleep pattern shows room for improvement. Try establishing a bedtime routine."
        ]
    }
    
    import random
    return random.choice(recommendations.get(request_type, ["Keep up the great work!"]))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=password_hash
    )
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        login_user(user)
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'subscription_type': user.subscription_type
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/courses')
@login_required
def get_courses():
    courses = Course.query.all()
    course_list = []
    
    for course in courses:
        # Check if user has access to premium courses
        if course.premium_required and current_user.subscription_type == 'free':
            continue
            
        # Get user's progress for this course
        progress = LearningProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course.id
        ).first()
        
        course_data = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'category': course.category,
            'difficulty_level': course.difficulty_level,
            'estimated_hours': course.estimated_hours,
            'premium_required': course.premium_required,
            'progress_percentage': progress.progress_percentage if progress else 0
        }
        course_list.append(course_data)
    
    return jsonify(course_list)

@app.route('/api/progress')
@login_required
def get_progress():
    progress_records = LearningProgress.query.filter_by(user_id=current_user.id).all()
    progress_data = []
    
    for progress in progress_records:
        progress_data.append({
            'course_title': progress.course.title,
            'progress_percentage': progress.progress_percentage,
            'last_accessed': progress.last_accessed.isoformat(),
            'completed': progress.completed
        })
    
    return jsonify(progress_data)

@app.route('/api/wellness/log', methods=['POST'])
@login_required
def log_wellness_activity():
    data = request.get_json()
    
    wellness_log = WellnessLog(
        user_id=current_user.id,
        activity_type=data.get('activity_type'),
        duration_minutes=data.get('duration_minutes'),
        intensity=data.get('intensity'),
        notes=data.get('notes')
    )
    
    db.session.add(wellness_log)
    db.session.commit()
    
    return jsonify({'message': 'Wellness activity logged successfully'}), 201

@app.route('/api/wellness/summary')
@login_required
def get_wellness_summary():
    # Get wellness data for the last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    wellness_logs = WellnessLog.query.filter(
        WellnessLog.user_id == current_user.id,
        WellnessLog.logged_at >= week_ago
    ).all()
    
    # Calculate summary statistics
    total_activities = len(wellness_logs)
    total_minutes = sum(log.duration_minutes or 0 for log in wellness_logs)
    
    activity_breakdown = {}
    for log in wellness_logs:
        activity_type = log.activity_type
        if activity_type not in activity_breakdown:
            activity_breakdown[activity_type] = {'count': 0, 'total_minutes': 0}
        activity_breakdown[activity_type]['count'] += 1
        activity_breakdown[activity_type]['total_minutes'] += log.duration_minutes or 0
    
    return jsonify({
        'total_activities': total_activities,
        'total_minutes': total_minutes,
        'activity_breakdown': activity_breakdown,
        'week_summary': f"You've completed {total_activities} wellness activities this week!"
    })

@app.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Determine interaction type based on message content
    interaction_type = 'general'
    if any(word in user_message.lower() for word in ['learn', 'study', 'course', 'progress']):
        interaction_type = 'learning'
    elif any(word in user_message.lower() for word in ['stress', 'wellness', 'exercise', 'meditation']):
        interaction_type = 'wellness'
    
    # Get AI response using Groq or fallback
    if groq_ai:
        try:
            # Get conversation history
            recent_interactions = AIInteraction.query.filter_by(
                user_id=current_user.id
            ).order_by(AIInteraction.created_at.desc()).limit(5).all()
            
            conversation_history = []
            for interaction in reversed(recent_interactions):
                conversation_history.append({"sender": "user", "message": interaction.message})
                conversation_history.append({"sender": "ai", "message": interaction.response})
            
            user_context = get_user_learning_context(current_user.id)
            ai_response = groq_ai.chat_response(user_message, conversation_history, user_context)
            
        except Exception as e:
            app.logger.error(f"Groq AI chat error: {e}")
            ai_response = get_ai_recommendation({}, interaction_type)
    else:
        ai_response = get_ai_recommendation({}, interaction_type)
    
    # Save interaction
    interaction = AIInteraction(
        user_id=current_user.id,
        message=user_message,
        response=ai_response,
        interaction_type=interaction_type,
        model_used='groq' if groq_ai else 'simulated'
    )
    
    db.session.add(interaction)
    db.session.commit()
    
    return jsonify({
        'response': ai_response,
        'interaction_type': interaction_type
    })

@app.route('/api/ai/recommendations')
@login_required
@premium_required
def get_ai_recommendations():
    # Get user's learning progress and wellness data
    progress_data = LearningProgress.query.filter_by(user_id=current_user.id).all()
    wellness_data = WellnessLog.query.filter_by(user_id=current_user.id).order_by(
        WellnessLog.logged_at.desc()
    ).limit(10).all()
    
    recommendations = {
        'learning': get_ai_recommendation(progress_data, 'learning'),
        'wellness': get_ai_recommendation(wellness_data, 'wellness'),
        'personalized_tips': [
            "Based on your learning pattern, you're most productive in the morning.",
            "Your wellness activities show great consistency. Keep it up!",
            "Consider taking a 10-minute break every hour while studying."
        ]
    }
    
    return jsonify(recommendations)

# Paystack payment routes
@app.route('/api/payment/initialize', methods=['POST'])
@login_required
def initialize_payment():
    if not paystack:
        return jsonify({'error': 'Payment system not configured'}), 500
    
    data = request.get_json()
    plan_type = data.get('plan_type', 'monthly')
    
    amount = 99.99 if plan_type == 'annual' else 9.99
    
    try:
        response = paystack.initialize_transaction(
            email=current_user.email,
            amount=amount,
            plan_type=plan_type,
            callback_url=data.get('callback_url')
        )
        
        if response.get('status'):
            # Create payment record
            payment = PaymentTransaction(
                user_id=current_user.id,
                paystack_reference=response['data']['reference'],
                amount=amount,
                plan_type=plan_type,
                status='pending'
            )
            db.session.add(payment)
            db.session.commit()
            
            return jsonify(response)
        else:
            return jsonify({'error': response.get('message', 'Payment initialization failed')}), 400
            
    except Exception as e:
        app.logger.error(f"Payment initialization error: {e}")
        return jsonify({'error': 'Payment initialization failed'}), 500

@app.route('/payment/success')
def payment_success():
    reference = request.args.get('reference')
    if reference:
        # Verify payment with Paystack
        if paystack:
            verification = paystack.verify_transaction(reference)
            if verification.get('status') and verification['data']['status'] == 'success':
                # Update user subscription
                payment = PaymentTransaction.query.filter_by(
                    paystack_reference=reference
                ).first()
                
                if payment:
                    payment.status = 'completed'
                    payment.user.subscription_type = 'premium'
                    payment.user.subscription_expires = datetime.utcnow() + timedelta(
                        days=365 if payment.plan_type == 'annual' else 30
                    )
                    db.session.commit()
                    
                return render_template('index.html', payment_success=True)
    
    return render_template('index.html', payment_error=True)

@app.route('/api/payment/webhook', methods=['POST'])
def paystack_webhook():
    if not paystack:
        return jsonify({'error': 'Payment system not configured'}), 500
    
    try:
        signature = request.headers.get('X-Paystack-Signature')
        payload = request.get_data()
        
        if paystack.verify_webhook(payload, signature):
            data = request.get_json()
            
            if data['event'] == 'charge.success':
                reference = data['data']['reference']
                
                # Update payment record
                payment = PaymentTransaction.query.filter_by(
                    paystack_reference=reference
                ).first()
                
                if payment:
                    payment.status = 'completed'
                    payment.user.subscription_type = 'premium'
                    payment.user.subscription_expires = datetime.utcnow() + timedelta(
                        days=365 if payment.plan_type == 'annual' else 30
                    )
                    db.session.commit()
                    
                    return jsonify({'status': 'success'})
        
        return jsonify({'error': 'Invalid webhook'}), 400
        
    except Exception as e:
        app.logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@app.route('/api/payment/verify/<reference>', methods=['GET'])
@login_required
def verify_payment(reference):
    if not paystack:
        return jsonify({'error': 'Payment system not configured'}), 500
    
    try:
        response = paystack.verify_transaction(reference)
        
        if response.get('status') and response['data']['status'] == 'success':
            # Update payment record
            payment = PaymentTransaction.query.filter_by(
                paystack_reference=reference,
                user_id=current_user.id
            ).first()
            
            if payment:
                payment.status = 'completed'
                
                # Update user subscription
                if payment.plan_type == 'annual':
                    current_user.subscription_type = 'premium'
                    current_user.subscription_expires = datetime.utcnow() + timedelta(days=365)
                else:
                    current_user.subscription_type = 'premium'
                    current_user.subscription_expires = datetime.utcnow() + timedelta(days=30)
                
                db.session.commit()
                
                return jsonify({
                    'message': 'Payment verified and subscription activated!',
                    'subscription_type': current_user.subscription_type,
                    'expires': current_user.subscription_expires.isoformat()
                })
        
        return jsonify({'error': 'Payment verification failed'}), 400
        
    except Exception as e:
        app.logger.error(f"Payment verification error: {e}")
        return jsonify({'error': 'Payment verification failed'}), 500

@app.route('/api/payment/webhook', methods=['POST'])
def payment_webhook():
    if not paystack:
        return jsonify({'error': 'Payment system not configured'}), 500
    
    signature = request.headers.get('X-Paystack-Signature')
    webhook_data = request.get_json()
    
    try:
        result = handle_paystack_webhook(webhook_data, signature)
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Webhook processing error: {e}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@app.route('/api/user/profile')
@login_required
def get_user_profile():
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'subscription_type': current_user.subscription_type,
        'subscription_expires': current_user.subscription_expires.isoformat() if current_user.subscription_expires else None,
        'member_since': current_user.created_at.isoformat()
    })

# Initialize database and sample data
def init_db():
    with app.app_context():
        try:
            # Try to setup Supabase if configured
            if os.getenv('SUPABASE_DATABASE_URL'):
                from database_config import setup_supabase_database
                if setup_supabase_database():
                    app.logger.info("Supabase database setup completed")
                    return
        except Exception as e:
            app.logger.warning(f"Supabase setup failed, using local database: {e}")
        
        # Fallback to local SQLite
        db.create_all()
        
        # Add sample courses if they don't exist
        if Course.query.count() == 0:
            sample_courses = [
                Course(
                    title="Python Programming Course",
                    description="Learn Python from basics to advanced concepts",
                    category="Programming",
                    difficulty_level="Beginner",
                    estimated_hours=40,
                    premium_required=False
                ),
                Course(
                    title="Data Science Fundamentals",
                    description="Introduction to data science and analytics",
                    category="Data Science",
                    difficulty_level="Intermediate",
                    estimated_hours=60,
                    premium_required=True
                ),
                Course(
                    title="Web Development Basics",
                    description="HTML, CSS, and JavaScript fundamentals",
                    category="Web Development",
                    difficulty_level="Beginner",
                    estimated_hours=35,
                    premium_required=False
                ),
                Course(
                    title="Machine Learning Essentials",
                    description="Core concepts of machine learning",
                    category="AI/ML",
                    difficulty_level="Advanced",
                    estimated_hours=80,
                    premium_required=True
                ),
                Course(
                    title="Digital Marketing Strategy",
                    description="Comprehensive digital marketing course",
                    category="Marketing",
                    difficulty_level="Intermediate",
                    estimated_hours=45,
                    premium_required=True
                ),
                Course(
                    title="Mindfulness and Meditation",
                    description="Learn mindfulness techniques for better wellness",
                    category="Wellness",
                    difficulty_level="Beginner",
                    estimated_hours=20,
                    premium_required=False
                )
            ]
            
            for course in sample_courses:
                db.session.add(course)
            
            db.session.commit()

# New AI-powered endpoints
@app.route('/api/ai/study-plan', methods=['POST'])
@login_required
@premium_required
def generate_study_plan():
    if not groq_ai:
        return jsonify({'error': 'AI service not available'}), 503
    
    data = request.get_json()
    goals = data.get('goals', '')
    available_time = data.get('available_time', 10)
    difficulty_level = data.get('difficulty_level', 'intermediate')
    
    try:
        study_plan = groq_ai.generate_study_plan(goals, available_time, difficulty_level)
        return jsonify(study_plan)
    except Exception as e:
        app.logger.error(f"Study plan generation error: {e}")
        return jsonify({'error': 'Failed to generate study plan'}), 500

@app.route('/api/ai/learning-analysis', methods=['GET'])
@login_required
@premium_required
def get_learning_analysis():
    if not groq_ai:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        # Get user's learning data
        progress_data = LearningProgress.query.filter_by(user_id=current_user.id).all()
        wellness_data = WellnessLog.query.filter_by(user_id=current_user.id).order_by(
            WellnessLog.logged_at.desc()
        ).limit(30).all()
        
        learning_data = []
        for progress in progress_data:
            learning_data.append({
                'course': progress.course.title,
                'progress': progress.progress_percentage,
                'last_accessed': progress.last_accessed.isoformat(),
                'completed': progress.completed
            })
        
        analysis = groq_ai.analyze_learning_pattern(learning_data)
        return jsonify(analysis)
        
    except Exception as e:
        app.logger.error(f"Learning analysis error: {e}")
        return jsonify({'error': 'Failed to analyze learning patterns'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
