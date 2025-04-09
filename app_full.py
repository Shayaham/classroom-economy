from flask import Flask, render_template, request, jsonify, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship
import pytz
import pyotp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://timwonderer:Deduce-Python5-Customize@localhost/classroom_economy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '1%Inspiration&99%Effort'
db = SQLAlchemy(app)

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    qr_id = db.Column(db.String(100), unique=True, nullable=False)
    pin_hash = db.Column(db.String(256), nullable=False)
    block = db.Column(db.String(1), nullable=False)
    passes_left = db.Column(db.Integer, default=3)
    last_tap_in = db.Column(db.DateTime)
    last_tap_out = db.Column(db.DateTime)
    is_rent_enabled = db.Column(db.Boolean, default=True)
    is_property_tax_enabled = db.Column(db.Boolean, default=False)
    owns_seat = db.Column(db.Boolean, default=False)
    insurance_plan = db.Column(db.String, default="none")  # "none", "paycheck_protection", "personal_responsibility", "bundle"
    insurance_last_paid = db.Column(db.DateTime, nullable=True)
    second_factor_type = db.Column(db.String, nullable=True)
    second_factor_secret = db.Column(db.String, nullable=True)
    has_completed_setup = db.Column(db.Boolean, default=False)

    @property
    def checking_balance(self):
        return round(sum(tx.amount for tx in self.transactions
                     if tx.account_type == 'checking' and not tx.is_void), 2)

    @property
    def savings_balance(self):
        return round(sum(tx.amount for tx in self.transactions
                     if tx.account_type == 'savings' and not tx.is_void), 2)

    @property
    def total_earnings(self):
        return round(sum(tx.amount for tx in self.transactions if tx.amount > 0 and not tx.is_void), 2)

    @property
    def amount_needed_to_cover_bills(self):
        total_due = 0
        if self.is_rent_enabled:
            total_due += 800
        if self.is_property_tax_enabled and self.owns_seat:
            total_due += 120
        if self.insurance_plan != "none":
            total_due += 200  # Estimated insurance cost
        return max(0, total_due - self.checking_balance)

    @property
    def next_pay_date(self):
        from datetime import timedelta
        return (self.last_tap_in or datetime.utcnow()) + timedelta(days=14)

    transactions = db.relationship('Transaction', backref='student', lazy='dynamic')
    purchases = db.relationship('StorePurchase', backref='student', lazy='dynamic')

    def set_pin(self, new_pin):
        self.pin_hash = generate_password_hash(new_pin)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.Column(db.String(50))  # 'tap_in' or 'tap_out'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    type = db.Column(db.String(50))  # e.g., 'deposit', 'withdrawal', 'purchase', 'refund'
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    account_type = db.Column(db.String)  # "checking" or "savings"
    is_void = db.Column(db.Boolean, default=False)

class StorePurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    item_name = db.Column(db.String(100))
    used = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    policy_name = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return redirect('/student/login')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    qr_id = data.get('qr_id')
    pin = data.get('pin')
    action = data.get('action')

    student = Student.query.filter_by(qr_id=qr_id).first()
    if not student or not check_password_hash(student.pin_hash, pin):
        return jsonify({"status": "error", "message": "Invalid QR or PIN"})

    if action == 'tap_in' or action == 'tap_out':
        new_entry = Attendance(student_id=student.id, action=action)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"status": "success", "message": f"{action} recorded."})

    return jsonify({"status": "error", "message": "Unknown action."})

@app.route('/admin')
def admin():
    from sqlalchemy import desc
    pacific = pytz.timezone('US/Pacific')
    logs = Attendance.query.order_by(Attendance.timestamp.desc()).limit(20).all()
    transactions = Transaction.query.order_by(desc(Transaction.timestamp)).limit(20).all()

    # Convert timestamps to Pacific time
    for log in logs:
        log.timestamp = log.timestamp.astimezone(pacific)
    for tx in transactions:
        tx.timestamp = tx.timestamp.astimezone(pacific)

    # Create a dictionary of student_id → student object
    student_lookup = {s.id: s for s in Student.query.all()}

    return render_template(
        "admin_dashboard.html",
        logs=logs,
        transactions=transactions,
        student_lookup=student_lookup
    )

@app.route('/admin/students')
def admin_students():
    blocks = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    selected_block = request.args.get('block', 'A')
    students = Student.query.filter_by(block=selected_block).all()
    return render_template("admin_students.html", students=students, blocks=blocks, selected_block=selected_block)

@app.route('/admin/students/<int:student_id>')
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    transactions = Transaction.query.filter_by(student_id=student_id).order_by(Transaction.timestamp.desc()).all()
    attendance_logs = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.timestamp.desc()).all()
    purchases = StorePurchase.query.filter_by(student_id=student_id, used=False).all()
    insurance = Insurance.query.filter_by(student_id=student_id, active=True).all()

    return render_template(
        "student_detail.html",
        student=student,
        transactions=transactions,
        attendance_logs=attendance_logs,
        purchases=purchases,
        insurance=insurance
    )

@app.route('/admin/students/<int:student_id>/bills', methods=['POST'])
def update_bills(student_id):
    student = Student.query.get_or_404(student_id)

    student.is_rent_enabled = 'rent' in request.form
    student.is_property_tax_enabled = 'property_tax' in request.form
    student.is_insurance_enabled = 'insurance' in request.form

    db.session.commit()

    return redirect(f'/admin/students/{student_id}')

@app.route('/admin/bonuses', methods=['POST'])
def post_bonus():
    title = request.form['title']
    amount = float(request.form['amount'])
    tx_type = request.form['type']

    students = Student.query.all()
    for student in students:
        tx = Transaction(
            student_id=student.id,
            amount=amount,
            type=tx_type,
            account_type="checking",
            description=title
        )
        db.session.add(tx)

    db.session.commit()
    return redirect('/admin')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        qr_id = request.form['qr_id']
        pin = request.form['pin']

        student = Student.query.filter_by(qr_id=qr_id).first()
        if student and check_password_hash(student.pin_hash, pin):
            session['student_id'] = student.id
            return redirect('/student/dashboard')
        else:
            return render_template('student_login.html', error="Invalid ID or PIN.")

    return render_template('student_login.html')

@app.route('/student/dashboard')
def student_dashboard():
    student_id = session.get('student_id')
    if not student_id:
        return redirect('/student/login')
    student = Student.query.get(student_id)
    if not student.has_completed_setup:
        return redirect('/student/setup')
    pacific = pytz.timezone('US/Pacific')
    now = datetime.now(pacific)
    return render_template('student_dashboard.html', student=student, now=now)

@app.route('/student/logout')
def student_logout():
    session.pop('student_id', None)
    return redirect('/student/login')

@app.route('/admin/transactions/<int:tx_id>/void', methods=['POST'])
def void_transaction(tx_id):
    tx = Transaction.query.get_or_404(tx_id)

    if tx.is_void:
        return "Transaction already voided", 400

    tx.is_void = True

    refund = Transaction(
        student_id=tx.student_id,
        amount=-tx.amount,
        type='refund',
        account_type=tx.account_type,
        description=f"VOID: {tx.description}",	
        is_void=True
    )

    db.session.add(refund)
    db.session.commit()

@app.route('/student/setup', methods=['GET', 'POST'])
def student_setup():
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('student_login'))

    student = Student.query.get(student_id)
    if not student or student.has_completed_setup:
        return redirect(url_for('student_dashboard'))

    error = None
    second_factor_type = None

    if request.method == 'POST':
        new_pin = request.form.get('new_pin')
        second_factor_type = request.form.get('second_factor_type')

        if not new_pin or not second_factor_type:
            error = 'Please enter a PIN and choose a second factor.'
        elif not new_pin.isdigit() or not (4 <= len(new_pin) <= 6):
            error = 'PIN must be 4–6 digits.'
        else:
            student.pin_hash = generate_password_hash(new_pin)
            student.second_factor_type = second_factor_type

            # Route to TOTP setup if selected
            if second_factor_type == 'totp':
                db.session.commit()
                return redirect(url_for('student_setup_totp'))

            # Future: Add passkey route here
            if second_factor_type == 'passkey':
                db.session.commit()
                return redirect(url_for('student_setup_passkey'))

            student.has_completed_setup = True
            db.session.commit()
            return redirect(url_for('student_dashboard'))

    return render_template('student_setup.html', student=student, error=error)
@app.route('/student/setup/totp', methods=['GET', 'POST'])
def student_setup_totp():
    print("🔍 Reached /student/setup/totp route")

    student_id = session.get('student_id')
    print(f"📌 session['student_id']: {student_id}")
    if not student_id:
        return redirect('/student/login')

    student = Student.query.get(student_id)
    print(f"📘 Loaded student: {student}")

    if not student:
        print("⚠️ No student found.")
        return redirect('/student/login')

    print(f"🔐 student.second_factor_type: {student.second_factor_type}")
    if student.second_factor_type != 'totp':
        return redirect('/student/setup')

    if not student.second_factor_secret:
        print("🔧 Generating new TOTP secret")
        student.second_factor_secret = pyotp.random_base32()
        db.session.commit()

    totp = pyotp.TOTP(student.second_factor_secret)
    email = student.email or "unknown@domain.com"
    print(f"📧 Using email: {email}")
    totp_uri = totp.provisioning_uri(name=email, issuer_name="Classroom Economy")

    if request.method == 'POST':
        print("📝 POST request received")
        code = request.form.get('code')
        print(f"🔢 Code entered: {code}")
        if totp.verify(code):
            print("✅ TOTP verified successfully")
            student.has_completed_setup = True
            db.session.commit()
            return redirect('/student/dashboard')
        else:
            print("❌ Invalid TOTP code")
            error = "Invalid code. Please try again."
            return render_template('student_setup_totp.html', student=student, totp_uri=totp_uri, error=error)

    print("📄 Rendering TOTP setup page (GET)")
    return render_template('student_setup_totp.html', student=student, totp_uri=totp_uri)
import urllib.parse

@app.template_filter('urlencode')
def urlencode_filter(s):
    return urllib.parse.quote_plus(s)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
