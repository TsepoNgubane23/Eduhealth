import os
import json
from groq import Groq
from flask import current_app
from datetime import datetime
from typing import Dict, List, Optional

class GroqAI:
    """Groq AI Integration for EduHealth"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.models = {
            "fast": "llama-3.1-8b-instant",
            "balanced": "llama-3.1-70b-versatile", 
            "creative": "llama-3.1-8b-instant"
        }
        
    def generate_learning_recommendation(self, user_data: Dict, context: str = "") -> str:
        """Generate personalized learning recommendations"""
        
        prompt = f"""
        You are an AI learning assistant for EduHealth, a personalized learning and wellness platform.
        
        User Context:
        - Learning Progress: {user_data.get('progress', 'No data available')}
        - Courses Enrolled: {user_data.get('courses', 'No courses')}
        - Learning Style: {user_data.get('learning_style', 'Not specified')}
        - Goals: {user_data.get('goals', 'General skill development')}
        
        Additional Context: {context}
        
        Generate a personalized learning recommendation that:
        1. Is specific and actionable
        2. Considers the user's current progress
        3. Suggests next steps or new topics
        4. Includes estimated time commitment
        5. Is encouraging and motivating
        
        Keep the response concise (2-3 sentences) and practical.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful AI learning assistant focused on personalized education recommendations."},
                    {"role": "user", "content": prompt}
                ],
                model=self.models["balanced"],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            current_app.logger.error(f"Groq learning recommendation error: {e}")
            return "I'm having trouble generating recommendations right now. Please try again later."
    
    def generate_wellness_recommendation(self, user_data: Dict, context: str = "") -> str:
        """Generate personalized wellness recommendations"""
        
        prompt = f"""
        You are an AI wellness coach for EduHealth, focusing on mental and physical wellbeing.
        
        User Wellness Data:
        - Recent Activities: {user_data.get('recent_activities', 'No recent activities')}
        - Stress Level: {user_data.get('stress_level', 'Not specified')}
        - Sleep Quality: {user_data.get('sleep_quality', 'Not specified')}
        - Physical Activity: {user_data.get('physical_activity', 'Not specified')}
        - Study Hours Today: {user_data.get('study_hours', 'Not specified')}
        
        Additional Context: {context}
        
        Generate a personalized wellness recommendation that:
        1. Addresses current wellness needs
        2. Suggests specific activities or exercises
        3. Considers work-life balance
        4. Includes duration and timing suggestions
        5. Is supportive and encouraging
        
        Keep the response concise (2-3 sentences) and actionable.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a supportive AI wellness coach focused on mental and physical health."},
                    {"role": "user", "content": prompt}
                ],
                model=self.models["balanced"],
                temperature=0.8,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            current_app.logger.error(f"Groq wellness recommendation error: {e}")
            return "I'm having trouble generating wellness recommendations right now. Please try again later."
    
    def chat_response(self, user_message: str, conversation_history: List[Dict], user_context: Dict) -> str:
        """Generate contextual chat responses"""
        
        # Build conversation context
        context_prompt = f"""
        You are an AI assistant for EduHealth, a learning and wellness platform. You help users with:
        - Learning guidance and study tips
        - Wellness advice and mental health support
        - Platform navigation and features
        - Motivation and encouragement
        
        User Profile:
        - Name: {user_context.get('name', 'User')}
        - Subscription: {user_context.get('subscription_type', 'free')}
        - Current Courses: {user_context.get('current_courses', 'None')}
        - Recent Activity: {user_context.get('recent_activity', 'None')}
        
        Guidelines:
        - Be helpful, encouraging, and supportive
        - Provide actionable advice when possible
        - If asked about premium features and user has free account, gently suggest upgrading
        - Keep responses concise but informative
        - Focus on both learning and wellness aspects
        """
        
        # Build message history
        messages = [{"role": "system", "content": context_prompt}]
        
        # Add conversation history (last 5 messages to stay within context)
        for msg in conversation_history[-5:]:
            messages.append({
                "role": "user" if msg.get("sender") == "user" else "assistant",
                "content": msg.get("message", "")
            })
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.models["fast"],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            current_app.logger.error(f"Groq chat response error: {e}")
            return "I'm experiencing some technical difficulties. Please try asking your question again."
    
    def analyze_learning_pattern(self, learning_data: List[Dict]) -> Dict:
        """Analyze user learning patterns and provide insights"""
        
        prompt = f"""
        Analyze the following learning data and provide insights:
        
        Learning Data: {json.dumps(learning_data, indent=2)}
        
        Provide analysis in the following JSON format:
        {{
            "learning_streak": "number of consecutive days",
            "most_active_time": "time of day when most active",
            "preferred_subjects": ["list", "of", "subjects"],
            "completion_rate": "percentage",
            "recommendations": ["specific", "actionable", "recommendations"],
            "strengths": ["identified", "strengths"],
            "areas_for_improvement": ["areas", "to", "focus", "on"]
        }}
        
        Base your analysis on patterns in the data and provide actionable insights.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a data analyst specializing in learning analytics. Provide structured JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                model=self.models["balanced"],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse JSON response
            analysis = json.loads(response.choices[0].message.content.strip())
            return analysis
            
        except Exception as e:
            current_app.logger.error(f"Groq learning analysis error: {e}")
            return {
                "learning_streak": "Unable to analyze",
                "most_active_time": "Unknown",
                "preferred_subjects": [],
                "completion_rate": "Unknown",
                "recommendations": ["Continue your learning journey!"],
                "strengths": ["Consistent engagement"],
                "areas_for_improvement": ["Data collection needed"]
            }
    
    def generate_study_plan(self, user_goals: str, available_time: int, difficulty_level: str) -> Dict:
        """Generate a personalized study plan"""
        
        prompt = f"""
        Create a personalized study plan based on:
        - Goals: {user_goals}
        - Available time per week: {available_time} hours
        - Difficulty level: {difficulty_level}
        
        Provide a structured study plan in JSON format:
        {{
            "weekly_schedule": {{
                "monday": ["task1", "task2"],
                "tuesday": ["task1", "task2"],
                // ... for each day
            }},
            "milestones": [
                {{"week": 1, "goal": "Complete basic concepts", "deliverable": "Quiz completion"}},
                // ... more milestones
            ],
            "resources": [
                {{"type": "video", "title": "Resource title", "duration": "30 min"}},
                // ... more resources
            ],
            "tips": ["study tip 1", "study tip 2"]
        }}
        
        Make the plan realistic and achievable within the given time constraints.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert educational planner. Create structured, realistic study plans in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                model=self.models["balanced"],
                temperature=0.5,
                max_tokens=800
            )
            
            study_plan = json.loads(response.choices[0].message.content.strip())
            return study_plan
            
        except Exception as e:
            current_app.logger.error(f"Groq study plan error: {e}")
            return {
                "weekly_schedule": {"message": "Unable to generate plan at this time"},
                "milestones": [],
                "resources": [],
                "tips": ["Set aside dedicated study time", "Take regular breaks", "Stay consistent"]
            }

def init_groq_ai():
    """Initialize Groq AI client"""
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY environment variable")
    
    return GroqAI(api_key)

def get_user_learning_context(user_id: str) -> Dict:
    """Get user context for AI recommendations"""
    try:
        from app import User, LearningProgress, Course, WellnessLog
        
        user = User.query.get(user_id)
        if not user:
            return {}
        
        # Get learning progress
        progress = LearningProgress.query.filter_by(user_id=user_id).all()
        courses = [p.course.title for p in progress if p.course]
        
        # Get recent wellness activities
        recent_wellness = WellnessLog.query.filter_by(user_id=user_id).order_by(
            WellnessLog.logged_at.desc()
        ).limit(5).all()
        
        return {
            "name": user.name,
            "subscription_type": user.subscription_type,
            "current_courses": courses,
            "progress": [{"course": p.course.title, "percentage": p.progress_percentage} for p in progress],
            "recent_activities": [{"type": w.activity_type, "duration": w.duration_minutes} for w in recent_wellness],
            "total_courses": len(courses),
            "avg_progress": sum(p.progress_percentage for p in progress) / len(progress) if progress else 0
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting user context: {e}")
        return {}

# Groq model configurations
GROQ_MODELS = {
    "llama3-8b-8192": {
        "name": "Llama 3 8B",
        "description": "Fast responses, good for quick interactions",
        "max_tokens": 8192,
        "best_for": ["chat", "quick_recommendations"]
    },
    "llama3-70b-8192": {
        "name": "Llama 3 70B", 
        "description": "Balanced performance and quality",
        "max_tokens": 8192,
        "best_for": ["detailed_analysis", "study_plans", "recommendations"]
    },
    "mixtral-8x7b-32768": {
        "name": "Mixtral 8x7B",
        "description": "Creative and detailed responses",
        "max_tokens": 32768,
        "best_for": ["creative_content", "long_form_analysis"]
    }
}
