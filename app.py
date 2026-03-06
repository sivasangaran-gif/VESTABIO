import os
import json
import re
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text # For WAL

# AI Integration
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'omnihealth_secure_key_2026'

# --- DATABASE CONFIG ---
basedir = os.path.abspath(os.path.dirname(__file__))
# SQLite with WAL mode setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'omnihealth_intelligence.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    food_name = db.Column(db.String(200), nullable=False)
    raw_text = db.Column(db.Text)
    has_image = db.Column(db.Boolean, default=False)

class SymptomLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    symptom_name = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False, default=25)
    height = db.Column(db.Float, nullable=False, default=170.0)
    weight = db.Column(db.Float, nullable=False, default=70.0)
    sex = db.Column(db.String(20), nullable=False, default='male')

# Enable WAL mode for high-speed read/writes
with app.app_context():
    db.create_all()
    with db.engine.connect() as con:
        con.execute(text('PRAGMA journal_mode=WAL;'))

# --- AI CONFIGURATION ---
if AI_AVAILABLE:
    genai.configure(api_key="AIzaSyDX4E8DQi5-HBfBMpnLXudQZz4GOzi0GBo")
    AI_MODEL_NAME = 'gemini-2.5-flash' 
else:
    AI_MODEL_NAME = None

def get_recent_history(user_email):
    # 72-hour sliding window
    cutoff_time = datetime.utcnow() - timedelta(hours=72)
    foods = FoodLog.query.filter(FoodLog.user_email == user_email, FoodLog.timestamp >= cutoff_time).order_by(FoodLog.timestamp.desc()).all()
    symptoms = SymptomLog.query.filter(SymptomLog.user_email == user_email, SymptomLog.timestamp >= cutoff_time).order_by(SymptomLog.timestamp.desc()).all()
    
    history_text = "--- Past 72 Hours Data for Context ---\n"
    if not foods and not symptoms:
        history_text += "No previous data logged in the last 72 hours.\n"
    else:
        if foods:
            history_text += "Foods Logged:\n"
            for f in foods:
                history_text += f"- {f.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}: {f.food_name} (Image uploaded: {f.has_image})\n"
        if symptoms:
            history_text += "\nSymptoms Logged:\n"
            for s in symptoms:
                history_text += f"- {s.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}: {s.symptom_name} (Severity: {s.severity}/5)\n"
    return history_text


# --- THE SYSTEM PROMPT ---
VESTA_BIO_PROMPT = """
🌐 VestaBio AI: Global Intelligence Super-Prompt
System Role: You are the VestaBio Engine, a high-performance Bio-Intelligence Architect. Your purpose is to bridge the gap between nutritional intake and systemic physiological responses through Temporal Correlation Mapping.

1. The Heuristic Logic (Bio-Temporal Engine)
Constraint: You operate on a 72-hour sliding window for all metabolic calculations.
Logic Flow:
Ingestion: Accept multi-modal inputs (Natural Language + Computer Vision).
Entity Extraction: Identify primary macronutrients and common allergens.
Temporal Weighting: Apply a Logarithmic Decay Function to correlations. Food consumed 2 hours before a symptom carries a 95% weight; food consumed 70 hours before carries a 5% weight. Compute personalized metabolic lag signature based on user history.
Normalization: Output a Metabolic Risk Index (MRI) on a scale of 0 <= MRI <= 100 based on predictive inflammation risk alerts.

2. Food Analysis & Recommendations
When analyzing food, estimate calories and macronutrients (Protein, Fiber, Fat, Carbohydrates).
Compare intake with recommended daily values and provide intelligent suggestions (e.g., "Your meal is low in protein. Add eggs or legumes.", "Fiber intake is insufficient. Include vegetables.", "Fat content is high. Reduce oily items.").
Generate a Meal Health Score (0-100).

3. The International Classification Matrix
Analyze and categorize all inputs based on the following Global Health Standards:
| Risk Tier | Index Range | Physiological Interpretation | Dashboard Action |
| --- | --- | --- | --- |
| Optimal | 0 - 29 | Homeostatic stability. | Blue/Green Pulse |
| Elevated | 30 - 59 | Acute inflammatory response detected. | Amber Warning |
| Critical | 60 - 100 | Chronic systemic dysregulation. | Red High-Frequency Alert |

4. The Neural Inference Prompt
When a user submits data, process it through this internal reasoning chain:
Semantic Parsing: Extract entities.
Correlation Calculus: Correlation Score = Sum(Severity * e^(-lambda * delta_t)). Establish 24-72 hour lag correlation between food and symptoms.
Actionable Insight: Do not just show data; provide a "Global Insight" regarding metabolic lag and predictive inflammation risk.

Now, based on the user's latest input and their provided 72-hour history:
Provide a JSON response *ONLY*, wrapped in NO markdown formatting. Your output must strictly follow this JSON schema:
{
    "mri": 45,
    "risk_tier": "Elevated",
    "dashboard_action": "Amber Warning",
    "entities_extracted": ["Dairy", "Caffeine"],
    "global_insight": "High correlation detected between Dairy intake and Level 3 fatigue.",
    "food_name": "Latte",
    "macronutrients": {
        "calories": 150,
        "protein": 5,
        "fiber": 0,
        "fat": 8,
        "carbs": 12
    },
    "suggestions": [
        "Your meal is low in protein. Add eggs or legumes."
    ],
    "health_score": 60
}
"""

def perform_omnibase_analysis(user_input, user_email, file_path=None):
    if not AI_AVAILABLE: return None
    try:
        model = genai.GenerativeModel(AI_MODEL_NAME, system_instruction=VESTA_BIO_PROMPT)
        history = get_recent_history(user_email)
        
        full_prompt = f"{history}\n--- Latest Input ---\n{user_input}\nProvide the requested JSON analysis strictly."
        print("Prompt sent:", full_prompt)
        
        if file_path:
            img = genai.upload_file(path=file_path)
            # YOLO verification constraint simulated via Gemini's multi-modal visual parsing
            response = model.generate_content([img, full_prompt])
        else:
            response = model.generate_content(full_prompt)
            
        print("AI Response:", response.text)
        
        # Robust JSON extraction
        json_str = response.text
        match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if match:
             json_str = match.group(0)
             
        # Sometimes AI adds markdown inside the JSON string
        json_str = json_str.replace("```json", "").replace("```", "").strip()
        
        parsed_data = json.loads(json_str)
        return parsed_data
    except Exception as e:
        print(f"AI Omni-Engine Error: {e}")
        return None

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', 'guest@omnihealth.ai')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_data'] = {
                'email': user.email,
                'age': user.age,
                'height': user.height,
                'weight': user.weight,
                'sex': user.sex
            }
            h = user.height / 100
            session['user_data']['bmi'] = round(user.weight / (h*h) if h > 0 else 0, 2)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials! Ensure you registered correctly.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        age = int(request.form.get('age', 25))
        height = float(request.form.get('height', 170))
        weight = float(request.form.get('weight', 70))
        sex = request.form.get('sex', 'male')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists!")
            return redirect(url_for('register'))
            
        new_user = User(email=email, password=password, age=age, height=height, weight=weight, sex=sex)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_data' not in session:
        return redirect(url_for('login'))

    user_email = session['user_data']['email']
    results = None
    
    profile = session['user_data']
    age = profile.get('age', 25)
    weight = profile.get('weight', 70)
    height = profile.get('height', 170)
    sex = profile.get('sex', 'male').lower()
    
    if sex == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
    daily_calories = round(bmr * 1.5)

    if request.method == 'POST':
        food_text = request.form.get('food', '')
        file = request.files.get('food_image')
        file_path = None
        has_img = False
        
        if file and file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)
            has_img = True
            
        if food_text or has_img:
            # Provide solid context if only an image is uploaded without text
            prompt_str = f"User ate: {food_text}" if food_text else "User uploaded this raw image of their meal for analysis."
            
            # First, fetch AI analysis
            results = perform_omnibase_analysis(prompt_str, user_email, file_path)
            
            # Then store in DB with complete context if possible
            if results:
                raw_text_enriched = f"{food_text} | AI Analysis: {json.dumps(results)}"
            else:
                raw_text_enriched = food_text
                
            food_name_eval = results.get('food_name', food_text or "Image Upload") if results else (food_text or "Image Upload")
            
            new_log = FoodLog(user_email=user_email, food_name=food_name_eval, raw_text=raw_text_enriched, has_image=has_img)
            db.session.add(new_log)
            db.session.commit()

    # Fetch recent food history
    history_food = FoodLog.query.filter_by(user_email=user_email).order_by(FoodLog.timestamp.desc()).limit(10).all()
    
    # Parse history_food to extract JSON if it exists
    parsed_history = []
    for f in history_food:
        entry = {
            'timestamp': f.timestamp,
            'food_name': f.food_name,
            'has_image': f.has_image,
            'details': None
        }
        if f.raw_text and " | AI Analysis: " in f.raw_text:
            try:
                parts = f.raw_text.split(" | AI Analysis: ")
                entry['details'] = json.loads(parts[1])
            except:
                pass
        parsed_history.append(entry)

    # Create lag chart data points for predictions (7 days)
    history_symptoms = SymptomLog.query.filter_by(user_email=user_email).order_by(SymptomLog.timestamp.desc()).limit(7).all()
    history_scores = [s.severity * 20 for s in reversed(history_symptoms)] # scale to 100
    if not history_scores:
        history_scores = [15, 25, 20, 30] 
        
    # Append the AI predicted MRI generated from the latest food
    if results and isinstance(results, dict) and 'mri' in results:
         history_scores.append(results['mri'])

    return render_template('dashboard.html', 
                           results=results, 
                           profile=session['user_data'],
                           history_scores=history_scores,
                           daily_calories=daily_calories,
                           food_history=parsed_history)

@app.route('/log_symptom', methods=['POST'])
def log_symptom():
    if 'user_data' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_data']['email']
    symptom_text = request.form.get('symptom_text', '')
    symptom_score = int(request.form.get('symptom_score', 1))
    
    if symptom_text:
        new_symptom = SymptomLog(user_email=user_email, symptom_name=symptom_text, severity=symptom_score)
        db.session.add(new_symptom)
        db.session.commit()
        
        # Fire AI analysis implicitly to get the insight
        results = perform_omnibase_analysis(f"User reported symptom: {symptom_text} with severity {symptom_score}/5", user_email)
        
        if results and 'global_insight' in results:
            flash({
                'insight': results['global_insight'],
                'mri': results.get('mri', 0),
                'risk': results.get('risk_tier', 'Optimal')
            })
        else:
            flash({'insight': "Symptom logged. Awaiting further temporal correlation."})
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_data', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)