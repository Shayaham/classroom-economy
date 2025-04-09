from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import pytz
import pyotp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://timwonderer:Deduce-Python5-Customize@localhost/classroom_economy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '1%Inspiration&99%Effort'
db = SQLAlchemy(app)

# -------------------- MODELS --------------------
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
    insurance_plan = db.Column(db.String, default="none")
    insurance_last_paid = db.Column(db.DateTime, nullable=True)
    second_factor_type = db.Column(db.String, nullable=True)
    second_factor_secret = db.Column(db.String, nullable=True)
    second_factor_enabled = db.Column(db.Boolean, default=False)
    has_completed_setup = db.Column(db.Boolean, default=False)

    transactions = db.relationship('Transaction', backref='student', lazy=True)
    purchases = db.relationship('Purchase', backref='student', lazy=True)

    @property
    def checking_balance(self):
        return round(sum(tx.amount for tx in self.transactions if tx.account_type == 'checking' and not tx.is_void), 2)

    @property
    def savings_balance(self):
        return round(sum(tx.amount for tx in self.transactions if tx.account_type == 'savings' and not tx.is_void), 2)

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
        return round(sum(tx.amount for tx in self.transactions if tx.amount > 0 and not tx.is_void), 2)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    account_type = db.Column(db.String(20), default='checking')
    description = db.Column(db.String(255))
    is_void = db.Column(db.Boolean, default=False)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    item_name = db.Column(db.String(100))
    redeemed = db.Column(db.Boolean, default=False)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- AUTH HELPERS --------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_logged_in_student():
    return Student.query.get(session['student_id']) if 'student_id' in session else None

# -------------------- STUDENT SETUP FLOW --------------------
@app.route('/setup-totp', methods=['GET', 'POST'])
@login_required
def setup_totp():
    student = get_logged_in_student()
    if request.method == 'POST':
        token = request.form.get('totp_token')
        if pyotp.TOTP(student.second_factor_secret).verify(token):
            student.second_factor_enabled = True
            student.has_completed_setup = True
            db.session.commit()
            flash("TOTP setup complete!")
            return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid token. Please try again.")

    if not student.second_factor_secret:
        student.second_factor_secret = pyotp.random_base32()
        db.session.commit()

    totp_uri = pyotp.TOTP(student.second_factor_secret).provisioning_uri(
        name=student.email, issuer_name="Classroom Economy"
    )
    return render_template('student_setup_totp.html', student=student, totp_uri=totp_uri)

@app.route('/setup-passphrase')
@login_required
def setup_passphrase():
    student = get_logged_in_student()
    student.has_completed_setup = True
    db.session.commit()
    return render_template('student_setup_passphrase.html', student=student)

@app.route('/setup-complete')
@login_required
def setup_complete():
    student = get_logged_in_student()
    student.has_completed_setup = True
    db.session.commit()
    return render_template('student_setup_complete.html')

@app.route('/student/setup', methods=['GET', 'POST'])
@login_required
def student_setup():
    student = get_logged_in_student()
    if request.method == 'POST':
        student.pin_hash = generate_password_hash(request.form.get("pin"))
        student.second_factor_type = request.form.get("second_factor")
        if student.second_factor_type == "passphrase":
            student.second_factor_secret = request.form.get("second_factor_secret")
        db.session.commit()

        if student.second_factor_type == "totp":
            return redirect(url_for('setup_totp'))
        elif student.second_factor_type == "passphrase":
            return redirect(url_for('setup_passphrase'))
        else:
            return redirect(url_for('setup_complete'))

    return render_template('student_setup.html', student=student)

# -------------------- STUDENT DASHBOARD --------------------
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    student = get_logged_in_student()
    transactions = Transaction.query.filter_by(student_id=student.id).order_by(Transaction.timestamp.desc()).all()
    purchases = Purchase.query.filter_by(student_id=student.id).all()
    return render_template('student_dashboard.html', student=student, transactions=transactions, purchases=purchases)

# -------------------- STUDENT LOGIN --------------------
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        qr_id = request.form.get('qr_id')
        pin = request.form.get('pin')
        student = Student.query.filter_by(qr_id=qr_id).first()
        if student and check_password_hash(student.pin_hash, pin):
            session['student_id'] = student.id
            flash("Logged in successfully.")
            return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid credentials.")
    return render_template('student_login.html')

# -------------------- ADMIN DASHBOARD --------------------
@app.route('/admin')
def admin_dashboard():
    students = Student.query.order_by(Student.name).all()
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(20).all()
    return render_template('admin_dashboard.html', students=students, transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)
