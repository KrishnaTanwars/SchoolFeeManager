"""
Seed Realistic Academic Structure Demo Data (Colleges, Universities & Schools).
Seeds B.Tech, MBA, BCA, BBA, MCA, and Class 10 with Semesters 1-8, Fee Heads, Students, and Receipts.
"""

import sys
import random
from pathlib import Path
from datetime import date, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.database import get_db, init_db
from models.student import Student
from models.fee_category import FeeCategory
from models.receipt import Receipt, ReceiptItem
from controllers.academic_controller import AcademicController
from controllers.receipt_controller import ReceiptController
from utils.logger import logger

FIRST_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Rohan", "Ananya", "Vikas", "Pooja",
    "Siddharth", "Neha", "Aditya", "Riya", "Karan", "Kavya", "Arjun", "Diya", "Gaurav",
    "Isha", "Manish", "Divya", "Akash", "Shweta", "Varun", "Tanvi", "Nikhil", "Simran",
    "Harsh", "Megha", "Abhishek", "Aakanksha", "Saurabh", "Sonam", "Deepak", "Swati",
    "Nitin", "Nisha", "Rishabh", "Preeti", "Kunal", "Archana", "Tarun", "Payal"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Joshi", "Mehta",
    "Chawla", "Bhatia", "Malhotra", "Agarwal", "Rao", "Nair", "Saxena", "Deshmukh",
    "Reddy", "Mishra", "Trivedi", "Pandey", "Kapoor", "Choudhury", "Mukherjee", "Yadav"
]

COURSES_DATA = [
    {
        "course": "B.Tech",
        "branches": ["Computer Science", "Mechanical Engineering", "Information Technology"],
        "years": ["1st Year", "2nd Year", "3rd Year", "4th Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8"]
    },
    {
        "course": "MBA",
        "branches": ["Finance", "Human Resource"],
        "years": ["1st Year", "2nd Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4"]
    },
    {
        "course": "BCA",
        "branches": ["Computer Applications"],
        "years": ["1st Year", "2nd Year", "3rd Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6"]
    },
    {
        "course": "BBA",
        "branches": ["Business Administration"],
        "years": ["1st Year", "2nd Year", "3rd Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6"]
    },
    {
        "course": "Class 10",
        "branches": ["General"],
        "years": ["None"],
        "semesters": ["None"]
    }
]

def seed_academic_demo_data():
    init_db()
    AcademicController.seed_academic_masters_if_empty()
    db = get_db()

    try:
        logger.info("Starting Academic ERP Demo Data Seeding...")

        # 1. Seed Academic Fee Heads
        academic_fee_heads = [
            # B.Tech Fee Heads
            {"name": "B.Tech Tuition Fee", "course": "B.Tech", "branch": "All", "academic_year": "All", "semester": "Semester 1", "default_amount": 45000.0},
            {"name": "B.Tech Tuition Fee", "course": "B.Tech", "branch": "All", "academic_year": "All", "semester": "Semester 3", "default_amount": 45000.0},
            {"name": "B.Tech Lab Fee", "course": "B.Tech", "branch": "All", "academic_year": "All", "semester": "Semester 3", "default_amount": 5000.0},
            {"name": "B.Tech Exam Fee", "course": "B.Tech", "branch": "All", "academic_year": "All", "semester": "Semester 3", "default_amount": 2500.0},
            # MBA Fee Heads
            {"name": "MBA Admission Fee", "course": "MBA", "branch": "All", "academic_year": "1st Year", "semester": "Semester 1", "default_amount": 12000.0},
            {"name": "MBA Tuition Fee", "course": "MBA", "branch": "All", "academic_year": "All", "semester": "Semester 1", "default_amount": 35000.0},
            {"name": "MBA Tuition Fee", "course": "MBA", "branch": "All", "academic_year": "All", "semester": "Semester 3", "default_amount": 35000.0},
            # BCA Fee Heads
            {"name": "BCA Tuition Fee", "course": "BCA", "branch": "All", "academic_year": "All", "semester": "Semester 1", "default_amount": 25000.0},
            {"name": "BCA Computer Lab Fee", "course": "BCA", "branch": "All", "academic_year": "All", "semester": "Semester 1", "default_amount": 3000.0},
            # Universal / All Course Fee Heads
            {"name": "Library Fee", "course": "All", "branch": "All", "academic_year": "All", "semester": "All", "default_amount": 1000.0},
            {"name": "Sports & Culturals Fee", "course": "All", "branch": "All", "academic_year": "All", "semester": "All", "default_amount": 500.0},
        ]

        for fh in academic_fee_heads:
            existing = db.query(FeeCategory).filter(
                FeeCategory.name == fh["name"],
                FeeCategory.course == fh["course"],
                FeeCategory.semester == fh["semester"]
            ).first()
            if not existing:
                db.add(FeeCategory(**fh, is_active=True))
        db.commit()

        # 2. Seed 100 Academic Students
        current_students_count = db.query(Student).count()
        if current_students_count < 100:
            students_needed = 100 - current_students_count
            for i in range(students_needed):
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                student_name = f"{first_name} {last_name}"
                father_name = f"{random.choice(FIRST_NAMES)} {last_name}"
                mother_name = f"{random.choice(FIRST_NAMES)} {last_name}"

                c_info = random.choice(COURSES_DATA)
                course = c_info["course"]
                branch = random.choice(c_info["branches"])
                year = random.choice(c_info["years"])
                semester = random.choice(c_info["semesters"])

                adm_no = f"ADM/2025/{1000 + current_students_count + i + 1:04d}"
                roll_no = f"{101 + (i % 90)}"
                mobile = f"98{random.randint(10000000, 99999999)}"

                st = Student(
                    admission_no=adm_no,
                    roll_no=roll_no,
                    name=student_name,
                    father_name=father_name,
                    mother_name=mother_name,
                    course=course,
                    branch=branch,
                    year="" if year == "None" else year,
                    semester="" if semester == "None" else semester,
                    class_name="Class 10" if course == "Class 10" else "Degree College",
                    section=random.choice(["A", "B", "C"]),
                    mobile=mobile,
                    address="Sector 12, Academic Block, University Campus",
                    admission_date=date(2025, 6, 1) + timedelta(days=random.randint(0, 60)),
                    academic_session="2025-2026",
                    status="Active"
                )
                db.add(st)
            db.commit()
            logger.info("Seeded 100 realistic Academic ERP students.")

        # 3. Seed 350 Academic Fee Receipts
        all_students = db.query(Student).all()
        current_receipts_count = db.query(Receipt).count()

        if current_receipts_count < 350 and all_students:
            receipts_to_create = 350 - current_receipts_count
            start_date = date(2025, 6, 1)

            payment_modes = ["Cash", "UPI / GPay", "Net Banking", "Cheque", "Demand Draft"]

            for i in range(receipts_to_create):
                student = random.choice(all_students)
                rec_date = start_date + timedelta(days=random.randint(0, 250))
                
                # Fetch applicable fee categories for this student
                applicable_cats = db.query(FeeCategory).filter(FeeCategory.is_active == True).all()
                selected_cats = random.sample(applicable_cats, min(len(applicable_cats), random.randint(1, 3)))
                
                items_data = [
                    {
                        "fee_category_id": cat.id,
                        "category_name": cat.name,
                        "amount": cat.default_amount
                    }
                    for cat in selected_cats
                ]

                pmode = random.choice(payment_modes)
                ref_no = f"UPI/{random.randint(100000, 999999)}" if "UPI" in pmode else (f"TXN{random.randint(10000, 99999)}" if "Banking" in pmode else "")

                ReceiptController.create_receipt(
                    student_id=student.id,
                    academic_session=student.academic_session,
                    items=items_data,
                    discount_amount=0.0,
                    fine_amount=0.0,
                    payment_mode=pmode,
                    reference_no=ref_no,
                    remarks=f"Fee collection for {student.course} {student.semester or ''}".strip(),
                    receipt_date=rec_date
                )

            logger.info("Seeded 350 realistic Academic ERP fee receipts.")

        print("============================================================")
        print("ACADEMIC ERP DEMO DATA SEEDED SUCCESSFULLY!")
        print("============================================================")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding Academic Demo Data: {e}", exc_info=True)
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_academic_demo_data()
