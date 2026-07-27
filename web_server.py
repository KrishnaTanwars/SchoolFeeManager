"""
Flask Web Application for School Fee Management System.
Allows client testing directly from mobile (iPhone/Android) or laptop web browsers.
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.database import init_db, get_db
from models.student import Student
from models.receipt import Receipt
from controllers.student_controller import StudentController
from controllers.receipt_controller import ReceiptController
from controllers.report_controller import ReportController
from services.pdf_service import PDFService
from utils.helpers import format_currency, format_date

app = Flask(__name__)
init_db()

# Main HTML Web Template (Responsive for Mobile & Laptop)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Fee Management System - Web Preview</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --navy: #1e3a8a; --sky: #0284c7; --emerald: #10b981; }
        body { background-color: #f8fafc; font-family: 'Segoe UI', system-ui, sans-serif; }
        .navbar-brand { font-weight: 800; color: var(--navy) !important; font-size: 1.3rem; }
        .card-kpi { border-radius: 10px; border: none; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card-kpi .val { font-size: 1.6rem; font-weight: 800; }
        .btn-custom-navy { background-color: var(--navy); color: white; font-weight: 600; }
        .btn-custom-navy:hover { background-color: #1e40af; color: white; }
        .btn-custom-emerald { background-color: var(--emerald); color: white; font-weight: bold; }
        .btn-custom-emerald:hover { background-color: #059669; color: white; }
        .table-responsive { background: white; border-radius: 8px; border: 1px solid #e2e8f0; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm px-4">
        <a class="navbar-brand" href="#"><i class="fa-solid fa-school text-primary me-2"></i>DPS International Public School</a>
        <span class="badge bg-primary ms-auto">Web Live Demo v2.0</span>
    </nav>

    <div class="container-fluid py-4 px-4">
        <!-- Navigation Tabs -->
        <ul class="nav nav-pills mb-4 gap-2" id="mainTabs">
            <li class="nav-item"><a class="nav-link active" id="tab-dash" href="#dashboard" onclick="showTab('dashboard')"><i class="fa-solid fa-gauge me-1"></i> Dashboard</a></li>
            <li class="nav-item"><a class="nav-link" id="tab-collect" href="#collect" onclick="showTab('collect')"><i class="fa-solid fa-receipt me-1"></i> Collect Fee</a></li>
            <li class="nav-item"><a class="nav-link" id="tab-students" href="#students" onclick="showTab('students')"><i class="fa-solid fa-users me-1"></i> Student Master</a></li>
            <li class="nav-item"><a class="nav-link" id="tab-history" href="#history" onclick="showTab('history')"><i class="fa-solid fa-clock-rotate-left me-1"></i> Receipt History</a></li>
        </ul>

        <!-- DASHBOARD TAB -->
        <div id="sec-dashboard" class="tab-sec">
            <div class="card mb-4 p-3 border-0 shadow-sm bg-white">
                <h5 class="fw-bold text-navy mb-3"><i class="fa-solid fa-bolt text-warning me-2"></i>Quick Management Actions</h5>
                <div class="row g-3">
                    <div class="col-md-3"><button class="btn btn-custom-emerald w-100 py-2" onclick="showTab('collect')"><i class="fa-solid fa-credit-card me-2"></i> Collect Fee / Issue Receipt</button></div>
                    <div class="col-md-3"><button class="btn btn-primary w-100 py-2" onclick="showTab('students')"><i class="fa-solid fa-user-plus me-2"></i> Register New Student</button></div>
                    <div class="col-md-3"><button class="btn btn-outline-secondary w-100 py-2" onclick="showTab('history')"><i class="fa-solid fa-chart-line me-2"></i> Financial Receipts Ledger</button></div>
                    <div class="col-md-3"><a href="/download-sample-csv" class="btn btn-outline-info w-100 py-2"><i class="fa-solid fa-file-csv me-2"></i> Download Sample CSV</a></div>
                </div>
            </div>

            <div class="row g-3">
                <div class="col-md-8">
                    <div class="card border-0 shadow-sm p-3">
                        <h6 class="fw-bold text-navy"><i class="fa-solid fa-list me-2"></i>Recent Fee Receipts Ledger</h6>
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr><th>Receipt No</th><th>Date</th><th>Student Name</th><th>Class</th><th>Paid Amount</th><th>Action</th></tr>
                                </thead>
                                <tbody>
                                    {% for r in recent_receipts %}
                                    <tr>
                                        <td><span class="badge bg-secondary">{{ r.receipt_no }}</span></td>
                                        <td>{{ r.receipt_date.strftime('%d-%m-%Y') }}</td>
                                        <td><strong>{{ r.student.name if r.student else 'N/A' }}</strong></td>
                                        <td>{{ r.student.class_name if r.student else 'N/A' }}</td>
                                        <td class="text-success fw-bold">₹ {{ "%.2f"|format(r.paid_amount or r.total_amount or 0) }}</td>
                                        <td><a href="/pdf/{{ r.id }}" target="_blank" class="btn btn-sm btn-custom-navy"><i class="fa-solid fa-file-pdf me-1"></i> PDF</a></td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-0 shadow-sm p-3">
                        <h6 class="fw-bold text-navy"><i class="fa-solid fa-chart-pie me-2"></i>Student Stats by Class</h6>
                        <div class="table-responsive">
                            <table class="table table-striped mb-0">
                                <thead><tr><th>Class</th><th>Enrolled</th></tr></thead>
                                <tbody>
                                    {% for stat in class_stats %}
                                    <tr><td>{{ stat.class_name }}</td><td><span class="badge bg-info">{{ stat.student_count }} Students</span></td></tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- COLLECT FEE TAB -->
        <div id="sec-collect" class="tab-sec d-none">
            <div class="card border-0 shadow-sm p-4">
                <h5 class="fw-bold text-navy mb-3"><i class="fa-solid fa-calculator me-2"></i>Fee Collection & Flexible Payment</h5>
                <form action="/create-receipt-web" method="POST">
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label fw-bold">Select Student:</label>
                            <select name="student_id" class="form-select" required onchange="onStudentSelect(this)">
                                <option value="">-- Choose Active Student --</option>
                                {% for s in students %}
                                <option value="{{ s.id }}">{{ s.name }} (Adm: {{ s.admission_no }}) - {{ s.class_name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-bold">Payment Mode:</label>
                            <select name="payment_mode" class="form-select" id="payModeSelect" onchange="togglePayFields(this.value)">
                                <option value="Cash">Cash</option>
                                <option value="UPI / QR">UPI / QR</option>
                                <option value="Cheque">Cheque</option>
                                <option value="Demand Draft (DD)">Demand Draft (DD)</option>
                                <option value="Net Banking / NEFT">Net Banking / NEFT</option>
                            </select>
                        </div>
                    </div>

                    <div class="row g-3 mb-3">
                        <div class="col-md-4">
                            <label class="form-label fw-bold">Total Calculated Fee (₹):</label>
                            <input type="number" step="0.01" name="total_amount" id="total_amount" class="form-control fw-bold text-primary" value="5000.00" oninput="calcDue()">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-bold text-success">ACTUAL PAID AMOUNT (₹):</label>
                            <input type="number" step="0.01" name="paid_amount" id="paid_amount" class="form-control fw-bold text-success" value="4000.00" oninput="calcDue()">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-bold text-danger">REMAINING DUE (₹):</label>
                            <input type="text" id="due_amount" class="form-control fw-bold text-danger" value="₹ 1000.00" readonly>
                        </div>
                    </div>

                    <div id="upi-fields" class="row g-3 mb-3 d-none">
                        <div class="col-md-6">
                            <label class="form-label">UTR Number:</label>
                            <input type="text" name="utr_number" class="form-control" placeholder="Enter 12-digit UTR No">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Bank Name:</label>
                            <input type="text" name="bank_name" class="form-control" placeholder="HDFC Bank, SBI, etc.">
                        </div>
                    </div>

                    <button type="submit" class="btn btn-custom-emerald px-4 py-2 mt-2"><i class="fa-solid fa-print me-2"></i> Issue Fee Receipt PDF</button>
                </form>
            </div>
        </div>

        <!-- STUDENT MASTER TAB -->
        <div id="sec-students" class="tab-sec d-none">
            <div class="row mb-3 align-items-center">
                <div class="col-md-8">
                    <div class="card card-kpi bg-purple text-white p-3 shadow-sm" style="background-color: #7c3aed;">
                        <span class="text-uppercase fw-bold opacity-75">Active Registered Students</span>
                        <div class="val">{{ students|length }} Students</div>
                    </div>
                </div>
                <div class="col-md-4 text-end">
                    <a href="/download-sample-csv" class="btn btn-outline-primary"><i class="fa-solid fa-file-csv me-1"></i> Download Sample CSV</a>
                </div>
            </div>

            <div class="card border-0 shadow-sm p-3">
                <h6 class="fw-bold text-navy mb-3"><i class="fa-solid fa-users me-2"></i>Student Master Directory</h6>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr><th>Adm No</th><th>Student Name</th><th>Class</th><th>Father Name</th><th>Mobile</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            {% for s in students %}
                            <tr>
                                <td><span class="badge bg-dark">{{ s.admission_no }}</span></td>
                                <td><strong>{{ s.name }}</strong></td>
                                <td>{{ s.class_name }} ({{ s.section or 'A' }})</td>
                                <td>{{ s.father_name }}</td>
                                <td>{{ s.mobile }}</td>
                                <td><span class="badge bg-success">{{ s.status }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- RECEIPT HISTORY TAB -->
        <div id="sec-history" class="tab-sec d-none">
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <div class="card card-kpi bg-white p-3 shadow-sm border-start border-success border-4">
                        <span class="text-muted fw-bold">TODAY'S COLLECTION</span>
                        <div class="val text-success">₹ {{ "%.2f"|format(today_col) }}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card card-kpi bg-white p-3 shadow-sm border-start border-primary border-4">
                        <span class="text-muted fw-bold">MONTHLY COLLECTION</span>
                        <div class="val text-primary">₹ {{ "%.2f"|format(month_col) }}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card card-kpi bg-white p-3 shadow-sm border-start border-warning border-4">
                        <span class="text-muted fw-bold">RECEIPTS ISSUED TODAY</span>
                        <div class="val text-warning">{{ receipts_today }}</div>
                    </div>
                </div>
            </div>

            <div class="card border-0 shadow-sm p-3">
                <h6 class="fw-bold text-navy mb-3"><i class="fa-solid fa-clock-rotate-left me-2"></i>Complete Receipt History Ledger</h6>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr><th>Receipt No</th><th>Date</th><th>Student Name</th><th>Total Fee</th><th>Paid Amount</th><th>Remaining Due</th><th>Payment Mode</th><th>PDF</th></tr>
                        </thead>
                        <tbody>
                            {% for r in all_receipts %}
                            <tr>
                                <td><span class="badge bg-primary">{{ r.receipt_no }}</span></td>
                                <td>{{ r.receipt_date.strftime('%d-%m-%Y') }}</td>
                                <td><strong>{{ r.student.name if r.student else 'N/A' }}</strong></td>
                                <td>₹ {{ "%.2f"|format(r.total_amount) }}</td>
                                <td class="text-success fw-bold">₹ {{ "%.2f"|format(r.paid_amount or r.total_amount or 0) }}</td>
                                <td class="text-danger fw-bold">₹ {{ "%.2f"|format(r.due_amount or 0) }}</td>
                                <td><span class="badge bg-secondary">{{ r.payment_mode }}</span></td>
                                <td><a href="/pdf/{{ r.id }}" target="_blank" class="btn btn-sm btn-custom-navy"><i class="fa-solid fa-file-pdf"></i> View PDF</a></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-sec').forEach(el => el.classList.add('d-none'));
            document.querySelectorAll('#mainTabs .nav-link').forEach(el => el.classList.remove('active'));
            document.getElementById('sec-' + tabName).classList.remove('d-none');
            document.getElementById('tab-' + tabName).classList.add('active');
        }
        function togglePayFields(val) {
            const upiDiv = document.getElementById('upi-fields');
            if(val.includes('UPI') || val.includes('Cheque') || val.includes('Draft') || val.includes('Net')) {
                upiDiv.classList.remove('d-none');
            } else {
                upiDiv.classList.add('d-none');
            }
        }
        function calcDue() {
            const tot = parseFloat(document.getElementById('total_amount').value) || 0;
            const paid = parseFloat(document.getElementById('paid_amount').value) || 0;
            const due = Math.max(0, tot - paid);
            document.getElementById('due_amount').value = '₹ ' + due.toFixed(2);
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    students = StudentController.get_all_students(status_filter="Active")
    all_receipts = ReceiptController.get_all_receipts()
    recent_receipts = all_receipts[:10]
    class_stats = StudentController.get_student_counts_by_class()
    today_col = ReportController.get_today_collection()
    month_col = ReportController.get_monthly_collection()
    receipts_today = ReportController.get_receipts_today_count()

    return render_template_string(
        HTML_TEMPLATE,
        students=students,
        all_receipts=all_receipts,
        recent_receipts=recent_receipts,
        class_stats=class_stats,
        today_col=today_col,
        month_col=month_col,
        receipts_today=receipts_today
    )

@app.route("/pdf/<int:receipt_id>")
def view_pdf(receipt_id):
    db = get_db()
    try:
        receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not receipt:
            return "Receipt not found", 444
        pdf_path = PDFService.generate_receipt_pdf(receipt)
        return send_file(pdf_path, mimetype='application/pdf')
    finally:
        db.close()

@app.route("/download-sample-csv")
def download_sample_csv():
    from services.export_service import ExportService
    csv_path = ExportService.generate_sample_student_csv()
    return send_file(csv_path, as_attachment=True, download_name="sample_students_import.csv")

@app.route("/create-receipt-web", methods=["POST"])
def create_receipt_web():
    student_id = int(request.form.get("student_id"))
    payment_mode = request.form.get("payment_mode", "Cash")
    total_amt = float(request.form.get("total_amount", 5000.0))
    paid_amt = float(request.form.get("paid_amount", 5000.0))
    utr_no = request.form.get("utr_number", "")
    bank_name = request.form.get("bank_name", "")

    items = [{"fee_category_id": 1, "category_name": "Tution & Development Fee", "amount": total_amt}]

    success, msg, receipt = ReceiptController.create_receipt(
        student_id=student_id,
        academic_session="2024-2025",
        items=items,
        paid_amount=paid_amt,
        payment_mode=payment_mode,
        utr_number=utr_no,
        bank_name=bank_name
    )
    if success:
        pdf_path = PDFService.generate_receipt_pdf(receipt)
        return send_file(pdf_path, mimetype='application/pdf')
    return f"Error: {msg}", 400

if __name__ == "__main__":
    print("============================================================")
    print("Starting School Fee Management Web Server on port 5000...")
    print("============================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)
