import requests
import json
from flask import current_app

class IntaSendPayment:
    """IntaSend Payment Gateway Integration for EduHealth"""
    
    def __init__(self, publishable_key, secret_key, test_mode=True):
        self.publishable_key = publishable_key
        self.secret_key = secret_key
        self.test_mode = test_mode
        self.base_url = "https://sandbox.intasend.com" if test_mode else "https://payment.intasend.com"
        
    def create_checkout_session(self, amount, currency="USD", email=None, phone_number=None, 
                               first_name=None, last_name=None, redirect_url=None):
        """Create a checkout session for payment processing"""
        
        url = f"{self.base_url}/api/v1/checkout/"
        
        headers = {
            'Content-Type': 'application/json',
            'X-IntaSend-Public-Key-Test' if self.test_mode else 'X-IntaSend-Public-Key': self.publishable_key,
            'X-IntaSend-Secret-Key-Test' if self.test_mode else 'X-IntaSend-Secret-Key': self.secret_key
        }
        
        payload = {
            "public_key": self.publishable_key,
            "amount": amount,
            "currency": currency,
            "method": "CARD-PAYMENT",
            "api_ref": f"eduhealth_{email}_{amount}",  # Unique reference
            "email": email,
            "phone_number": phone_number,
            "first_name": first_name,
            "last_name": last_name,
            "redirect_url": redirect_url or "https://yourdomain.com/payment/success",
            "comment": "EduHealth Premium Subscription"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"IntaSend API Error: {e}")
            return {"error": "Payment processing failed", "details": str(e)}
    
    def verify_payment(self, checkout_id):
        """Verify payment status"""
        
        url = f"{self.base_url}/api/v1/checkout/{checkout_id}/"
        
        headers = {
            'Content-Type': 'application/json',
            'X-IntaSend-Public-Key-Test' if self.test_mode else 'X-IntaSend-Public-Key': self.publishable_key,
            'X-IntaSend-Secret-Key-Test' if self.test_mode else 'X-IntaSend-Secret-Key': self.secret_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"IntaSend Verification Error: {e}")
            return {"error": "Payment verification failed", "details": str(e)}
    
    def process_mobile_payment(self, amount, phone_number, currency="KES", method="M-PESA"):
        """Process mobile money payment (M-PESA, etc.)"""
        
        url = f"{self.base_url}/api/v1/payment/mpesa-stk-push/"
        
        headers = {
            'Content-Type': 'application/json',
            'X-IntaSend-Public-Key-Test' if self.test_mode else 'X-IntaSend-Public-Key': self.publishable_key,
            'X-IntaSend-Secret-Key-Test' if self.test_mode else 'X-IntaSend-Secret-Key': self.secret_key
        }
        
        payload = {
            "public_key": self.publishable_key,
            "amount": amount,
            "phone_number": phone_number,
            "currency": currency,
            "api_ref": f"eduhealth_mobile_{phone_number}_{amount}",
            "comment": "EduHealth Premium Subscription"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"IntaSend Mobile Payment Error: {e}")
            return {"error": "Mobile payment processing failed", "details": str(e)}

# Example usage and integration with Flask app
def init_intasend_payment():
    """Initialize IntaSend payment gateway"""
    # In production, these should be environment variables
    INTASEND_PUBLISHABLE_KEY = "ISPubKey_test_your_key_here"
    INTASEND_SECRET_KEY = "ISSecretKey_test_your_secret_here"
    
    return IntaSendPayment(
        publishable_key=INTASEND_PUBLISHABLE_KEY,
        secret_key=INTASEND_SECRET_KEY,
        test_mode=True  # Set to False in production
    )

# Webhook handler for payment notifications
def handle_intasend_webhook(webhook_data):
    """Handle IntaSend webhook notifications"""
    
    try:
        # Verify webhook signature (implement signature verification)
        # Update user subscription status based on payment status
        
        checkout_id = webhook_data.get('checkout_id')
        status = webhook_data.get('status')
        api_ref = webhook_data.get('api_ref')
        
        if status == 'COMPLETE':
            # Payment successful - activate subscription
            # Extract user email from api_ref
            parts = api_ref.split('_')
            if len(parts) >= 2:
                email = parts[1]
                amount = parts[2]
                
                # Update user subscription in database
                from app import User, db
                user = User.query.filter_by(email=email).first()
                if user:
                    if float(amount) >= 99.99:  # Annual subscription
                        user.subscription_type = 'premium'
                        user.subscription_expires = datetime.utcnow() + timedelta(days=365)
                    else:  # Monthly subscription
                        user.subscription_type = 'premium'
                        user.subscription_expires = datetime.utcnow() + timedelta(days=30)
                    
                    db.session.commit()
                    return {"status": "success", "message": "Subscription activated"}
        
        elif status == 'FAILED':
            # Payment failed - handle accordingly
            return {"status": "failed", "message": "Payment failed"}
            
    except Exception as e:
        current_app.logger.error(f"Webhook processing error: {e}")
        return {"status": "error", "message": str(e)}
    
    return {"status": "processed"}

# JavaScript integration for frontend
INTASEND_FRONTEND_JS = """
// IntaSend Frontend Integration
class IntaSendPayment {
    constructor(publicKey) {
        this.publicKey = publicKey;
        this.intasend = new IntaSend();
        this.intasend.init(publicKey);
    }
    
    async processCardPayment(paymentData) {
        try {
            const response = await this.intasend.checkout({
                public_key: this.publicKey,
                amount: paymentData.amount,
                currency: paymentData.currency || 'USD',
                email: paymentData.email,
                first_name: paymentData.firstName,
                last_name: paymentData.lastName,
                phone_number: paymentData.phoneNumber,
                redirect_url: paymentData.redirectUrl
            });
            
            return response;
        } catch (error) {
            console.error('IntaSend payment error:', error);
            throw error;
        }
    }
    
    async processMobilePayment(paymentData) {
        try {
            const response = await this.intasend.mpesaSTKPush({
                public_key: this.publicKey,
                amount: paymentData.amount,
                phone_number: paymentData.phoneNumber,
                currency: paymentData.currency || 'KES'
            });
            
            return response;
        } catch (error) {
            console.error('IntaSend mobile payment error:', error);
            throw error;
        }
    }
}

// Usage in EduHealth app
const intasendPayment = new IntaSendPayment('ISPubKey_test_your_key_here');

// Add to existing processPayment function in app.js
async function processPaymentWithIntaSend() {
    const planSelect = document.getElementById('planSelect');
    const planType = planSelect.value;
    
    const paymentData = {
        amount: planType === 'annual' ? 99.99 : 9.99,
        currency: 'USD',
        email: app.currentUser.email,
        firstName: app.currentUser.name.split(' ')[0],
        lastName: app.currentUser.name.split(' ').slice(1).join(' '),
        redirectUrl: window.location.origin + '/payment/success'
    };
    
    try {
        const response = await intasendPayment.processCardPayment(paymentData);
        
        if (response.checkout_url) {
            // Redirect to IntaSend checkout page
            window.location.href = response.checkout_url;
        } else {
            throw new Error('No checkout URL received');
        }
    } catch (error) {
        app.showNotification('Payment processing failed: ' + error.message, 'error');
    }
}
"""
