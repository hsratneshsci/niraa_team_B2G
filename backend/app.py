from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from models import db, User, Income
from services.scoring import calculate_kazhai_score
from services.nlp import extract_amount, process_chat_gemini, recommend_jobs
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kazhai-secret-key-48hr-mvp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kazhai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    if not phone:
        flash("Phone number required")
        return redirect(url_for('index'))
    
    # Mock Auth: Create user if not exists
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(phone=phone)
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('index'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date).all()
    income_data = [{'date': i.date, 'amount': i.amount} for i in incomes]
    score_data = calculate_kazhai_score(income_data)
    chart_data = [{'date': i.date.strftime('%Y-%m-%d'), 'amount': i.amount} for i in incomes]

    return render_template('dashboard.html', user=user, score=score_data, income_history=chart_data)

@app.route('/log_income')
def log_income():
    if 'user_id' not in session: return redirect(url_for('index'))
    return render_template('log_income.html')

@app.route('/ledger')
def ledger():
    if 'user_id' not in session: return redirect(url_for('index'))
    user_id = session['user_id']
    # Sort by date desc for ledger view
    incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc()).all()
    return render_template('ledger.html', incomes=incomes)

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('index'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    incomes = Income.query.filter_by(user_id=user_id).all()
    income_data = [{'date': i.date, 'amount': i.amount} for i in incomes]
    score_data = calculate_kazhai_score(income_data)
    
    return render_template('profile.html', user=user, score=score_data)

@app.route('/api/income/add', methods=['POST'])
def add_income():
    if 'user_id' not in session: return redirect(url_for('index'))

    text = request.form.get('text')
    amount = extract_amount(text)
    
    if amount > 0:
        new_income = Income(
            user_id=session['user_id'],
            amount=amount,
            description=text,
            hash_signature="hash_placeholder"
        )
        new_income.hash_signature = new_income.calculate_hash()
        db.session.add(new_income)
        db.session.commit()
    
    return redirect(url_for('ledger')) # Redirect to ledger to see the entry

@app.route('/skill_match')
def skill_match():
    if 'user_id' not in session: return redirect(url_for('index'))
    return render_template('skill_match.html')

@app.route('/api/skill/chat', methods=['POST'])
def chat():
    data = request.json
    text = data.get('message', '')
    
    # New logic: Process chat using Gemini (or fallback)
    skills, reply = process_chat_gemini(text)
    
    # Get job recommendations solely based on extracted skills
    jobs = recommend_jobs(skills)
    
    return jsonify({
        "skills": skills,
        "jobs": jobs,
        "reply": reply
    })

@app.route('/report/download')
def download_report():
    if 'user_id' not in session: return redirect(url_for('index'))
        
    user = User.query.get(session['user_id'])
    incomes = Income.query.filter_by(user_id=user.id).order_by(Income.date.desc()).all()
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"KazhaiAI Income Ledger - {user.phone}")
    
    p.setFont("Helvetica", 12)
    y = 700
    p.drawString(100, y, "Date")
    p.drawString(250, y, "Description")
    p.drawString(500, y, "Amount")
    
    y -= 20
    p.line(100, y, 550, y)
    y -= 20
    
    total = 0
    for income in incomes:
        p.drawString(100, y, income.date.strftime('%Y-%m-%d'))
        p.drawString(250, y, income.description[:40])
        p.drawString(500, y, f"Rs. {income.amount}")
        total += income.amount
        y -= 20
        if y < 50:
            p.showPage()
            y = 750
            
    p.line(100, y, 550, y)
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y, f"Total Verified Income: Rs. {total}")
    
    p.save()
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"ledger_{user.phone}.pdf", mimetype='application/pdf')

# Create DB if not exists
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
