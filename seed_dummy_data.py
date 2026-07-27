"""
Dummy Data Seeder for School Fee Management System v1.0.
Populates realistic Students, Receipts, and Receipt Items for testing and demonstration.
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

STUDENT_DATA = [
    ("ADM/2024/001", "101", "Aarav Sharma", "Rajesh Sharma", "Sunita Sharma", "Class 10", "A", "9876543210", "123 Green Park, New Delhi"),
    ("ADM/2024/002", "102", "Ananya Verma", "Sanjay Verma", "Meena Verma", "Class 10", "B", "9811223344", "456 Vasant Kunj, New Delhi"),
    ("ADM/2024/003", "103", "Rohan Gupta", "Amit Gupta", "Pooja Gupta", "Class 9", "A", "9988776655", "789 Lajpat Nagar, New Delhi"),
    ("ADM/2024/004", "104", "Isha Patel", "Vikram Patel", "Rekha Patel", "Class 12", "Science", "9711002233", "12 Sector 14, Gurgaon"),
    ("ADM/2024/005", "105", "Kabir Singh", "Harpreet Singh", "Simran Kaur", "Class 12", "Commerce", "9899112233", "34 Block B, Rohini, New Delhi"),
    ("ADM/2024/006", "106", "Diya Kumar", "Ramesh Kumar", "Kavita Kumar", "Class 8", "A", "9818877665", "56 Greater Kailash, New Delhi"),
    ("ADM/2024/007", "107", "Aditya Mishra", "Alok Mishra", "Sangeeta Mishra", "Class 11", "Science", "9871122334", "78 Sector 62, Noida"),
    ("ADM/2024/008", "108", "Sanya Malhotra", "Vijay Malhotra", "Nisha Malhotra", "Class 11", "Arts", "9910011223", "90 Defence Colony, New Delhi"),
    ("ADM/2024/009", "109", "Vihaan Joshi", "Pradeep Joshi", "Anita Joshi", "Class 7", "B", "9868877112", "23 Dwarka Sector 10, New Delhi"),
    ("ADM/2024/010", "110", "Meera Nair", "Unnikrishnan Nair", "Radhika Nair", "Class 6", "A", "9717766554", "45 Mayur Vihar Phase 1, New Delhi"),
    ("ADM/2024/011", "111", "Devansh Saxena", "Manish Saxena", "Renu Saxena", "Class 5", "A", "9810055443", "67 Preet Vihar, New Delhi"),
    ("ADM/2024/012", "112", "Kavya Choudhary", "Surendra Choudhary", "Kamlesh Choudhary", "Class 4", "B", "9999888777", "89 Janakpuri, New Delhi"),
    ("ADM/2024/013", "113", "Arjun Reddy", "Venkat Reddy", "Latha Reddy", "Class 3", "A", "9888777666", "101 Model Town, New Delhi"),
    ("ADM/2024/014", "114", "Anvi Deshmukh", "Nitin Deshmukh", "Swati Deshmukh", "Class 2", "A", "9777666555", "202 Pitampura, New Delhi"),
    ("ADM/2024/015", "115", "Reyansh Bhatia", "Gaurav Bhatia", "Neha Bhatia", "Class 1", "A", "9666555444", "303 Shalimar Bagh, New Delhi"),
]

PAYMENT_MODES = ["Cash", "UPI", "Cheque", "Demand Draft", "Net Banking"]
REMARKS_LIST = [
    "Quarter 1 Fee Payment",
    "Monthly Tuition + Transport Fee",
    "Annual Charges + Development Fee",
    "Tuition Fee Paid in Full",
    "Partial Fee Payment (Second Installment)",
    "Term Exam & Lab Charges Included"
]

def seed_dummy_data():
    print("=" * 60)
    print("Seeding Dummy Data into School Fee ERP...")
    print("=" * 60)

    init_db()
    seed_initial_data()

    db = get_db()
    try:
        # Check or retrieve Admin user
        admin = db.query(User).filter(User.username == "admin").first()
        admin_id = admin.id if admin else None

        # Fetch active Fee Categories
        categories = db.query(FeeCategory).filter(FeeCategory.is_active == True).all()
        if not categories:
            print("No fee categories found. Run seed_initial_data first.")
            return

        cat_dict = {c.name: c for c in categories}

        # 1. Seed Students
        existing_students = db.query(Student).all()
        student_objs = []
        if len(existing_students) < len(STUDENT_DATA):
            for adm_no, roll, name, father, mother, cls, sec, mob, addr in STUDENT_DATA:
                st = db.query(Student).filter(Student.admission_no == adm_no).first()
                if not st:
                    st = Student(
                        admission_no=adm_no,
                        roll_no=roll,
                        name=name,
                        father_name=father,
                        mother_name=mother,
                        class_name=cls,
                        section=sec,
                        mobile=mob,
                        address=addr,
                        admission_date=date(2024, 4, 1),
                        academic_session="2024-2025",
                        status="Active"
                    )
                    db.add(st)
            db.commit()
            print(f" Successfully seeded {len(STUDENT_DATA)} dummy students.")

        students = db.query(Student).all()

        # 2. Seed Receipts
        existing_receipts_count = db.query(Receipt).count()
        if existing_receipts_count < 15:
            today = date.today()
            receipt_counter = existing_receipts_count + 1

            # Dates spread out over the last 30 days including TODAY
            dates_sample = [
                today, today, today, # 3 receipts today for immediate KPI visibility!
                today - timedelta(days=1),
                today - timedelta(days=2),
                today - timedelta(days=3),
                today - timedelta(days=5),
                today - timedelta(days=7),
                today - timedelta(days=10),
                today - timedelta(days=12),
                today - timedelta(days=15),
                today - timedelta(days=18),
                today - timedelta(days=20),
                today - timedelta(days=25),
                today - timedelta(days=28),
            ]

            created_count = 0
            for r_date in dates_sample:
                st = random.choice(students)
                receipt_no = f"REC/2024/{receipt_counter:05d}"
                receipt_counter += 1

                # Pick 2 to 4 fee heads
                selected_cats = random.sample(categories, k=random.randint(2, 4))
                items_data = []
                subtotal = 0.0

                for c in selected_cats:
                    amt = c.default_amount
                    if amt == 0:
                        amt = 500.0
                    subtotal += amt
                    items_data.append((c.id, c.name, amt))

                discount = random.choice([0.0, 0.0, 100.0, 200.0, 500.0])
                fine = random.choice([0.0, 0.0, 0.0, 50.0, 100.0])
                total_amt = max(0.0, subtotal - discount + fine)

                # Partial payment sample logic (e.g. 20% of receipts have partial payments)
                if random.random() < 0.25 and total_amt > 2000:
                    paid_amt = round(total_amt * 0.75, -2) # e.g. pays 75%
                    due_amt = total_amt - paid_amt
                else:
                    paid_amt = total_amt
                    due_amt = 0.0

                amount_words = number_to_words_indian(paid_amt)
                pay_mode = random.choice(["Cash", "UPI / QR", "Cheque", "Demand Draft (DD)", "Net Banking / NEFT"])

                utr_num = f"UPI{random.randint(100000000000, 999999999999)}" if "UPI" in pay_mode or "Net" in pay_mode else ""
                chq_num = f"{random.randint(100000, 999999)}" if "Cheque" in pay_mode or "DD" in pay_mode else ""
                chq_date = r_date - timedelta(days=2) if chq_num else None
                bank = random.choice(["State Bank of India (SBI)", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank (PNB)"]) if pay_mode != "Cash" else ""

                ref_no = f"TXN{random.randint(10000000, 99999999)}" if pay_mode != "Cash" else ""
                remarks = random.choice(REMARKS_LIST)

                receipt = Receipt(
                    receipt_no=receipt_no,
                    receipt_date=r_date,
                    student_id=st.id,
                    academic_session="2024-2025",
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
                    created_by_user_id=admin_id,
                    status="Paid"
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

                created_count += 1

            db.commit()
            print(f" Successfully seeded {created_count} realistic fee receipts across dates & payment modes.")

        print("=" * 60)
        print("DUMMY DATA SEEDING COMPLETE!")
        print("Database updated: database/school_fee.db")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding dummy data: {e}")
        logger.error(f"Error seeding dummy data: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    seed_dummy_data()
