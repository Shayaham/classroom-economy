#!/usr/bin/env python3
"""
Comprehensive database seeding script for multi-tenancy testing.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pyotp
import secrets

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models import Admin, Student, TeacherBlock
from werkzeug.security import generate_password_hash
from hash_utils import hash_username_lookup, get_random_salt
from app.utils.join_code import generate_join_code  # ← Fixed import

app = create_app()

def create_teacher(username: str, totp_secret: str) -> Admin:
    teacher = Admin(username=username, totp_secret=totp_secret)
    db.session.add(teacher)
    return teacher

def create_student_with_seat(first_name: str, last_initial: str, birth_year: int, block: str, teacher: Admin):
    """Create a student AND their claimed TeacherBlock seat."""
    dob_sum = sum(int(d) for d in str(birth_year))
    username = f"{first_name.lower()}{last_initial.lower()}{dob_sum}"
    pin = f"{first_name[0].upper()}{dob_sum}"
    
    salt = get_random_salt()
    unique_suffix = secrets.token_hex(16)
    
    # Create the student
    student = Student(
        first_name=first_name,
        last_initial=last_initial,
        dob_sum=dob_sum,
        block=block,
        salt=salt,
        teacher_id=teacher.id,
        username_lookup_hash=hash_username_lookup(username),
        pin_hash=generate_password_hash(pin),
        has_completed_setup=True,
        first_half_hash=f"legacy_{unique_suffix}_first",
        second_half_hash=f"legacy_{unique_suffix}_second",
        username_hash=f"legacy_{unique_suffix}_username",
        last_name_hash_by_part={},
    )
    db.session.add(student)
    db.session.flush()  # Get student.id
    
    # CRITICAL: Create the TeacherBlock seat (join code entry) for this student
    join_code = generate_join_code()  # ← Fixed function call
    seat = TeacherBlock(
        teacher_id=teacher.id,
        block=block,
        join_code=join_code,
        student_id=student.id,
        is_claimed=True,
        first_name=first_name,
        last_initial=last_initial,
        dob_sum=dob_sum,
        salt=salt,
        first_half_hash=f"seat_{unique_suffix}_first",
        last_name_hash_by_part={},
    )
    db.session.add(seat)
    
    return student, username, pin, join_code

def seed_database():
    """Seed minimal test data with proper multi-tenancy structure."""
    with app.app_context():
        print("🌱 Starting database seeding...")
        print("=" * 60)
        
        totp_secret = pyotp.random_base32()
        teacher = create_teacher("ms_johnson", totp_secret)
        db.session.flush()
        print(f"✅ Teacher: {teacher.username} (ID: {teacher.id})")
        print(f"   TOTP: {totp_secret}")
        
        students_data = [
            ("Alice", "A", 2008, "A"),
            ("Bob", "B", 2008, "A"),
            ("Carol", "C", 2009, "B"),
        ]
        
        credentials = []
        for first, last, year, block in students_data:
            student, username, pin, join_code = create_student_with_seat(
                first, last, year, block, teacher
            )
            credentials.append((username, pin, block, join_code))
            print(f"✅ Student: {username} / {pin} (Block {block}, Join: {join_code})")
        
        db.session.commit()
        
        print("=" * 60)
        print("✨ Seeding complete!")
        print("\nTest Credentials:")
        print(f"Teacher: {teacher.username} (use TOTP app with secret above)")
        for username, pin, block, join_code in credentials:
            print(f"Student: {username} / {pin} (Block {block}, Join: {join_code})")

if __name__ == "__main__":
    seed_database()
