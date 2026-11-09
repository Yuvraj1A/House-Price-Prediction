from flask import Flask, render_template, request, redirect, session, make_response, jsonify
import pickle
import numpy as np
from flask_sqlalchemy import SQLAlchemy
import io
from reportlab.pdfgen import canvas

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

# 🔐 SESSION
app.secret_key = "realestate_secret_key"

# 🟢 DB CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 🤖 OPENAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- USER ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# ---------------- HISTORY ----------------
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    crim = db.Column(db.Float)
    rm = db.Column(db.Float)
    price = db.Column(db.Float)
    roi = db.Column(db.Float)
    location = db.Column(db.String(100))

# ---------------- MODEL ----------------
model = pickle.load(open("model.pkl", "rb"))

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect('/login')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template("index.html", user=session['user'])

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            session['user'] = user.username
            return redirect('/dashboard')

        return "Invalid Credentials"

    return render_template("login.html")

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        db.session.add(User(
            username=request.form['username'],
            password=request.form['password']
        ))
        db.session.commit()
        return redirect('/login')

    return render_template("signup.html")

# ---------------- ✅ FIXED PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect('/login')

    try:
        # 🔥 fetch inputs
        CRIM = float(request.form['CRIM'])
        ZN = float(request.form['ZN'])
        INDUS = float(request.form['INDUS'])
        CHAS = float(request.form['CHAS'])
        NOX = float(request.form['NOX'])
        RM = float(request.form['RM'])
        AGE = float(request.form['AGE'])
        DIS = float(request.form['DIS'])
        RAD = float(request.form['RAD'])
        TAX = float(request.form['TAX'])
        PTRATIO = float(request.form['PTRATIO'])
        B = float(request.form['B'])
        LSTAT = float(request.form['LSTAT'])

        location = request.form.get("location")

        # 🔥 model input
        features = np.array([[CRIM, ZN, INDUS, CHAS, NOX, RM, AGE,
                              DIS, RAD, TAX, PTRATIO, B, LSTAT]])

        prediction = model.predict(features)

        price = float(prediction[0]) * 1000
        if price < 0:
          price = abs(price)
        future_price = price * 1.15
        roi = 15.0
          # 🔥 AI INSIGHT (IMPORTANT)
        ai_text = f"""
📍 Location: {location}

🏠 Estimated Property Price: ₹{round(price,2):,}

📈 Expected growth in next 5 years is strong.
ROI is around {roi}% which makes it a good investment opportunity.

💡 Recommendation: Suitable for long-term investment.
"""

        # 🔥 SAVE HISTORY (FIXED)
        record = History(
            username=session['user'],
            crim=CRIM,
            rm=RM,
            price=price,
            roi=roi,
            location=location
        )

        db.session.add(record)
        db.session.commit()

        return render_template("index.html",
            prediction=f"{round(price, 2):,}",
            future_price=f"{round(future_price, 2):,}",
            roi=roi,
            location=location,
            ai_text=ai_text,
            user=session['user']
        )
    except KeyError as e:
        return f"Missing Form Field: {str(e)}"

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a real estate AI assistant."},
            {"role": "user", "content": msg}
        ]
    )

    return jsonify({"reply": response.choices[0].message.content})

# ---------------- ✅ FIXED HISTORY ----------------
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/login')

    records = History.query.filter_by(username=session['user']).all()

    # 🔥 convert to JSON safe
    data = [{
        "crim": r.crim,
        "rm": r.rm,
        "price": r.price,
        "roi": r.roi,
        "location": r.location
    } for r in records]

    return render_template("history.html", data=data)

# ---------------- PDF ----------------
@app.route('/download-pdf')
def download_pdf():
    if 'user' not in session:
        return redirect('/login')

    data = History.query.filter_by(username=session['user']).all()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    y = 800
    for d in data:
        p.drawString(50, y, f"{d.location} | ₹{d.price} | ROI {d.roi}%")
        y -= 20

    p.save()
    buffer.seek(0)

    return make_response(buffer.read(), {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename=report.pdf'
    })

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- RUN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
