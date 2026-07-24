"""
ReportLab Utility Script to convert INSTALLATION_GUIDE.md and USER_MANUAL.md into commercial A4 PDF documents.
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_installation_guide_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=18, leading=22, textColor=colors.HexColor("#1e3a8a"), alignment=0
    )
    h2_style = ParagraphStyle(
        'H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=12, leading=16, textColor=colors.HexColor("#1e3a8a"), spaceBefore=10, spaceAfter=4
    )
    h3_style = ParagraphStyle(
        'H3Style', parent=styles['Heading3'], fontName='Helvetica-Bold',
        fontSize=10, leading=14, textColor=colors.HexColor("#334155"), spaceBefore=6, spaceAfter=2
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontName='Helvetica',
        fontSize=9.5, leading=13.5, textColor=colors.HexColor("#0f172a")
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style, leftIndent=12, firstLineIndent=-8
    )
    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=9, leading=12, textColor=colors.white
    )
    tb_style = ParagraphStyle(
        'TB', parent=styles['Normal'], fontName='Helvetica',
        fontSize=8.5, leading=11.5, textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Title & Divider
    story.append(Paragraph("Installation & Setup Guide", title_style))
    story.append(Paragraph("<font size=10 color='#64748b'><b>School Fee Management System v1.0</b></font>", body_style))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=5*mm))

    # System Requirements
    story.append(Paragraph("System Requirements", h2_style))
    reqs = [
        "<b>Operating System:</b> Microsoft Windows 10 or Windows 11 (64-bit Edition)",
        "<b>Processor:</b> Intel Core i3 / AMD Ryzen 3 or higher",
        "<b>RAM:</b> Minimum 4 GB (8 GB Recommended)",
        "<b>Disk Space:</b> 500 MB free space",
        "<b>Display Resolution:</b> 1366x768 or higher (High DPI / 4K Displays supported)",
        "<b>Printer:</b> Any standard Windows-compatible printer (LaserJet, InkJet, Thermal, or PDF virtual printer)"
    ]
    for r in reqs:
        story.append(Paragraph(f"• {r}", bullet_style))
        story.append(Spacer(1, 1.5 * mm))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=4*mm))

    # 1. Quick Installation Steps
    story.append(Paragraph("1. Quick Installation Steps", h2_style))
    steps = [
        "1. Extract the client release ZIP file <b>SchoolFeeManager_v1.0.zip</b> to your target directory (e.g., <font color='#1e3a8a'><b>C:\\SchoolFeeManager</b></font>).",
        "2. Navigate to the extracted <b>SchoolFeeManager</b> folder.",
        "3. Double-click <b>SchoolFeeManager.exe</b> to launch the software.",
        "<i>(Optional) Right-click <b>SchoolFeeManager.exe</b> -> Select <b>Send to -> Desktop (create shortcut)</b> for instant access.</i>"
    ]
    for st in steps:
        story.append(Paragraph(st, body_style))
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=4*mm))

    # 2. Initial Setup & Default Login Credentials
    story.append(Paragraph("2. Initial Setup & Default Login Credentials", h2_style))
    story.append(Paragraph("On first startup, the application automatically initializes the SQLite database and seeds default user accounts:", body_style))
    story.append(Spacer(1, 3 * mm))

    table_data = [
        [Paragraph("User Role", th_style), Paragraph("Default Username", th_style), Paragraph("Default Password", th_style), Paragraph("Recommended Usage", th_style)],
        [Paragraph("<b>System Administrator</b>", tb_style), Paragraph("admin", tb_style), Paragraph("admin123", tb_style), Paragraph("Full access to settings, user management, & restores.", tb_style)],
        [Paragraph("<b>Fee Collection Operator</b>", tb_style), Paragraph("operator", tb_style), Paragraph("operator123", tb_style), Paragraph("Fee collection, student registration, & receipt searching.", tb_style)]
    ]

    cred_table = Table(table_data, colWidths=[40*mm, 32*mm, 32*mm, 76*mm])
    cred_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cred_table)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("<font color='#dc2626'><b>IMPORTANT:</b></font> Change default administrator password after first login via <b>Settings & Backup -> User Management</b>.", body_style))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=4*mm))

    # 3. Database & Backup Directory Locations
    story.append(Paragraph("3. Database & Backup Directory Locations", h2_style))
    dirs = [
        "<b>database/school_fee.db</b>: Main SQLite relational database storing student profiles, fee heads, and receipt ledgers.",
        "<b>backup/</b>: Automated timestamped ZIP backup directory created during manual or scheduled backups.",
        "<b>exports/</b>: Generated fee receipt PDFs and CSV reports exported from the application.",
        "<b>logs/app.log</b>: Application activity and error diagnostic log file."
    ]
    for d in dirs:
        story.append(Paragraph(f"• {d}", bullet_style))
        story.append(Spacer(1, 1.5 * mm))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=4*mm))

    # 4. Troubleshooting & FAQ
    story.append(Paragraph("4. Troubleshooting & FAQ", h2_style))
    story.append(Paragraph("<b>Q: The application fails to print fee receipts.</b>", h3_style))
    story.append(Paragraph("<b>A:</b> Ensure a default Windows printer is configured in <b>Windows Control Panel -> Devices and Printers</b>. The application routes receipts directly through the native Windows Shell printer driver.", body_style))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("<b>Q: How do I move the software to a new computer?</b>", h3_style))
    story.append(Paragraph("<b>A:</b><br/>1. Run a database backup in <b>Settings & Backup -> Create Database Backup</b>.<br/>2. Copy the generated .zip file to the new computer.<br/>3. Install SchoolFeeManager.exe on the new computer and use <b>Settings & Backup -> Restore Database</b>.", body_style))

    doc.build(story)
    print(f"SUCCESS: Created {output_path}")

def build_user_manual_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=18, leading=22, textColor=colors.HexColor("#1e3a8a"), alignment=0
    )
    h2_style = ParagraphStyle(
        'H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=11.5, leading=15, textColor=colors.HexColor("#1e3a8a"), spaceBefore=8, spaceAfter=3
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontName='Helvetica',
        fontSize=9, leading=12.5, textColor=colors.HexColor("#0f172a")
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style, leftIndent=10, firstLineIndent=-6
    )

    story = []

    # Title & Header
    story.append(Paragraph("School Fee Management System v1.0", title_style))
    story.append(Paragraph("<font size=10 color='#64748b'><b>Commercial User Operations Manual</b></font>", body_style))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=4*mm))

    # Sections 1 to 7
    sections = [
        ("1. Logging In", [
            "1. Launch <b>SchoolFeeManager.exe</b>.",
            "2. Enter credentials on login screen (Administrator: <b>admin / admin123</b> | Operator: <b>operator / operator123</b>).",
            "3. Click <b>LOG IN TO ERP</b>."
        ]),
        ("2. Registering & Managing Students", [
            "1. Click <b>👨‍🎓 Student Master</b> in the left sidebar.",
            "2. Click <b>+ Register New Student</b>.",
            "3. Fill in student info: Admission No (unique), Roll No, Student Name, Father's Name, Mother's Name, Class & Section, 10-digit Mobile, Address.",
            "4. Click <b>Save Student</b>.",
            "5. Use top search bar to filter students instantly by name, admission no, or mobile."
        ]),
        ("3. Managing Fee Categories / Heads", [
            "1. Click <b>🏷️ Fee Heads</b> in the left sidebar.",
            "2. Click <b>+ Add New Fee Category / Head</b> to configure custom fee heads (Tuition, Transport, Fine, Computer Fee, etc.).",
            "3. Set default amounts and active status.",
            "4. Existing fee heads can be edited or disabled at any time."
        ]),
        ("4. Fee Collection & Receipt Generation", [
            "1. Click <b>💳 Collect Fee</b> in the left sidebar.",
            "2. Search student name or admission number in <b>1. Select Student</b>.",
            "3. Select student to load profile and outstanding balance.",
            "4. Check fee heads to collect in <b>2. Fee Particulars</b>.",
            "5. Adjust amounts, add discount (-) or fine (+). Total Amount & Amount in Words update in real-time.",
            "6. Select payment mode (Cash, UPI, Cheque, DD, Net Banking) and reference number.",
            "7. Click <b>GENERATE & PRINT RECEIPT</b>.",
            "8. A commercial A4 receipt preview will open for instant thermal/A4 printing or PDF saving."
        ]),
        ("5. Receipt History & Searching", [
            "1. Click <b>📜 Receipt History</b> in the left sidebar.",
            "2. View generated receipts ledger sorted chronologically.",
            "3. Filter by date range or search student name / admission no.",
            "4. Click <b>View / Print</b> on any row to reprint receipt copy.",
            "5. Click <b>Export CSV</b> to download the transaction ledger."
        ]),
        ("6. Financial Reports & Analytics", [
            "1. Click <b>📈 Financial Reports</b> in the left sidebar.",
            "2. Select report type: Daily Collection, Monthly Collection, Custom Date Range, or Class-Wise Summary.",
            "3. Click <b>Generate Report</b> to calculate summary metrics.",
            "4. Click <b>Export Report PDF</b> or <b>Export CSV</b> to save report."
        ]),
        ("7. Database Backup & Disaster Recovery", [
            "1. Click <b>⚙️ Settings & Backup</b> in the left sidebar.",
            "2. Go to <b>Backup & Restore</b> tab.",
            "3. <b>Backup:</b> Click <b>Create Immediate Backup ZIP</b> to save timestamped ZIP backup.",
            "4. <b>Restore:</b> Click <b>Restore Database from ZIP</b>, select backup file, and confirm."
        ])
    ]

    for title, steps in sections:
        sec_flowables = [
            Paragraph(title, h2_style),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=2*mm)
        ]
        for st in steps:
            sec_flowables.append(Paragraph(st, body_style))
            sec_flowables.append(Spacer(1, 1 * mm))
        sec_flowables.append(Spacer(1, 2 * mm))
        story.append(KeepTogether(sec_flowables))

    doc.build(story)
    print(f"SUCCESS: Created {output_path}")

if __name__ == "__main__":
    build_installation_guide_pdf("INSTALLATION_GUIDE.pdf")
    build_user_manual_pdf("USER_MANUAL.pdf")
