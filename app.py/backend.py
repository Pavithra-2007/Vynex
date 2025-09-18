from flask import Flask, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Requests

# Mock user database
users = {
    "testuser": {"password": "password123", "name": "Test User", "email": "test@example.com", "age": 30, "income": 50000}
}

# Mock financial data
financial_data = {
    "monthly_income": 5000,
    "monthly_expenses": {"Housing": 1500, "Food": 600, "Transport": 300, "Entertainment": 200},
    "monthly_savings": 1000,
    "total_savings": 15000,
    "budget": {
        "total_budget": 4000,
        "actual_spending": 3200,
        "category_budget": {"Housing": 1600, "Food": 800, "Transport": 400, "Entertainment": 400, "Utilities": 300, "Other": 500},
        "category_actual": {"Housing": 1500, "Food": 600, "Transport": 300, "Entertainment": 200, "Utilities": 280, "Other": 320}
    },
    "budget_summary": "Your spending is well-controlled. You're saving 20% of your income, which is excellent. Consider investing your savings for better returns.",
    "spending_analysis": {
        "transactions": [
            {"date": "2023-10-01", "amount": 1500, "category": "Housing", "description": "Rent"},
            {"date": "2023-10-05", "amount": 200, "category": "Food", "description": "Groceries"},
            {"date": "2023-10-10", "amount": 100, "category": "Transport", "description": "Gas"},
            {"date": "2023-10-15", "amount": 150, "category": "Entertainment", "description": "Dinner Out"}
        ],
        "category_totals": {"Housing": 1500, "Food": 600, "Transport": 300, "Entertainment": 200},
        "insights": [
            "You're spending 30% of your income on housing, which is within the recommended range.",
            "Your food expenses are well-controlled at 12% of income.",
            "Consider meal prepping to reduce your dining out expenses."
        ]
    }
}

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users and users[username]['password'] == password:
        return jsonify({"access_token": "mock_token_12345", "token_type": "bearer"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/user/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != "mock_token_12345":
        return jsonify({"error": "Invalid token"}), 401
    
    username = "testuser"  # In a real app, you'd decode this from the token
    return jsonify(users[username])

@app.route('/user/profile', methods=['PUT'])
def update_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != "mock_token_12345":
        return jsonify({"error": "Invalid token"}), 401
    
    data = request.get_json()
    users["testuser"].update(data)
    return jsonify({"message": "Profile updated successfully"})

@app.route('/financial/data', methods=['GET'])
def get_financial_data():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != "mock_token_12345":
        return jsonify({"error": "Invalid token"}), 401
    
    return jsonify(financial_data)

@app.route('/chat', methods=['POST'])
def chat():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != "mock_token_12345":
        return jsonify({"error": "Invalid token"}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Simple mock responses
    responses = [
        "I've analyzed your financial data. Based on your spending patterns, I recommend increasing your emergency fund to 3 months of expenses.",
        "Looking at your budget, I suggest reducing entertainment expenses by 15% to meet your savings goals faster.",
        "Your financial health is improving! Consider setting up automatic transfers to your savings account."
    ]
    
    return jsonify({"response": random.choice(responses)})

@app.route('/upload/statement', methods=['POST'])
def upload_statement():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != "mock_token_12345":
        return jsonify({"error": "Invalid token"}), 401
    
    # Simulate processing time
    import time
    time.sleep(2)
    
    return jsonify({"message": "Statement processed successfully"})

@app.route('/ai/analyze/sentiment', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    text = data.get('text', '')
    
    # Mock sentiment analysis
    sentiments = ['positive', 'neutral', 'negative']
    scores = [0.8, 0.6, 0.4]
    
    return jsonify({
        "sentiment": random.choice(sentiments),
        "score": random.choice(scores),
        "keywords": ["savings", "investment", "budget"][:random.randint(1, 3)]
    })

@app.route('/ai/analyze/document', methods=['POST'])
def analyze_document():
    # Mock document analysis
    return jsonify({
        "insights": [
            "You're spending 25% of income on dining out - consider reducing this",
            "Your savings rate has improved by 5% compared to last month",
            "Detected recurring subscriptions that could be optimized"
        ],
        "recommendations": [
            "Set up automatic transfers to savings account",
            "Review subscription services for potential savings",
            "Consider refinancing your mortgage given current rates"
        ]
    })

@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    message = data.get('message', '')
    
    # Mock AI responses based on message content
    if 'budget' in message.lower():
        response = "Based on your spending patterns, I recommend allocating more funds to your emergency fund."
    elif 'investment' in message.lower():
        response = "Considering your risk profile, a 60/40 stock/bond allocation might be appropriate."
    else:
        responses = [
            "I've analyzed your financial situation and suggest increasing your retirement contributions.",
            "Your spending habits show good discipline. Consider investing your surplus cash.",
            "I recommend building a 6-month emergency fund before pursuing aggressive investments."
        ]
        response = random.choice(responses)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=8000)