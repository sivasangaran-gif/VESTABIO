# 🧬 VestaBio — Metabolic Intelligence Platform

**VestaBio** is an advanced health-tech web application that bridges the gap between nutrition and physiological symptoms. By leveraging generative AI and longitudinal data tracking, VestaBio helps users uncover the "metabolic lag" between foods they consume and symptoms they experience — turning complex biological patterns into actionable wellness insights.

Project Website : https://sivasangaran-gif.github.io/VESTABIOWEB/

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📸 **AI Food Analysis** | Upload a meal photo or describe it in text; Gemini AI estimates macronutrients, fiber, and a personalized health score |
| 🌡️ **Symptom Tracker** | Log symptoms (bloating, fatigue, brain fog, etc.) with severity ratings |
| 🔍 **Metabolic Lag Engine** | Detects 24–72 hour correlations between dietary triggers and symptom spikes |
| 📊 **Personalized Dashboard** | Visualize calorie trends and nutrient breakdowns with interactive Chart.js graphs |
| 🧑 **User Profiles** | Tailored nutritional goals based on age, height, weight, and sex |
| 🔐 **Secure Auth** | Account registration and login with bcrypt password hashing and session management |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
- **Database**: SQLite (WAL mode for high-speed concurrent reads/writes)
- **AI Engine**: Google Gemini API via `google-genai` SDK
- **Frontend**: HTML5, Vanilla CSS (Dark-mode UI), Chart.js
- **Forms**: Flask-WTF, WTForms

---

## 📂 Project Structure

```
VESTABIO/
├── app.py              # Main Flask application, routes & business logic
├── ai_engine.py        # Metabolic intelligence & AI integration layer
├── models.py           # Database models (User, FoodLog, SymptomLog)
├── requirements.txt    # Python dependencies
├── static/             # CSS, JS, and user-uploaded meal images
├── templates/          # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── instance/           # Local SQLite database (auto-generated)
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd VESTABIO
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Activate on Windows:
.\venv\Scripts\activate

# Activate on Linux / macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API Key
In `app.py`, locate the AI configuration section and replace the placeholder key, or use a `.env` file:
```python
# app.py
genai.configure(api_key="YOUR_GEMINI_API_KEY")
```
> You can get a free API key from [Google AI Studio](https://aistudio.google.com/).

### 5. Run the application
```bash
python app.py
```
The app will start at **http://127.0.0.1:5000** in debug mode.

---

## 🖥️ Usage

1. **Register** a new account with your health profile (age, height, weight).
2. **Log a meal** via the dashboard — type the food name or upload a photo.
3. **Log symptoms** after meals to start building your personal metabolic history.
4. **Review insights** on the dashboard — the AI engine will correlate patterns over time.

---

## 🔮 Roadmap

- [ ] Real-time Gemini Vision integration for food image recognition
- [ ] CGM & wearable device data sync
- [ ] AI-powered recipe optimizer to reduce inflammation risk
- [ ] Export health reports as PDF

---

*Built with ❤️ for the VestaBio Health Intelligence Initiative.*

