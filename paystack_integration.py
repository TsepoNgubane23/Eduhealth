import requests
import json
import hmac
import hashlib
from flask import current_app
from datetime import datetime, timedelta

class PaystackPayment:
    """Paystack Payment Gateway Integration for EduHealth"""
    
    def __init__(self, public_key, secret_key):
        self.public_key = public_key
        self.secret_key = secret_key
        self.base_url = "https://api.paystack.co"
        
    def initialize_transaction(self, email, amount, plan_type, callback_url=None):
        """Initialize a payment transaction"""
        
        url = f"{self.base_url}/transaction/initialize"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        # Convert USD to ZAR (South African Rand) - approximate rate: 1 USD = 18 ZAR
        if isinstance(amount, str):
            amount = float(amount)
        amount_zar = amount * 18  # Convert USD to ZAR
        amount_cents = int(amount_zar * 100)  # Convert to cents for ZAR
        
        payload = {
            "email": email,
            "amount": amount_cents,
            "currency": "ZAR",
            "reference": f"eduhealth_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(email) % 10000}",
            "callback_url": callback_url or "http://127.0.0.1:5000/payment/success",
            "metadata": {
                "plan_type": plan_type,
                "platform": "eduhealth",
                "custom_fields": [
                    {
                        "display_name": "Plan Type",
                        "variable_name": "plan_type",
                        "value": plan_type
                    }
                ]
            },
            "channels": ["card", "bank", "ussd", "qr", "mobile_money", "bank_transfer"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status'):
                return response_data
            else:
                error_msg = response_data.get('message', 'Unknown error')
                current_app.logger.error(f"Paystack API Error: {response.status_code} - {error_msg}")
                current_app.logger.error(f"Payload sent: {payload}")
                return {"status": False, "message": error_msg, "error": str(response_data)}
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Paystack API Error: {e}")
            return {"status": False, "message": "Payment initialization failed", "error": str(e)}
    
    def verify_transaction(self, reference):
        """Verify a payment transaction"""
        
        url = f"{self.base_url}/transaction/verify/{reference}"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Paystack Verification Error: {e}")
            return {"status": False, "message": "Payment verification failed", "error": str(e)}
    
    def create_plan(self, name, amount, interval="monthly"):
        """Create a subscription plan"""
        
        url = f"{self.base_url}/plan"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        # Convert amount to kobo
        amount_kobo = int(float(amount) * 100)
        
        payload = {
            "name": name,
            "amount": amount_kobo,
            "interval": interval,
            "currency": "USD"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Paystack Plan Creation Error: {e}")
            return {"status": False, "message": "Plan creation failed", "error": str(e)}
    
    def create_subscription(self, customer_code, plan_code, authorization_code):
        """Create a subscription for a customer"""
        
        url = f"{self.base_url}/subscription"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "customer": customer_code,
            "plan": plan_code,
            "authorization": authorization_code
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Paystack Subscription Error: {e}")
            return {"status": False, "message": "Subscription creation failed", "error": str(e)}
    
    def verify_webhook_signature(self, payload, signature):
        """Verify Paystack webhook signature"""
        
        computed_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    
    def get_banks(self, country="NG"):
        """Get list of supported banks"""
        
        url = f"{self.base_url}/bank"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        params = {"country": country}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Paystack Banks Error: {e}")
            return {"status": False, "message": "Failed to fetch banks", "error": str(e)}

def init_paystack_payment():
    """Initialize Paystack payment gateway"""
    import os
    
    PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    
    if not PAYSTACK_PUBLIC_KEY or not PAYSTACK_SECRET_KEY:
        raise ValueError("Missing Paystack API keys in environment variables")
    
    return PaystackPayment(
        public_key=PAYSTACK_PUBLIC_KEY,
        secret_key=PAYSTACK_SECRET_KEY
    )

def handle_paystack_webhook(webhook_data, signature):
    """Handle Paystack webhook notifications"""
    
    try:
        paystack = init_paystack_payment()
        
        # Verify webhook signature
        payload = json.dumps(webhook_data, separators=(',', ':')).encode('utf-8')
        if not paystack.verify_webhook_signature(payload, signature):
            return {"status": "error", "message": "Invalid signature"}
        
        event = webhook_data.get('event')
        data = webhook_data.get('data', {})
        
        if event == 'charge.success':
            # Payment successful
            reference = data.get('reference')
            customer_email = data.get('customer', {}).get('email')
            amount = data.get('amount', 0) / 100  # Convert from kobo
            metadata = data.get('metadata', {})
            plan_type = metadata.get('plan_type', 'monthly')
            
            # Update user subscription in database
            from app import User, PaymentTransaction, db
            from datetime import datetime, timedelta
            
            user = User.query.filter_by(email=customer_email).first()
            if user:
                # Create payment record
                payment = PaymentTransaction(
                    user_id=user.id,
                    paystack_reference=reference,
                    amount=amount,
                    status='completed',
                    plan_type=plan_type
                )
                db.session.add(payment)
                
                # Update subscription
                if plan_type == 'annual':
                    user.subscription_type = 'premium'
                    user.subscription_expires = datetime.utcnow() + timedelta(days=365)
                else:  # monthly
                    user.subscription_type = 'premium'
                    user.subscription_expires = datetime.utcnow() + timedelta(days=30)
                
                db.session.commit()
                return {"status": "success", "message": "Subscription activated"}
        
        elif event == 'charge.failed':
            # Payment failed
            reference = data.get('reference')
            
            # Update payment record
            from app import PaymentTransaction, db
            
            payment = PaymentTransaction.query.filter_by(paystack_reference=reference).first()
            if payment:
                payment.status = 'failed'
                db.session.commit()
            
            return {"status": "failed", "message": "Payment failed"}
            
    except Exception as e:
        current_app.logger.error(f"Webhook processing error: {e}")
        return {"status": "error", "message": str(e)}
    
    return {"status": "processed"}

# JavaScript integration for frontend
PAYSTACK_FRONTEND_JS = """
// Paystack Frontend Integration
class PaystackPayment {
    constructor(publicKey) {
        this.publicKey = publicKey;
    }
    
    async initializePayment(paymentData) {
        try {
            // Initialize payment on backend
            const response = await fetch('/api/payment/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(paymentData)
            });
            
            const data = await response.json();
            
            if (data.status && data.data) {
                // Use Paystack Popup
                const handler = PaystackPop.setup({
                    key: this.publicKey,
                    email: paymentData.email,
                    amount: data.data.amount,
                    currency: 'USD',
                    ref: data.data.reference,
                    callback: function(response) {
                        // Payment successful
                        window.location.href = `/payment/success?reference=${response.reference}`;
                    },
                    onClose: function() {
                        // Payment cancelled
                        console.log('Payment cancelled');
                    }
                });
                
                handler.openIframe();
            } else {
                throw new Error(data.message || 'Payment initialization failed');
            }
        } catch (error) {
            console.error('Paystack payment error:', error);
            throw error;
        }
    }
}

// Usage in EduHealth app
const paystackPayment = new PaystackPayment('pk_test_your_public_key_here');

// Add to existing processPayment function in app.js
async function processPaymentWithPaystack() {
    const planSelect = document.getElementById('planSelect');
    const planType = planSelect.value;
    
    const paymentData = {
        email: app.currentUser.email,
        amount: planType === 'annual' ? 99.99 : 9.99,
        plan_type: planType,
        callback_url: window.location.origin + '/payment/callback'
    };
    
    try {
        await paystackPayment.initializePayment(paymentData);
    } catch (error) {
        app.showNotification('Payment processing failed: ' + error.message, 'error');
    }
}
"""

# Paystack plans configuration
PAYSTACK_PLANS = {
    "monthly": {
        "name": "EduHealth Premium Monthly",
        "amount": 9.99,
        "interval": "monthly",
        "description": "Monthly access to all premium features"
    },
    "annual": {
        "name": "EduHealth Premium Annual",
        "amount": 99.99,
        "interval": "annually", 
        "description": "Annual access to all premium features with 2 months free"
    }
}
