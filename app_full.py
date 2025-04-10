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
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("You must be an admin to view this page.")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function
# -------------------- STUDENT SETUP FLOW --------------------
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
        # Save the new PIN
        student.pin_hash = generate_password_hash(request.form.get("pin"))

        # Save the passphrase as the second factor secret
        passphrase = request.form.get("second_factor_secret")
        if passphrase:
            student.second_factor_secret = passphrase
        else:
            flash("Passphrase is required.", "danger")
            return redirect(url_for('student_setup'))

        student.has_completed_setup = True
        db.session.commit()

        return redirect(url_for('setup_complete'))

    return render_template('student_setup.html', student=student)
# -------------------- STUDENT DASHBOARD --------------------
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    student = get_logged_in_student()
    transactions = Transaction.query.filter_by(student_id=student.id).order_by(Transaction.timestamp.desc()).all()
    purchases = Purchase.query.filter_by(student_id=student.id).all()
    return render_template('student_dashboard.html', student=student, transactions=transactions, purchases=purchases, now=datetime.now())

# -------------------- STUDENT LOGIN --------------------
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        qr_id = request.form.get('qr_id')
        pin = request.form.get('pin')
        student = Student.query.filter_by(qr_id=qr_id).first()

        if not student or not check_password_hash(student.pin_hash, pin):
            flash("Invalid credentials")
            return redirect(url_for('student_login'))

        session['student_id'] = student.id

        if not student.has_completed_setup:
            return redirect(url_for('student_setup'))

        return redirect(url_for('student_dashboard'))

    return render_template('student_login.html')
# -------------------- ADMIN DASHBOARD --------------------
@app.route('/admin')
@admin_required
def admin_dashboard():
    students = Student.query.order_by(Student.name).all()
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(20).all()
    return render_template('admin_dashboard.html', students=students, transactions=transactions)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # Replace with something more secure later!
        if username == "admin" and password == "bhu87ygv":
            session["is_admin"] = True
            flash("Admin login successful.")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials.")
            return redirect(url_for("admin_login"))
    return render_template("admin_login.html")

@app.route('/admin/logout')
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out.")
    return redirect(url_for("admin_login"))
if __name__ == '__main__':
    app.run(debug=True)
