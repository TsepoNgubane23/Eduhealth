import os
from supabase import create_client, Client
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

class SupabaseConfig:
    """Supabase database configuration for EduHealth"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.database_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if not all([self.supabase_url, self.supabase_key, self.database_url]):
            raise ValueError("Missing required Supabase environment variables")
    
    def get_supabase_client(self) -> Client:
        """Get Supabase client for real-time features and auth"""
        return create_client(self.supabase_url, self.supabase_key)
    
    def get_database_url(self) -> str:
        """Get PostgreSQL connection string for SQLAlchemy"""
        return self.database_url
    
    def create_tables_sql(self) -> str:
        """SQL commands to create tables in Supabase"""
        return """
        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            subscription_type VARCHAR(20) DEFAULT 'free',
            subscription_expires TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Courses table
        CREATE TABLE IF NOT EXISTS courses (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            title VARCHAR(200) NOT NULL,
            description TEXT,
            category VARCHAR(50),
            difficulty_level VARCHAR(20),
            estimated_hours INTEGER,
            premium_required BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Learning progress table
        CREATE TABLE IF NOT EXISTS learning_progress (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
            progress_percentage DECIMAL(5,2) DEFAULT 0.0,
            last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id, course_id)
        );
        
        -- Wellness logs table
        CREATE TABLE IF NOT EXISTS wellness_logs (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            activity_type VARCHAR(50) NOT NULL,
            duration_minutes INTEGER,
            intensity VARCHAR(20),
            notes TEXT,
            logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- AI interactions table
        CREATE TABLE IF NOT EXISTS ai_interactions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            interaction_type VARCHAR(50) DEFAULT 'general',
            model_used VARCHAR(50) DEFAULT 'groq',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Payment transactions table
        CREATE TABLE IF NOT EXISTS payment_transactions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            paystack_reference VARCHAR(100) UNIQUE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'USD',
            status VARCHAR(20) DEFAULT 'pending',
            plan_type VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_learning_progress_user_id ON learning_progress(user_id);
        CREATE INDEX IF NOT EXISTS idx_wellness_logs_user_id ON wellness_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_ai_interactions_user_id ON ai_interactions(user_id);
        CREATE INDEX IF NOT EXISTS idx_payment_transactions_user_id ON payment_transactions(user_id);
        CREATE INDEX IF NOT EXISTS idx_payment_transactions_reference ON payment_transactions(paystack_reference);
        
        -- Enable Row Level Security (RLS)
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE learning_progress ENABLE ROW LEVEL SECURITY;
        ALTER TABLE wellness_logs ENABLE ROW LEVEL SECURITY;
        ALTER TABLE ai_interactions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
        
        -- Create RLS policies
        CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid()::text = id::text);
        CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid()::text = id::text);
        
        CREATE POLICY "Users can view own progress" ON learning_progress FOR ALL USING (auth.uid()::text = user_id::text);
        CREATE POLICY "Users can view own wellness logs" ON wellness_logs FOR ALL USING (auth.uid()::text = user_id::text);
        CREATE POLICY "Users can view own AI interactions" ON ai_interactions FOR ALL USING (auth.uid()::text = user_id::text);
        CREATE POLICY "Users can view own transactions" ON payment_transactions FOR SELECT USING (auth.uid()::text = user_id::text);
        
        -- Insert sample courses
        INSERT INTO courses (title, description, category, difficulty_level, estimated_hours, premium_required) VALUES
        ('Python Programming Course', 'Learn Python from basics to advanced concepts', 'Programming', 'Beginner', 40, FALSE),
        ('Data Science Fundamentals', 'Introduction to data science and analytics', 'Data Science', 'Intermediate', 60, TRUE),
        ('Web Development Basics', 'HTML, CSS, and JavaScript fundamentals', 'Web Development', 'Beginner', 35, FALSE),
        ('Machine Learning Essentials', 'Core concepts of machine learning', 'AI/ML', 'Advanced', 80, TRUE),
        ('Digital Marketing Strategy', 'Comprehensive digital marketing course', 'Marketing', 'Intermediate', 45, TRUE),
        ('Mindfulness and Meditation', 'Learn mindfulness techniques for better wellness', 'Wellness', 'Beginner', 20, FALSE)
        ON CONFLICT DO NOTHING;
        """

def setup_supabase_database():
    """Initialize Supabase database with tables and sample data"""
    try:
        config = SupabaseConfig()
        
        # Create engine for direct SQL execution
        engine = create_engine(config.get_database_url())
        
        with engine.connect() as connection:
            # Execute table creation SQL
            connection.execute(text(config.create_tables_sql()))
            connection.commit()
            
        print("✅ Supabase database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Supabase database: {e}")
        return False

def get_supabase_engine():
    """Get SQLAlchemy engine for Supabase"""
    config = SupabaseConfig()
    return create_engine(
        config.get_database_url(),
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300
    )

# Environment variables template for .env file
ENV_TEMPLATE = """
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres

# Paystack Configuration
PAYSTACK_PUBLIC_KEY=pk_test_your-public-key
PAYSTACK_SECRET_KEY=sk_test_your-secret-key

# Groq Configuration
GROQ_API_KEY=your-groq-api-key

# Flask Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=development
"""
