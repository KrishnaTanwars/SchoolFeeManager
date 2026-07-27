"""
Flask Web Application matching the EXACT 1:1 Desktop EXE Layout & Theme.
Serves full interactive web ERP on Vercel and local deployments.
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

# Exact 1:1 PySide6 Desktop GUI HTML & CSS Replica
EXACT_DESKTOP_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Fee Management System - Executive ERP</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Inter, system-ui, sans-serif; }
        body, html { height: 100%; margin: 0; padding: 0; background-color: #f8fafc; overflow: hidden; }
        
        /* 1:1 PySide6 Desktop ERP Layout Container */
        .app-container { display: flex; height: 100vh; width: 100vw; }
        
        /* Left Dark Sidebar (#0f172a) */
        .sidebar { width: 250px; background-color: #0f172a; border-right: 1px solid #1e293b; display: flex; flex-direction: column; padding: 15px 10px; flex-shrink: 0; }
        .sidebar-brand { color: #ffffff; font-size: 16px; font-weight: 800; padding: 10px; letter-spacing: 0.5px; }
        .sidebar-sub { color: #38bdf8; font-size: 11px; font-weight: 600; padding-left: 10px; margin-bottom: 20px; }
        .nav-btn { background: transparent; color: #94a3b8; border: none; border-radius: 8px; padding: 12px 14px; text-align: left; font-size: 13px; font-weight: 600; width: 100%; margin-bottom: 5px; cursor: pointer; transition: all 0.2s; }
        .nav-btn:hover { background-color: #1e293b; color: #38bdf8; }
        .nav-btn.active { background-color: #1e3a8a; color: #ffffff; font-weight: 700; }
        
        /* Main Workspace Container */
        .main-wrapper { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; }
        
        /* Top Header Bar (#HeaderFrame) */
        .top-header { background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; height: 60px; }
        .header-title { font-size: 18px; font-weight: 800; color: #1e3a8a; }
        .header-user { font-size: 12px; font-weight: 600; color: #475569; }
        
        /* Content Area */
        .content-body { padding: 20px; overflow-y: auto; flex-grow: 1; }
        
        /* KPI Cards */
        .kpi-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .kpi-title { color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; }
        .kpi-val { font-size: 22px; font-weight: 800; margin-top: 4px; }
        
        /* Tables */
        .table-custom { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }
        .table-custom th { background: #1e3a8a; color: #ffffff; font-weight: 700; font-size: 12px; }
        
        /* Exact Desktop Fee Table */
        .fee-table { height: 260px; overflow-y: auto; border: 1px solid #cbd5e1; border-radius: 6px; background: white; }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- 1:1 Desktop Left Sidebar -->
        <div class="sidebar">
            <div class="sidebar-brand"><i class="fa-solid fa-graduation-cap me-2 text-primary"></i>SCHOOL FEE MANAGER</div>
            <div class="sidebar-sub">v2.0 Professional ERP</div>
            
            <button class="nav-btn active" id="btn-nav-dash" onclick="switchView('dash')"><i class="fa-solid fa-chart-line me-2"></i>Executive Dashboard</button>
            <button class="nav-btn" id="btn-nav-collect" onclick="switchView('collect')"><i class="fa-solid fa-credit-card me-2"></i>Collect Fee / Receipt</button>
            <button class="nav-btn" id="btn-nav-students" onclick="switchView('students')"><i class="fa-solid fa-user-graduate me-2"></i>Student Master Directory</button>
            <button class="nav-btn" id="btn-nav-history" onclick="switchView('history')"><i class="fa-solid fa-clock-rotate-left me-2"></i>Receipt History Ledger</button>
            <button class="nav-btn" id="btn-nav-reports" onclick="switchView('history')"><i class="fa-solid fa-file-invoice-dollar me-2"></i>Financial Audit Reports</button>
            <button class="nav-btn" id="btn-nav-settings" onclick="switchView('dash')"><i class="fa-solid fa-gear me-2"></i>Database & Settings</button>

            <div class="mt-auto text-muted small px-2">Logged in as: <strong>Admin</strong></div>
        </div>

        <!-- Main Workspace -->
        <div class="main-wrapper">
            <!-- Top Header -->
            <div class="top-header">
                <div class="header-title" id="page-title">Executive Dashboard & Quick Actions</div>
                <div class="header-user"><i class="fa-solid fa-user-shield text-success me-1"></i> Logged in as: <strong>System Administrator (Admin)</strong></div>
            </div>

            <!-- Body Views -->
            <div class="content-body">
                <!-- 1. DASHBOARD VIEW -->
                <div id="view-dash" class="view-sec">
                    <!-- Quick Actions Hub at Top -->
                    <div class="card p-3 mb-4 border-0 shadow-sm">
                        <h6 class="fw-bold text-primary mb-3"><i class="fa-solid fa-bolt text-warning me-2"></i>Quick Management Actions</h6>
                        <div class="row g-2">
                            <div class="col-md-3"><button class="btn btn-success w-100 fw-bold py-2" onclick="switchView('collect')"><i class="fa-solid fa-credit-card me-1"></i> Collect Fee / Issue Receipt</button></div>
                            <div class="col-md-3"><button class="btn btn-primary w-100 fw-bold py-2" onclick="switchView('students')"><i class="fa-solid fa-user-plus me-1"></i> Register New Student</button></div>
                            <div class="col-md-3"><button class="btn btn-outline-secondary w-100 fw-bold py-2" onclick="switchView('history')"><i class="fa-solid fa-chart-pie me-1"></i> Financial Reports & Audit</button></div>
                            <div class="col-md-3"><a href="/download-sample-csv" class="btn btn-outline-dark w-100 fw-bold py-2"><i class="fa-solid fa-download me-1"></i> Download Sample CSV</a></div>
                        </div>
                    </div>

                    <!-- Recent Receipts + Stats -->
                    <div class="row g-3">
                        <div class="col-md-8">
                            <div class="card p-3 border-0 shadow-sm">
                                <h6 class="fw-bold text-navy mb-3"><i class="fa-solid fa-receipt me-2"></i>Recent Fee Receipts Ledger</h6>
                                <table class="table table-hover align-middle mb-0 border">
                                    <thead class="table-dark">
                                        <tr><th>Receipt No</th><th>Date</th><th>Student Name</th><th>Class</th><th>Paid (₹)</th><th>Action</th></tr>
                                    </thead>
                                    <tbody>
                                        {% for r in recent_receipts %}
                                        <tr>
                                            <td><span class="badge bg-primary">{{ r.receipt_no }}</span></td>
                                            <td>{{ r.receipt_date.strftime('%d-%m-%Y') }}</td>
                                            <td><strong>{{ r.student.name if r.student else 'N/A' }}</strong></td>
                                            <td>{{ r.student.class_name if r.student else 'N/A' }}</td>
                                            <td class="text-success fw-bold">₹ {{ "%.2f"|format(r.paid_amount or r.total_amount or 0) }}</td>
                                            <td><a href="/pdf/{{ r.id }}" target="_blank" class="btn btn-sm btn-dark"><i class="fa-solid fa-eye me-1"></i> View / Print</a></td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card p-3 border-0 shadow-sm">
                                <h6 class="fw-bold text-navy mb-3"><i class="fa-solid fa-chart-bar me-2"></i>Student Statistics by Class</h6>
                                <table class="table table-striped border">
                                    <thead><tr><th>Class</th><th>Enrolled</th></tr></thead>
                                    <tbody>
                                        {% for stat in class_stats %}
                                        <tr><td>{{ stat.class_name }}</td><td><span class="badge bg-purple" style="background:#7c3aed;">{{ stat.student_count }} Students</span></td></tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 2. COLLECT FEE VIEW (Exact 260px Fee Heads Particulars Table + 2-Column Bottom Layout) -->
                <div id="view-collect" class="view-sec d-none">
                    <div class="card p-3 border-0 shadow-sm mb-3">
                        <div class="row g-3 align-items-center">
                            <div class="col-md-6">
                                <label class="fw-bold text-primary mb-1">1. Select Student:</label>
                                <select name="student_id" id="sel_student" class="form-select fw-bold border-primary" required>
                                    {% for s in students %}
                                    <option value="{{ s.id }}">{{ s.name }} (Adm No: {{ s.admission_no }}) - Class {{ s.class_name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            <div class="col-md-6 text-end">
                                <span class="badge bg-secondary p-2">Next Receipt No: <strong>REC/2024/00039</strong></span>
                            </div>
                        </div>
                    </div>

                    <!-- Fee Particulars Table (260px Minimum Height Guarantee) -->
                    <div class="card p-3 border-0 shadow-sm mb-3">
                        <h6 class="fw-bold text-navy mb-2"><i class="fa-solid fa-list-check me-2"></i>2. Fee Heads Particulars (Flexible Payment)</h6>
                        <div class="fee-table">
                            <table class="table table-bordered align-middle mb-0">
                                <thead style="background:#1e3a8a; color:white; position:sticky; top:0;">
                                    <tr><th style="width:40px;">Select</th><th>Fee Head Name</th><th>Code</th><th style="width:180px;">Amount (₹)</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td><input type="checkbox" checked class="fee-chk" value="2000" onchange="recalc()"></td><td>Admission Fee</td><td>ADM</td><td><input type="number" class="form-control form-control-sm fee-amt" value="2000.00" oninput="recalc()"></td></tr>
                                    <tr><td><input type="checkbox" checked class="fee-chk" value="1500" onchange="recalc()"></td><td>Tuition Fee</td><td>TUT</td><td><input type="number" class="form-control form-control-sm fee-amt" value="1500.00" oninput="recalc()"></td></tr>
                                    <tr><td><input type="checkbox" checked class="fee-chk" value="800" onchange="recalc()"></td><td>Computer Fee</td><td>CMP</td><td><input type="number" class="form-control form-control-sm fee-amt" value="800.00" oninput="recalc()"></td></tr>
                                    <tr><td><input type="checkbox" checked class="fee-chk" value="500" onchange="recalc()"></td><td>Development Fee</td><td>DEV</td><td><input type="number" class="form-control form-control-sm fee-amt" value="500.00" oninput="recalc()"></td></tr>
                                    <tr><td><input type="checkbox" checked class="fee-chk" value="200" onchange="recalc()"></td><td>Examination Fee</td><td>EXM</td><td><input type="number" class="form-control form-control-sm fee-amt" value="200.00" oninput="recalc()"></td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- 2-Column Bottom Payment Grid -->
                    <form action="/create-receipt-web" method="POST">
                        <input type="hidden" name="student_id" id="hidden_student_id" value="1">
                        <div class="row g-3">
                            <!-- Left Column: Totals & Dues -->
                            <div class="col-md-6">
                                <div class="card p-3 border-0 shadow-sm">
                                    <h6 class="fw-bold text-navy border-bottom pb-2">Calculation & Totals</h6>
                                    <div class="d-flex justify-content-between mb-2"><span>Subtotal:</span><strong id="lbl_subtotal">₹ 5,000.00</strong></div>
                                    <div class="d-flex justify-content-between mb-2 align-items-center"><span>Discount (-):</span><input type="number" name="discount" id="inp_discount" class="form-control form-control-sm w-50" value="0.00" oninput="recalc()"></div>
                                    <div class="d-flex justify-content-between mb-2 align-items-center"><span>Fine / Penalty (+):</span><input type="number" name="fine" id="inp_fine" class="form-control form-control-sm w-50" value="0.00" oninput="recalc()"></div>
                                    <hr>
                                    <div class="d-flex justify-content-between mb-2"><span class="fw-bold">Total Calculated Fee:</span><strong id="lbl_total" class="text-primary fs-5">₹ 5,000.00</strong></div>
                                    <div class="d-flex justify-content-between mb-2 align-items-center"><span class="fw-bold text-success">ACTUAL PAID AMOUNT:</span><input type="number" step="0.01" name="paid_amount" id="inp_paid" class="form-control form-control-sm w-50 fw-bold border-success text-success" value="4000.00" oninput="recalc()"></div>
                                    <div class="d-flex justify-content-between mb-2"><span class="fw-bold text-danger">Remaining Due:</span><strong id="lbl_due" class="text-danger fs-5">₹ 1,000.00</strong></div>
                                </div>
                            </div>
                            
                            <!-- Right Column: Mode & Generate Button -->
                            <div class="col-md-6">
                                <div class="card p-3 border-0 shadow-sm h-100 d-flex flex-column justify-content-between">
                                    <div>
                                        <h6 class="fw-bold text-navy border-bottom pb-2">Payment Details</h6>
                                        <div class="mb-3">
                                            <label class="form-label fw-bold">Payment Mode:</label>
                                            <select name="payment_mode" class="form-select">
                                                <option value="Cash">Cash</option>
                                                <option value="UPI / QR">UPI / QR</option>
                                                <option value="Cheque">Cheque</option>
                                                <option value="Net Banking / NEFT">Net Banking / NEFT</option>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">UTR / Cheque / Ref Number:</label>
                                            <input type="text" name="utr_number" class="form-control" placeholder="Optional transaction reference">
                                        </div>
                                    </div>
                                    <button type="submit" class="btn btn-success btn-lg w-100 fw-bold py-3 mt-3"><i class="fa-solid fa-print me-2"></i> GENERATE & PRINT RECEIPT</button>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>

                <!-- 3. STUDENT MASTER VIEW (Top Active Students KPI) -->
                <div id="view-students" class="view-sec d-none">
                    <!-- Top Active Students KPI Card -->
                    <div class="kpi-card mb-3 border-start border-purple border-4" style="border-left: 5px solid #7c3aed !important;">
                        <div class="kpi-title">ACTIVE REGISTERED STUDENTS</div>
                        <div class="kpi-val text-purple" style="color:#7c3aed;">{{ students|length }} Active Students</div>
                    </div>

                    <div class="card p-3 border-0 shadow-sm">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="fw-bold text-navy mb-0"><i class="fa-solid fa-users me-2"></i>Student Directory & Fee History</h6>
                            <a href="/download-sample-csv" class="btn btn-sm btn-outline-primary"><i class="fa-solid fa-file-csv me-1"></i> Download Sample CSV</a>
                        </div>
                        <table class="table table-hover border align-middle">
                            <thead class="table-dark">
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

                <!-- 4. RECEIPT HISTORY VIEW (Top Collection KPIs) -->
                <div id="view-history" class="view-sec d-none">
                    <!-- Relocated KPI Cards Banner -->
                    <div class="row g-3 mb-3">
                        <div class="col-md-4">
                            <div class="kpi-card border-start border-success border-4" style="border-left:5px solid #059669 !important;">
                                <div class="kpi-title">TODAY'S COLLECTION</div>
                                <div class="kpi-val text-success">₹ {{ "%.2f"|format(today_col) }}</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="kpi-card border-start border-primary border-4" style="border-left:5px solid #2563eb !important;">
                                <div class="kpi-title">MONTHLY COLLECTION</div>
                                <div class="kpi-val text-primary">₹ {{ "%.2f"|format(month_col) }}</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="kpi-card border-start border-warning border-4" style="border-left:5px solid #d97706 !important;">
                                <div class="kpi-title">RECEIPTS ISSUED TODAY</div>
                                <div class="kpi-val text-warning">{{ receipts_today }}</div>
                            </div>
                        </div>
                    </div>

                    <div class="card p-3 border-0 shadow-sm">
                        <h6 class="fw-bold text-navy mb-3"><i class="fa-solid fa-clock-rotate-left me-2"></i>Complete Receipt History Ledger</h6>
                        <table class="table table-hover border align-middle">
                            <thead class="table-dark">
                                <tr><th>Receipt No</th><th>Date</th><th>Student Name</th><th>Total Fee</th><th>Paid Amount</th><th>Remaining Due</th><th>Payment Mode</th><th>Action</th></tr>
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
                                    <td><a href="/pdf/{{ r.id }}" target="_blank" class="btn btn-sm btn-dark"><i class="fa-solid fa-file-pdf me-1"></i> PDF</a></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchView(viewName) {
            document.querySelectorAll('.view-sec').forEach(el => el.classList.add('d-none'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById('view-' + viewName).classList.remove('d-none');
            const btn = document.getElementById('btn-nav-' + viewName);
            if(btn) btn.classList.add('active');

            const titles = {
                'dash': 'Executive Dashboard & Quick Actions',
                'collect': 'Fee Collection & Flexible Payment',
                'students': 'Student Master Directory',
                'history': 'Receipt History & Financial Ledger'
            };
            document.getElementById('page-title').innerText = titles[viewName] || 'Executive ERP';
        }

        function recalc() {
            let sum = 0;
            document.querySelectorAll('.fee-chk:checked').forEach(chk => {
                const tr = chk.closest('tr');
                const amt = parseFloat(tr.querySelector('.fee-amt').value) || 0;
                sum += amt;
            });
            const disc = parseFloat(document.getElementById('inp_discount').value) || 0;
            const fine = parseFloat(document.getElementById('inp_fine').value) || 0;
            const tot = Math.max(0, sum - disc + fine);
            
            document.getElementById('lbl_subtotal').innerText = '₹ ' + sum.toFixed(2);
            document.getElementById('lbl_total').innerText = '₹ ' + tot.toFixed(2);
            
            const paid = parseFloat(document.getElementById('inp_paid').value) || 0;
            const due = Math.max(0, tot - paid);
            document.getElementById('lbl_due').innerText = '₹ ' + due.toFixed(2);
        }

        document.getElementById('sel_student').addEventListener('change', function() {
            document.getElementById('hidden_student_id').value = this.value;
        });
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
        EXACT_DESKTOP_TEMPLATE,
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
            return "Receipt not found", 404
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
    student_id = int(request.form.get("student_id", 1))
    payment_mode = request.form.get("payment_mode", "Cash")
    paid_amt = float(request.form.get("paid_amount", 4000.0))
    utr_no = request.form.get("utr_number", "")

    items = [{"fee_category_id": 1, "category_name": "Tution & Development Fee", "amount": paid_amt}]

    success, msg, receipt = ReceiptController.create_receipt(
        student_id=student_id,
        academic_session="2024-2025",
        items=items,
        paid_amount=paid_amt,
        payment_mode=payment_mode,
        utr_number=utr_no
    )
    if success:
        pdf_path = PDFService.generate_receipt_pdf(receipt)
        return send_file(pdf_path, mimetype='application/pdf')
    return f"Error: {msg}", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
