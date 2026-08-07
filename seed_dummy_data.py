"""
Dummy Data Seeder for School Fee Management System v2.0.
Populates 100 realistic Students (UG & PG), Fee Heads, and 350+ Receipts across payment modes for testing.
"""

import sys
import random
from datetime import date, datetime, timedelta
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.database import get_db, init_db
from models.student import Student
from models.fee_category import FeeCategory
from models.receipt import Receipt, ReceiptItem
from models.user import User
from models.settings import SchoolInformation
from services.db_seed import seed_initial_data
from utils.number_to_words import number_to_words_indian
from utils.logger import logger

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Isha", "Kabir", "Diya", "Aditya", "Sanya", "Vihaan", "Meera",
    "Devansh", "Kavya", "Arjun", "Anvi", "Reyansh", "Priya", "Rahul", "Neha", "Amit", "Pooja",
    "Siddharth", "Riya", "Karan", "Shreya", "Nikhil", "Tanya", "Varun", "Simran", "Aakash", "Divya",
    "Yash", "Sneha", "Manish", "Kritika", "Gaurav", "Deepika", "Pranav", "Bhavna", "Abhinav", "Payal",
    "Rishabh", "Meenakshi", "Sameer", "Swati", "Tarun", "Rashmi", "Alok", "Komal", "Vikas", "Archana",
    "Ayush", "Sonam", "Nitin", "Preeti", "Mayank", "Nisha", "Saurabh", "Rachna", "Deepak", "Anushka"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Mishra", "Malhotra", "Joshi", "Nair",
    "Saxena", "Choudhary", "Reddy", "Deshmukh", "Bhatia", "Kulkarni", "Aggarwal", "Pandey", "Rao", "Iyer",
    "Chawla", "Bhasin", "Trivedi", "Shukla", "Thakur", "Yadav", "Dutta", "Sinha", "Chauhan", "Kapoor"
]

COURSES_CLASSES = [
    ("UG", "B.Pharmacy FY", "A"),
    ("UG", "B.Pharmacy SY", "A"),
    ("UG", "B.Pharmacy TY", "B"),
    ("UG", "B.Pharmacy Final Year", "A"),
    ("PG", "M.Pharmacy 1st Year", "A"),
    ("PG", "M.Pharmacy 2nd Year", "A"),
    ("UG", "B.Sc Computer Science", "A"),
    ("PG", "M.Sc Information Tech", "A"),
    ("UG", "B.Com Honours", "B"),
    ("PG", "M.Com Finance", "A"),
]

CITIES_ADDRESSES = [
    "123 Green Park, New Delhi", "456 Vasant Kunj, New Delhi", "789 Lajpat Nagar, New Delhi",
    "12 Sector 14, Gurgaon", "34 Block B, Rohini, New Delhi", "56 Greater Kailash, New Delhi",
    "78 Sector 62, Noida", "90 Defence Colony, New Delhi", "23 Dwarka Sector 10, New Delhi",
    "45 Mayur Vihar Phase 1, New Delhi", "67 Preet Vihar, New Delhi", "89 Janakpuri, New Delhi",
    "101 Model Town, New Delhi", "202 Pitampura, New Delhi", "303 Shalimar Bagh, New Delhi",
    "15 FC Road, Pune", "88 MG Road, Bangalore", "42 Civil Lines, Jaipur", "99 FC Road, Indore"
]

PAYMENT_MODES = [
    "Cash",
    "UPI / QR",
    "Cheque",
    "Demand Draft (DD)",
    "Net Banking / NEFT",
    "Credit / Debit Card"
]

REMARKS_LIST = [
    "Semester 1 Fee Payment",
    "Monthly Tuition + Transport Fee",
    "Annual Development + Lab Charges",
    "Tuition Fee Paid in Full",
    "Second Installment Fee Payment",
    "Term Exam & Library Charges Included",
    "Scholarship Discount Applied",
    "Advance Semester Payment"
]

def seed_dummy_data():
    print("=" * 60)
    print("Seeding Realistic Demo Data into School Fee ERP...")
    print("=" * 60)

    init_db()
    seed_initial_data()

    db = get_db()
    try:
        # Check or retrieve Admin and Operator users
        admin = db.query(User).filter(User.username == "admin").first()
        operator = db.query(User).filter(User.username == "operator").first()
        user_ids = [u.id for u in [admin, operator] if u]

        # 1. Seed Fee Categories (UG & PG)
        FeeCategoryData = [
            ("Tuition Fee (UG)", "UG", 15000.0, "Standard semester tuition fee for undergraduate courses"),
            ("Admission Fee (UG)", "UG", 3000.0, "One-time admission fee for UG registration"),
            ("Examination Fee (UG)", "UG", 1500.0, "Semester examination fee"),
            ("Laboratory Fee (UG)", "UG", 2500.0, "Practical laboratory usage and equipment fee"),
            ("Transport Fee (UG)", "UG", 4000.0, "Bus and transport facility fee"),
            ("Computer & IT Lab Fee (UG)", "UG", 2000.0, "Computer lab and internet access fee"),
            ("Library Fee (UG)", "UG", 1000.0, "Library membership and book issue fee"),
            ("Sports & Gymnasium Fee (UG)", "UG", 500.0, "Sports and gym facility maintenance"),
            ("Tuition Fee (PG)", "PG", 25000.0, "Postgraduate advanced tuition fee"),
            ("Admission Fee (PG)", "PG", 5000.0, "One-time PG registration and counseling fee"),
            ("Examination & Thesis Fee (PG)", "PG", 3000.0, "PG examination and dissertation fee"),
            ("Research Lab Fee (PG)", "PG", 6000.0, "Advanced research lab usage fee"),
            ("Library & E-Journal Fee (PG)", "PG", 2000.0, "PG digital library and research journal subscription"),
            ("Transport Fee (PG)", "PG", 5000.0, "PG transport facility fee"),
            ("Late Fine", "UG", 200.0, "Penalty for late payment"),
        ]
        for name, crs, amt, desc in FeeCategoryData:
            cat = db.query(FeeCategory).filter(FeeCategory.name == name, FeeCategory.course == crs).first()
            if not cat:
                cat = FeeCategory(name=name, course=crs, default_amount=amt, description=desc, is_active=True)
                db.add(cat)
        db.commit()

        categories = db.query(FeeCategory).filter(FeeCategory.is_active == True).all()

        # 2. Seed 100 Students
        existing_count = db.query(Student).count()
        target_students = 100
        if existing_count < target_students:
            needed = target_students - existing_count
            print(f"Generating {needed} new students to reach {target_students} target...")

            random.seed(42)  # Deterministic seed for reproducible data
            for i in range(existing_count + 1, target_students + 1):
                adm_no = f"ADM/2026/{i:03d}"
                roll_no = f"{100 + i}"
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                name = f"{first_name} {last_name}"
                father_name = f"{random.choice(FIRST_NAMES)} {last_name}"
                mother_name = f"{random.choice(FIRST_NAMES)} {last_name}"
                course_type, cls_name, sec_name = random.choice(COURSES_CLASSES)
                mobile = f"9{random.randint(100000009, 999999999)}"
                address = random.choice(CITIES_ADDRESSES)

                st = db.query(Student).filter(Student.admission_no == adm_no).first()
                if not st:
                    st = Student(
                        admission_no=adm_no,
                        roll_no=roll_no,
                        name=name,
                        father_name=father_name,
                        mother_name=mother_name,
                        course=course_type,
                        class_name=cls_name,
                        section=sec_name,
                        mobile=mobile,
                        address=address,
                        admission_date=date(2025, 6, 1) + timedelta(days=random.randint(0, 60)),
                        academic_session="2025-2026",
                        status="Active"
                    )
                    db.add(st)
            db.commit()
            print(f" Successfully populated {target_students} realistic students.")

        students = db.query(Student).all()

        # 3. Seed 350+ Receipts
        existing_receipts_count = db.query(Receipt).count()
        target_receipts = 350
        if existing_receipts_count < target_receipts:
            today = date.today()
            needed_receipts = target_receipts - existing_receipts_count
            print(f"Generating {needed_receipts} new receipts to reach {target_receipts} target...")

            receipt_counter = existing_receipts_count + 1

            for r_idx in range(needed_receipts):
                # Distribute dates across last 90 days
                days_ago = random.randint(0, 90)
                r_date = today - timedelta(days=days_ago)
                st = random.choice(students)
                receipt_no = f"REC/2026/{receipt_counter:05d}"
                receipt_counter += 1

                # Filter categories matching student course or All
                st_crs = st.course or "UG"
                eligible_cats = [c for c in categories if c.course in (st_crs, "All")]
                if not eligible_cats:
                    eligible_cats = categories

                selected_cats = random.sample(eligible_cats, k=min(len(eligible_cats), random.randint(2, 4)))
                items_data = []
                subtotal = 0.0

                for c in selected_cats:
                    amt = c.default_amount
                    subtotal += amt
                    items_data.append((c.id, c.name, amt))

                discount = random.choice([0.0, 0.0, 0.0, 200.0, 500.0, 1000.0])
                fine = random.choice([0.0, 0.0, 0.0, 100.0, 250.0])
                total_amt = max(0.0, subtotal - discount + fine)

                # Partial payment sample logic (15% partial payments)
                if random.random() < 0.15 and total_amt > 3000:
                    paid_amt = float(int(total_amt * 0.7))
                    due_amt = total_amt - paid_amt
                else:
                    paid_amt = total_amt
                    due_amt = 0.0

                amount_words = number_to_words_indian(paid_amt)
                pay_mode = random.choice(PAYMENT_MODES)

                utr_num = f"UPI{random.randint(100000000000, 999999999999)}" if "UPI" in pay_mode or "Net" in pay_mode else ""
                chq_num = f"{random.randint(100000, 999999)}" if "Cheque" in pay_mode or "DD" in pay_mode else ""
                chq_date = r_date - timedelta(days=random.randint(1, 5)) if chq_num else None
                bank = random.choice(["State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank"]) if pay_mode != "Cash" else ""

                ref_no = f"TXN{random.randint(10000000, 99999999)}" if pay_mode not in ("Cash", "Cheque") else ""
                remarks = random.choice(REMARKS_LIST)
                user_id = random.choice(user_ids) if user_ids else None

                receipt = Receipt(
                    receipt_no=receipt_no,
                    receipt_date=r_date,
                    student_id=st.id,
                    academic_session="2025-2026",
                    subtotal=subtotal,
                    discount_amount=discount,
                    fine_amount=fine,
                    total_amount=total_amt,
                    paid_amount=paid_amt,
                    due_amount=due_amt,
                    amount_in_words=amount_words,
                    payment_mode=pay_mode,
                    reference_no=ref_no,
                    utr_number=utr_num,
                    cheque_number=chq_num,
                    cheque_date=chq_date,
                    bank_name=bank,
                    payment_date=r_date,
                    remarks=remarks,
                    created_by_user_id=user_id,
                    status="Paid" if due_amt == 0 else "Partial"
                )
                db.add(receipt)
                db.flush()

                for cat_id, cat_name, amt in items_data:
                    ritem = ReceiptItem(
                        receipt_id=receipt.id,
                        fee_category_id=cat_id,
                        category_name=cat_name,
                        amount=amt
                    )
                    db.add(ritem)

            db.commit()
            print(f" Successfully seeded {target_receipts} realistic fee receipts.")

        final_st_count = db.query(Student).count()
        final_rc_count = db.query(Receipt).count()

        print("=" * 60)
        print("DUMMY DATA SEEDING COMPLETE!")
        print(f"Total Students in Database: {final_st_count}")
        print(f"Total Receipts in Database: {final_rc_count}")
        print("Database file updated: database/school_fee.db")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f" Error seeding dummy data: {e}")
        logger.error(f"Error seeding dummy data: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    seed_dummy_data()
