"""
Student Bulk Import & Data Validation Service for EduLedger ERP v1.9.0.
Supports CSV and Excel (.xlsx) file parsing, field validation, duplicate detection,
row-by-row previews, skipping invalid rows, and downloadable error reports.
"""

import csv
import re
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from config.app_config import EXPORTS_DIR
from config.database import get_db
from models.student import Student
from models.audit import AuditLog
from controllers.auth_controller import AuthController
from services.export_service import ExportService
from utils.logger import logger


class ImportService:
    @staticmethod
    def _get_100_sample_indian_rows() -> List[List[str]]:
        first_names = [
            "Aarav", "Ananya", "Rohan", "Priya", "Aditya", "Ishaan", "Kavya", "Siddharth",
            "Pooja", "Manish", "Divya", "Vikas", "Sneha", "Karan", "Tanvi", "Abhishek",
            "Megha", "Rishabh", "Saurabh", "Swati", "Gaurav", "Nisha", "Nikhil", "Archana",
            "Tarun", "Payal", "Varun", "Simran", "Akash", "Shweta", "Nitin", "Preeti"
        ]
        last_names = [
            "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Joshi", "Mehta",
            "Chawla", "Bhatia", "Malhotra", "Agarwal", "Rao", "Nair", "Saxena", "Deshmukh",
            "Reddy", "Mishra", "Trivedi", "Pandey", "Kapoor", "Choudhury", "Mukherjee", "Yadav"
        ]
        courses_data = [
            ("B.Tech", "Computer Science", "2nd Year", "Semester 3"),
            ("B.Tech", "Information Technology", "3rd Year", "Semester 5"),
            ("B.Tech", "Mechanical Engineering", "1st Year", "Semester 1"),
            ("B.Tech", "Electrical Engineering", "4th Year", "Semester 7"),
            ("MBA", "Finance", "1st Year", "Semester 1"),
            ("MBA", "Marketing", "2nd Year", "Semester 3"),
            ("BCA", "Computer Applications", "1st Year", "Semester 1"),
            ("BCA", "Computer Applications", "2nd Year", "Semester 3"),
            ("BBA", "Business Administration", "1st Year", "Semester 1"),
            ("MCA", "Software Systems", "2nd Year", "Semester 3")
        ]
        cities = [
            "123 Green Park, New Delhi", "456 Vasant Kunj, New Delhi", "789 Malviya Nagar, New Delhi",
            "102 Hill Road, Bandra West, Mumbai", "A-501 Hiranandani, Powai, Mumbai",
            "88 Koramangala 4th Block, Bengaluru", "12th Main, Indiranagar, Bengaluru",
            "Flat 405, Viman Nagar, Pune", "C-84 Malviya Nagar, Jaipur", "Vipul Khand, Gomti Nagar, Lucknow"
        ]

        rows = []
        for i in range(1, 101):
            fn = first_names[(i - 1) % len(first_names)]
            ln = last_names[(i * 3) % len(last_names)]
            st_name = f"{fn} {ln}"
            f_name = f"{first_names[(i * 5) % len(first_names)]} {ln}"
            m_name = f"{first_names[(i * 7) % len(first_names)]} {ln}"
            crs, br, yr, sem = courses_data[(i - 1) % len(courses_data)]
            adm_no = f"ADM/2025/{1000 + i:04d}"
            roll_no = f"{100 + i}"
            mob = f"987{i:07d}"
            addr = cities[(i - 1) % len(cities)]
            adm_date = f"2025-06-{(i % 28) + 1:02d}"
            dob_sample = f"2005-0{((i % 8) + 1)}-{(i % 25) + 1:02d}"
            aadhaar_sample = f"6789{i:08d}"
            sess = "2025-2026"
            rows.append([adm_no, roll_no, st_name, dob_sample, crs, br, yr, sem, f_name, m_name, mob, aadhaar_sample, addr, adm_date, sess, "Active"])
        return rows

    @staticmethod
    def generate_sample_csv(output_path: Optional[str] = None) -> Tuple[bool, str]:
        """Generates sample CSV student import template with 100 Indian college student rows."""
        headers = [
            "Admission Number", "Roll Number", "Student Name", "Date of Birth", "Course", "Branch",
            "Academic Year", "Semester", "Father Name",
            "Mother Name", "Mobile Number", "Aadhaar Number", "Address", "Admission Date", "Academic Session", "Status"
        ]
        rows = ImportService._get_100_sample_indian_rows()
        if not output_path:
            output_path = str(EXPORTS_DIR / "sample_student_import.csv")

        return ExportService.export_to_csv(headers, rows, filename_prefix="Sample_Students_100", output_path=output_path)

    @staticmethod
    def generate_sample_excel(output_path: Optional[str] = None) -> Tuple[bool, str]:
        """Generates sample Excel student import template with 100 Indian college student rows."""
        headers = [
            "Admission Number", "Roll Number", "Student Name", "Date of Birth", "Course", "Branch",
            "Academic Year", "Semester", "Father Name",
            "Mother Name", "Mobile Number", "Aadhaar Number", "Address", "Admission Date", "Academic Session", "Status"
        ]
        rows = ImportService._get_100_sample_indian_rows()
        if not output_path:
            output_path = str(EXPORTS_DIR / "sample_student_import.xlsx")

        return ExportService.export_to_excel(headers, rows, filename_prefix="Sample_Students_100", output_path=output_path)

    @staticmethod
    def read_students_file(file_path: str) -> Tuple[bool, List[str], List[Dict[str, Any]], str]:
        """Reads CSV or Excel (.xlsx) file and returns headers and raw row dictionaries."""
        path = Path(file_path)
        if not path.exists():
            return False, [], [], "File does not exist."

        ext = path.suffix.lower()
        if ext == ".csv":
            return ImportService._read_csv(path)
        elif ext in (".xlsx", ".xls"):
            return ImportService._read_excel(path)
        else:
            return False, [], [], "Unsupported file format. Please select a .csv or .xlsx file."

    @staticmethod
    def _read_csv(path: Path) -> Tuple[bool, List[str], List[Dict[str, Any]], str]:
        try:
            with open(path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = [h.strip() for h in next(reader, [])]
                rows = []
                for row_idx, r in enumerate(reader, start=2):
                    if not any(cell.strip() for cell in r):
                        continue
                    row_dict = {}
                    for idx, h in enumerate(headers):
                        val = r[idx].strip() if idx < len(r) else ""
                        row_dict[h] = val
                    row_dict["__row_num__"] = row_idx
                    rows.append(row_dict)
            return True, headers, rows, f"Read {len(rows)} rows from CSV."
        except Exception as e:
            logger.error(f"Error reading CSV: {e}", exc_info=True)
            return False, [], [], f"Failed to read CSV file: {str(e)}"

    @staticmethod
    def _read_excel(path: Path) -> Tuple[bool, List[str], List[Dict[str, Any]], str]:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            iter_rows = ws.iter_rows(values_only=True)
            raw_headers = next(iter_rows, [])
            headers = [str(h).strip() if h else f"Col{idx}" for idx, h in enumerate(raw_headers)]

            rows = []
            for row_idx, r in enumerate(iter_rows, start=2):
                if not r or not any(str(cell).strip() for cell in r if cell is not None):
                    continue
                row_dict = {}
                for idx, h in enumerate(headers):
                    val = str(r[idx]).strip() if idx < len(r) and r[idx] is not None else ""
                    if val == "None":
                        val = ""
                    row_dict[h] = val
                row_dict["__row_num__"] = row_idx
                rows.append(row_dict)
            return True, headers, rows, f"Read {len(rows)} rows from Excel."
        except ImportError:
            # Fallback for TSV-Excel files
            return ImportService._read_csv(path)
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}", exc_info=True)
            return False, [], [], f"Failed to read Excel file: {str(e)}"

    @staticmethod
    def validate_and_parse_students(raw_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates raw student records against database and business rules.
        Returns detailed status, issues, and structured error report.
        """
        db = get_db()
        try:
            # Load existing DB sets for fast duplicate lookup
            existing_adm_nos = set(a[0].lower() for a in db.query(Student.admission_no).all() if a[0])
            existing_rolls = set(r[0].lower() for r in db.query(Student.roll_no).all() if r[0])
            existing_mobiles = set(m[0] for m in db.query(Student.mobile).all() if m[0])
            existing_aadhaars = set(a[0] for a in db.query(Student.aadhaar_number).all() if a[0])

            file_adm_nos = set()
            file_rolls = set()
            file_aadhaars = set()

            parsed_items = []
            errors_report = []

            for row in raw_rows:
                row_num = row.get("__row_num__", 0)

                # Field mapping extraction with flexible column names
                adm_no = row.get("Admission Number") or row.get("Admission No") or row.get("Adm No") or ""
                roll_no = row.get("Roll Number") or row.get("Roll No") or ""
                name = row.get("Student Name") or row.get("Name") or ""
                dob_str = row.get("Date of Birth") or row.get("Date Of Birth") or row.get("DOB") or ""
                cls_name = row.get("Class") or row.get("Class Name") or "Degree College"
                sec = row.get("Section") or "A"
                crs = row.get("Course") or "General"
                branch = row.get("Branch") or row.get("Department") or ""
                year = row.get("Academic Year") or row.get("Year") or ""
                sem = row.get("Semester") or ""
                father_name = row.get("Father Name") or ""
                mother_name = row.get("Mother Name") or ""
                mobile = row.get("Mobile Number") or row.get("Mobile") or row.get("Phone") or ""
                aadhaar = row.get("Aadhaar Number") or row.get("Aadhaar No") or row.get("Aadhaar") or row.get("Aadhar") or ""
                address = row.get("Address") or ""
                adm_date_str = row.get("Admission Date") or row.get("Date Of Admission") or ""
                session = row.get("Academic Session") or row.get("Session") or "2025-2026"
                status = row.get("Status") or "Active"

                issues = []
                suggested_fixes = []
                status_code = "Valid"  # Valid / Duplicate / Invalid

                # 1. Required Fields Check
                if not adm_no.strip():
                    issues.append("Missing Admission Number")
                    suggested_fixes.append("Provide a unique admission number")
                if not name.strip():
                    issues.append("Missing Student Name")
                    suggested_fixes.append("Enter student full name")
                if not father_name.strip():
                    issues.append("Missing Father Name")
                    suggested_fixes.append("Enter father's name")
                if not mobile.strip():
                    issues.append("Missing Mobile Number")
                    suggested_fixes.append("Provide 10-digit mobile number")

                # 2. Mobile Validation
                clean_mobile = re.sub(r"\D", "", mobile)
                if mobile.strip() and len(clean_mobile) != 10:
                    issues.append("Invalid Mobile Format (must be 10 digits)")
                    suggested_fixes.append("Format mobile to 10 digits e.g. 9876543210")

                # 3. Aadhaar Validation & Duplicate Check
                clean_aadhaar = aadhaar.strip()
                if clean_aadhaar:
                    if not clean_aadhaar.isdigit() or len(clean_aadhaar) != 12:
                        issues.append("Invalid Aadhaar Format (must be exactly 12 digits)")
                        suggested_fixes.append("Provide 12 numeric digits for Aadhaar")
                    elif clean_aadhaar in existing_aadhaars or clean_aadhaar in file_aadhaars:
                        issues.append(f"Aadhaar Number '{clean_aadhaar}' is already registered")
                        suggested_fixes.append("Use a unique Aadhaar number")
                        status_code = "Duplicate"
                    else:
                        file_aadhaars.add(clean_aadhaar)

                # 4. Admission Number Duplicate Detection
                norm_adm = adm_no.strip().lower()
                if norm_adm:
                    if norm_adm in existing_adm_nos:
                        issues.append(f"Admission No '{adm_no}' already exists in database")
                        suggested_fixes.append("Use a new unique admission number")
                        status_code = "Duplicate"
                    elif norm_adm in file_adm_nos:
                        issues.append(f"Duplicate Admission No '{adm_no}' within import file")
                        suggested_fixes.append("Remove duplicate row in file")
                        status_code = "Duplicate"
                    else:
                        file_adm_nos.add(norm_adm)

                # 5. Roll Number Duplicate Detection
                norm_roll = roll_no.strip().lower()
                if norm_roll:
                    if norm_roll in existing_rolls or norm_roll in file_rolls:
                        issues.append(f"Duplicate Roll No '{roll_no}'")
                        suggested_fixes.append("Assign distinct roll number")
                        if status_code != "Duplicate":
                            status_code = "Duplicate"
                    else:
                        file_rolls.add(norm_roll)

                # 6. Date Parsing (DOB & Admission Date)
                parsed_dob = None
                if dob_str.strip():
                    try:
                        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                            try:
                                parsed_dob = datetime.strptime(dob_str.strip(), fmt).date()
                                break
                            except ValueError:
                                pass
                    except Exception:
                        issues.append("Invalid DOB format")
                        suggested_fixes.append("Use YYYY-MM-DD or DD-MM-YYYY format for Date of Birth")

                parsed_adm_date = date.today()
                if adm_date_str.strip():
                    try:
                        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                            try:
                                parsed_adm_date = datetime.strptime(adm_date_str.strip(), fmt).date()
                                break
                            except ValueError:
                                pass
                    except Exception:
                        issues.append("Invalid Date format")
                        suggested_fixes.append("Use YYYY-MM-DD or DD-MM-YYYY format")

                if issues and status_code == "Valid":
                    # Mandatory missing fields make it Invalid
                    if any("Missing" in i or "Invalid" in i for i in issues):
                        status_code = "Invalid"

                if status_code != "Valid":
                    errors_report.append({
                        "Row Number": row_num,
                        "Admission No": adm_no,
                        "Student Name": name,
                        "Column / Field": ", ".join(set([i.split()[1] if len(i.split()) > 1 else i for i in issues])),
                        "Reason": "; ".join(issues),
                        "Suggested Fix": "; ".join(suggested_fixes)
                    })

                parsed_items.append({
                    "row_num": row_num,
                    "admission_no": adm_no.strip(),
                    "roll_no": roll_no.strip(),
                    "name": name.strip(),
                    "date_of_birth": parsed_dob,
                    "class_name": cls_name.strip(),
                    "section": sec.strip() or "A",
                    "course": crs.strip(),
                    "branch": branch.strip(),
                    "year": year.strip(),
                    "semester": sem.strip(),
                    "father_name": father_name.strip(),
                    "mother_name": mother_name.strip(),
                    "mobile": clean_mobile or mobile.strip(),
                    "aadhaar_number": clean_aadhaar or None,
                    "address": address.strip(),
                    "admission_date": parsed_adm_date,
                    "academic_session": session.strip() or "2025-2026",
                    "status": "Active" if status.strip().lower() != "inactive" else "Inactive",
                    "validation_status": status_code,
                    "issues": "; ".join(issues) if issues else "OK",
                    "is_importable": (status_code == "Valid")
                })

            valid_count = sum(1 for i in parsed_items if i["validation_status"] == "Valid")
            duplicate_count = sum(1 for i in parsed_items if i["validation_status"] == "Duplicate")
            invalid_count = sum(1 for i in parsed_items if i["validation_status"] == "Invalid")

            return {
                "items": parsed_items,
                "total_rows": len(parsed_items),
                "valid_count": valid_count,
                "duplicate_count": duplicate_count,
                "invalid_count": invalid_count,
                "errors_report": errors_report
            }
        finally:
            db.close()

    @staticmethod
    def commit_imported_students(selected_items: List[Dict[str, Any]]) -> Tuple[bool, int, str]:
        """Commits selected valid student records to SQLite database."""
        db = get_db()
        imported_count = 0
        try:
            user = AuthController.get_current_user()
            user_id = user.id if user else None

            for item in selected_items:
                if not item.get("is_importable"):
                    continue

                student = Student(
                    admission_no=item["admission_no"],
                    roll_no=item["roll_no"],
                    name=item["name"],
                    date_of_birth=item.get("date_of_birth"),
                    class_name=item.get("course") or item.get("class_name") or "",
                    section=item.get("section", ""),
                    course=item.get("course", "General"),
                    branch=item.get("branch", ""),
                    year=item.get("year", ""),
                    semester=item.get("semester", ""),
                    father_name=item["father_name"],
                    mother_name=item["mother_name"],
                    mobile=item["mobile"],
                    aadhaar_number=item.get("aadhaar_number"),
                    address=item["address"],
                    admission_date=item["admission_date"],
                    academic_session=item["academic_session"],
                    status=item["status"]
                )
                db.add(student)
                imported_count += 1

            if imported_count > 0:
                audit = AuditLog(
                    user_id=user_id,
                    action="BULK_IMPORT_STUDENTS",
                    details=f"Successfully imported {imported_count} student records via bulk import wizard."
                )
                db.add(audit)
                db.commit()
                logger.info(f"Bulk student import committed: {imported_count} students added.")

            return True, imported_count, f"Successfully imported {imported_count} students into database."
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing bulk import: {e}", exc_info=True)
            return False, 0, f"Database import error: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def export_error_report(errors_report: List[Dict[str, Any]], output_path: Optional[str] = None) -> Tuple[bool, str]:
        """Exports import error report details to a CSV file."""
        headers = ["Row Number", "Admission No", "Student Name", "Column / Field", "Reason", "Suggested Fix"]
        rows = []
        for err in errors_report:
            rows.append([
                str(err.get("Row Number", "")),
                err.get("Admission No", ""),
                err.get("Student Name", ""),
                err.get("Column / Field", ""),
                err.get("Reason", ""),
                err.get("Suggested Fix", "")
            ])

        if not output_path:
            output_path = str(EXPORTS_DIR / f"import_error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        return ExportService.export_to_csv(headers, rows, filename_prefix="Import_Error_Report", output_path=output_path)
