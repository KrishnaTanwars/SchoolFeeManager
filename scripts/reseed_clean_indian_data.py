"""
Clean Reseed Script for EduLedger ERP (v2.3.0).
Wipes all old dummy/test records and seeds 100 Fresh Indian Context Students,
9 Standard Indian College Fee Heads, and 350 Authentic Fee Receipts with UPI/NetBanking/DD.
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
from models.academic import Course, Branch, AcademicYear, Semester
from controllers.academic_controller import AcademicController
from controllers.receipt_controller import ReceiptController
from utils.logger import logger

# --- AUTHENTIC INDIAN MASTER DATA ---
INDIAN_FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Aditya", "Ishaan", "Kavya", "Siddharth",
    "Pooja", "Manish", "Divya", "Vikas", "Sneha", "Karan", "Tanvi", "Abhishek",
    "Megha", "Rishabh", "Saurabh", "Swati", "Gaurav", "Nisha", "Nikhil", "Archana",
    "Tarun", "Payal", "Varun", "Simran", "Akash", "Shweta", "Nitin", "Preeti",
    "Kunal", "Aakanksha", "Sonam", "Deepak", "Riya", "Arjun", "Diya", "Kavita"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Joshi", "Mehta",
    "Chawla", "Bhatia", "Malhotra", "Agarwal", "Rao", "Nair", "Saxena", "Deshmukh",
    "Reddy", "Mishra", "Trivedi", "Pandey", "Kapoor", "Choudhury", "Mukherjee", "Yadav",
    "Iyer", "Deshpande", "Kulkarni", "Chauhan", "Dutta", "Nambiar"
]

INDIAN_CITIES_ADDRESSES = [
    ("New Delhi", "Plot 42, Sector 12, Dwarka, New Delhi - 110078"),
    ("New Delhi", "Flat 302, Vasant Kunj, New Delhi - 110070"),
    ("New Delhi", "B-14, Green Park Main, New Delhi - 110016"),
    ("Mumbai", "102, Bandra West, Hill Road, Mumbai - 400050"),
    ("Mumbai", "A-501, Hiranandani Gardens, Powai, Mumbai - 400076"),
    ("Bengaluru", "No. 88, 4th Block, Koramangala, Bengaluru - 560034"),
    ("Bengaluru", "12th Main, Indiranagar, Bengaluru - 560038"),
    ("Pune", "Flat 405, Viman Nagar, Pune - 411014"),
    ("Pune", "Lane 7, Koregaon Park, Pune - 411001"),
    ("Jaipur", "C-84, Malviya Nagar, Jaipur - 302017"),
    ("Jaipur", "12, Civil Lines, Jaipur - 302006"),
    ("Lucknow", "Vipul Khand 3, Gomti Nagar, Lucknow - 226010"),
    ("Lucknow", "14, Hazratganj, Lucknow - 226001"),
    ("Hyderabad", "Road No. 12, Banjara Hills, Hyderabad - 500034"),
    ("Hyderabad", "Plot 90, HITECH City, Madhapur, Hyderabad - 500081"),
    ("Chennai", "Door No. 15, 2nd Avenue, Anna Nagar, Chennai - 600040"),
    ("Kolkata", "Block CF, Sector 1, Salt Lake, Kolkata - 700064"),
    ("Ahmedabad", "101, Satellite Road, Ahmedabad - 380015")
]

INDIAN_COLLEGE_COURSES = [
    {
        "course": "B.Tech",
        "branches": ["Computer Science", "Mechanical Engineering", "Information Technology"],
        "years": ["1st Year", "2nd Year", "3rd Year", "4th Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8"],
        "class_name": "Degree College"
    },
    {
        "course": "MBA",
        "branches": ["Finance", "Human Resource", "Marketing"],
        "years": ["1st Year", "2nd Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4"],
        "class_name": "Post Graduate"
    },
    {
        "course": "BCA",
        "branches": ["Computer Applications"],
        "years": ["1st Year", "2nd Year", "3rd Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6"],
        "class_name": "Degree College"
    },
    {
        "course": "BBA",
        "branches": ["Business Administration"],
        "years": ["1st Year", "2nd Year", "3rd Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6"],
        "class_name": "Degree College"
    },
    {
        "course": "MCA",
        "branches": ["Computer Applications"],
        "years": ["1st Year", "2nd Year"],
        "semesters": ["Semester 1", "Semester 2", "Semester 3", "Semester 4"],
        "class_name": "Post Graduate"
    },
    {
        "course": "Class 10",
        "branches": ["General"],
        "years": [""],
        "semesters": [""],
        "class_name": "Class 10"
    }
]

# --- 9 STANDARD REQUIRED INDIAN COLLEGE FEE HEADS ---
STANDARD_INDIAN_FEE_HEADS = [
    {
        "name": "Tuition Fee",
        "course": "All",
        "branch": "All",
        "academic_year": "All",
        "semester": "All",
        "default_amount": 35000.0,
        "description": "Standard Semester Tuition Fee"
    },
    {
        "name": "Admission & Enrollment Fee",
        "course": "All",
        "branch": "All",
        "academic_year": "1st Year",
        "semester": "Semester 1",
        "default_amount": 5000.0,
        "description": "One-time Admission & University Registration Fee"
    },
    {
        "name": "University Examination Fee",
        "course": "All",
        "branch": "All",
        "academic_year": "All",
        "semester": "All",
        "default_amount": 2500.0,
        "description": "End-Semester Examination Fee"
    },
    {
        "name": "Computer & IT Lab Fee",
        "course": "B.Tech",
        "branch": "All",
        "academic_year": "All",
        "semester": "All",
        "default_amount": 3000.0,
        "description": "Software & Practical Laboratory Usage Fee"
    },
    {
        "name": "Library & E-Resources Fee",
        "course": "All",
        "branch": "All",
        "academic_year": "All",
        "semester": "All",
        "default_amount": 1500.0,
        "description": "Central Library & Digital Journal Subscription"
    },
    {
        "name": "Campus Development Fee",
        "course": "All",
        "branch": "All",
        "academic_year": "All",
        "semester": "All",
        "default_amount": 2000.0,
        "description": "Institution Infrastructure & Building Maintenance"
    },
    {
        "name": "Training & Placement Fee",
        "course": "All",
        "branch": "All",
        "academic_year": "All",
        "semester": "All",
        "default_amount": 2500.0,
        "description": "Skill Development & Campus Placement Cell Fee"
    },
    {
        "name": "Sports & Cultural Activities Fee",
        "course": "All",
        "branch": "All",
        "academic_year": "All",
        "semester": "All",
        "default_amount": 1000.0,
        "description": "Annual Sports & Youth Festival Activity Fee"
    },
    {
        "name": "Refundable Caution Deposit",
        "course": "All",
        "branch": "All",
        "academic_year": "1st Year",
        "semester": "Semester 1",
        "default_amount": 5000.0,
        "description": "One-time Refundable Institution Caution Money"
    }
]

def reseed_clean_indian_data():
    init_db()
    AcademicController.seed_academic_masters_if_empty()
    db = get_db()

    try:
        print("============================================================")
        print("Wiping old dummy/test records...")
        print("============================================================")
        
        # 1. Delete all existing receipts, items, students, fee categories
        db.query(ReceiptItem).delete()
        db.query(Receipt).delete()
        db.query(Student).delete()
        db.query(FeeCategory).delete()
        db.commit()
        print("Old database tables cleared successfully.")

        # 2. Seed Standard Indian College Fee Heads
        print("Seeding 9 Standard Indian College Fee Heads...")
        for fh_data in STANDARD_INDIAN_FEE_HEADS:
            cat = FeeCategory(**fh_data, is_active=True)
            db.add(cat)
        db.commit()
        print("Seeded 9 Standard Indian College Fee Heads.")

        # 3. Seed 100 Fresh Indian Context Students
        print("Seeding 100 Fresh Indian Context Students...")
        seeded_students = []
        for i in range(100):
            first_name = INDIAN_FIRST_NAMES[i % len(INDIAN_FIRST_NAMES)]
            last_name = INDIAN_LAST_NAMES[(i * 3) % len(INDIAN_LAST_NAMES)]
            student_name = f"{first_name} {last_name}"
            father_name = f"{random.choice(INDIAN_FIRST_NAMES)} {last_name}"
            mother_name = f"{random.choice(INDIAN_FIRST_NAMES)} {last_name}"

            course_info = INDIAN_COLLEGE_COURSES[i % len(INDIAN_COLLEGE_COURSES)]
            course = course_info["course"]
            branch = random.choice(course_info["branches"])
            year = random.choice(course_info["years"])
            semester = random.choice(course_info["semesters"])
            cls_name = course_info["class_name"]

            adm_no = f"ADM/2025/{1001 + i:04d}"
            roll_no = f"{101 + (i % 80)}"

            # Authentic Indian Mobile format (98xxxxxxxx, 97xxxxxxxx, 99xxxxxxxx)
            mob_prefix = random.choice(["98", "97", "99", "981", "987", "991", "965", "880"])
            mob_suffix = f"{random.randint(100000, 999999)}"
            mobile = (mob_prefix + mob_suffix)[:10]

            city, address = random.choice(INDIAN_CITIES_ADDRESSES)

            adm_date = date(2025, 6, 1) + timedelta(days=random.randint(0, 75))

            st = Student(
                admission_no=adm_no,
                roll_no=roll_no,
                name=student_name,
                father_name=father_name,
                mother_name=mother_name,
                course=course,
                branch=branch,
                year=year,
                semester=semester,
                class_name=cls_name,
                section=random.choice(["A", "B", "C"]),
                mobile=mobile,
                address=address,
                admission_date=adm_date,
                academic_session="2025-2026",
                status="Active"
            )
            db.add(st)
            seeded_students.append(st)
        
        db.commit()
        print("Seeded 100 Fresh Indian Context Students successfully.")

        # Re-query all committed students
        all_students = db.query(Student).all()
        all_fee_heads = db.query(FeeCategory).all()

        # 4. Seed 350 Authentic Indian Fee Receipts
        print("Seeding 350 Authentic Indian Fee Receipts...")
        payment_modes = [
            ("UPI / GPay", "UPI"),
            ("Net Banking", "NET"),
            ("Cash", "CASH"),
            ("Demand Draft", "DD"),
            ("Cheque", "CHQ")
        ]

        banks = ["State Bank of India (SBI)", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank (PNB)"]

        start_date = date(2025, 6, 1)
        for i in range(350):
            st = random.choice(all_students)
            rec_date = start_date + timedelta(days=random.randint(0, 240))

            # Select 1 to 4 applicable fee heads
            cats_sample = random.sample(all_fee_heads, min(len(all_fee_heads), random.randint(1, 4)))
            items_data = [
                {
                    "fee_category_id": cat.id,
                    "category_name": cat.name,
                    "amount": cat.default_amount
                }
                for cat in cats_sample
            ]

            pmode, ptype = random.choice(payment_modes)
            ref_no = ""
            utr_no = ""
            chq_no = ""
            bank_name = ""

            if ptype == "UPI":
                utr_no = f"UPI/{random.randint(400000000000, 499999999999)}"
                ref_no = utr_no
            elif ptype == "NET":
                utr_no = f"TXN{random.randint(100000000, 999999999)}"
                bank_name = random.choice(banks)
                ref_no = utr_no
            elif ptype == "DD":
                ref_no = f"DD-{random.randint(100000, 999999)}"
                bank_name = random.choice(banks)
            elif ptype == "CHQ":
                chq_no = f"{random.randint(100000, 999999)}"
                bank_name = random.choice(banks)
                ref_no = f"CHQ-{chq_no}"

            ReceiptController.create_receipt(
                student_id=st.id,
                academic_session=st.academic_session,
                items=items_data,
                discount_amount=0.0,
                fine_amount=0.0,
                payment_mode=pmode,
                reference_no=ref_no,
                utr_number=utr_no,
                cheque_number=chq_no,
                bank_name=bank_name,
                remarks=f"Fee payment for {st.course} {st.semester or ''}".strip(),
                receipt_date=rec_date
            )

        print("Seeded 350 Authentic Indian Fee Receipts successfully.")

        print("============================================================")
        print("DATABASE RESEEDED SUCCESSFULLY WITH CLEAN INDIAN CONTEXT DATA!")
        print("============================================================")

    except Exception as e:
        db.rollback()
        logger.error(f"Reseed Error: {e}", exc_info=True)
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reseed_clean_indian_data()
