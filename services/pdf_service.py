"""
ReportLab Commercial A4 PDF Fee Receipt, Student Profile, & Financial Report Generation Service.
Uses 'Rs.' currency notation to prevent Type1 font unicode square box (■) rendering errors.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from config.app_config import EXPORTS_DIR, STUDENT_PHOTOS_DIR
from models.receipt import Receipt
from models.student import Student
from controllers.settings_controller import SettingsController
from utils.helpers import format_date
from utils.logger import logger


class PDFService:
    @staticmethod
    def generate_receipt_pdf(receipt: Receipt, output_path: Optional[str] = None) -> str:
        """
        Generates a commercial A4 single-page Fee Receipt PDF optimized to fit 1 page cleanly.
        """
        if not output_path:
            filename = f"Receipt_{receipt.receipt_no.replace('/', '_')}.pdf"
            output_path = str(EXPORTS_DIR / filename)

        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

        school_info = SettingsController.get_school_info()
        school_name = school_info.school_name if school_info else "DPS International Public School"
        school_addr = school_info.address if school_info else "Plot 12, Sector 5, RK Puram, New Delhi - 110022"
        school_phone = school_info.phone if school_info else "+91 98765 43210, 011-26123456"
        school_email = school_info.email if school_info else "accounts@dpsschool.edu.in"

        # Determine Logo File Path
        logo_path = school_info.logo_path if (school_info and school_info.logo_path and Path(school_info.logo_path).exists()) else None
        if not logo_path:
            default_logo = Path(__file__).resolve().parent.parent / "assets" / "school_logo.png"
            if default_logo.exists():
                logo_path = str(default_logo)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=8 * mm, rightMargin=8 * mm,
            topMargin=5 * mm, bottomMargin=5 * mm
        )

        styles = getSampleStyleSheet()
        
        subtitle_style = ParagraphStyle(
            'SchoolSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )
        badge_style = ParagraphStyle(
            'ReceiptBadge',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=1
        )

        # Dynamic font sizing based on fee item count for guaranteed 1-page A4 fit
        item_count = len(receipt.items) if receipt.items else 1
        if item_count >= 12:
            font_sz = 7.0
            leading_sz = 8.2
            padding_sz = 0.8
            spacer_sz = 0.8 * mm
        elif item_count >= 8:
            font_sz = 7.5
            leading_sz = 9.0
            padding_sz = 1.0
            spacer_sz = 1.0 * mm
        else:
            font_sz = 8.0
            leading_sz = 10.0
            padding_sz = 1.5
            spacer_sz = 1.5 * mm

        label_bold = ParagraphStyle(
            'LabelBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=font_sz,
            leading=leading_sz,
            textColor=colors.HexColor("#1e293b")
        )
        label_val = ParagraphStyle(
            'LabelVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=font_sz,
            leading=leading_sz,
            textColor=colors.HexColor("#334155")
        )
        label_val_bold = ParagraphStyle(
            'LabelValBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=font_sz,
            leading=leading_sz,
            textColor=colors.HexColor("#0f172a")
        )
        table_hdr = ParagraphStyle(
            'TableHdr',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=font_sz,
            leading=leading_sz,
            textColor=colors.white
        )

        story = []

        # Header Block
        header_data = []
        if logo_path:
            try:
                img = Image(logo_path, width=15*mm, height=15*mm)
                header_data.append([img, Paragraph(f"<b><font size='11' color='#1e3a8a'>{school_name}</font></b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])
            except Exception:
                header_data.append([Paragraph(f"<b><font size='11' color='#1e3a8a'>{school_name}</font></b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])
        else:
            header_data.append([Paragraph(f"<b><font size='11' color='#1e3a8a'>{school_name}</font></b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])

        hdr_table = Table(header_data, colWidths=[194*mm] if not logo_path else [18*mm, 176*mm])
        hdr_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(hdr_table)
        story.append(Spacer(1, 0.5 * mm))

        story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor("#1e3a8a"), spaceBefore=0.5*mm, spaceAfter=0.5*mm))

        # Receipt Title Badge
        story.append(Paragraph("FEE PAYMENT RECEIPT", badge_style))
        story.append(Spacer(1, spacer_sz))

        # Student & Receipt Details Table
        student = receipt.student
        course_str = getattr(receipt, "course", None) or (getattr(student, "course", None) if student else None) or "General"
        branch_str = getattr(receipt, "branch", None) or (getattr(student, "branch", None) if student else None) or "General"
        year_str = getattr(receipt, "academic_year", None) or (getattr(student, "year", None) if student else None) or "N/A"
        sem_str = getattr(receipt, "semester", None) or (getattr(student, "semester", None) if student else None) or "N/A"
        st_name = getattr(student, "name", "N/A") if student else "N/A"
        adm_no = getattr(student, "admission_no", "N/A") if student else "N/A"
        father_name = getattr(student, "father_name", "N/A") if student else "N/A"
        mobile_num = getattr(student, "mobile", "N/A") if student else "N/A"

        student_info_data = [
            [
                Paragraph("<b>Receipt No:</b>", label_bold), Paragraph(receipt.receipt_no, label_val),
                Paragraph("<b>Date:</b>", label_bold), Paragraph(format_date(receipt.receipt_date), label_val)
            ],
            [
                Paragraph("<b>Admission / Enrollment No:</b>", label_bold), Paragraph(adm_no, label_val),
                Paragraph("<b>Academic Session:</b>", label_bold), Paragraph(receipt.academic_session, label_val)
            ],
            [
                Paragraph("<b>Student Name:</b>", label_bold), Paragraph(st_name, label_val),
                Paragraph("<b>Course / Branch:</b>", label_bold), Paragraph(f"{course_str} ({branch_str})", label_val)
            ],
            [
                Paragraph("<b>Year / Semester:</b>", label_bold), Paragraph(f"{year_str} / {sem_str}", label_val),
                Paragraph("<b>Father's Name:</b>", label_bold), Paragraph(father_name, label_val)
            ],
            [
                Paragraph("<b>Mobile No:</b>", label_bold), Paragraph(mobile_num, label_val),
                Paragraph("<b>Payment Mode:</b>", label_bold), Paragraph(receipt.payment_mode, label_val)
            ]
        ]

        info_table = Table(student_info_data, colWidths=[46*mm, 51*mm, 37*mm, 60*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 1.0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(info_table)
        story.append(Spacer(1, spacer_sz))

        # Fee Items Table with 'Rs.' Notation (Prevents ■ square box rendering)
        fee_table_data = [
            [Paragraph("S.No.", table_hdr), Paragraph("Fee Head / Particular Description", table_hdr), Paragraph("Amount Paid (Rs.)", table_hdr)]
        ]

        if receipt.items:
            for idx, item in enumerate(receipt.items, 1):
                fee_table_data.append([
                    Paragraph(str(idx), label_val),
                    Paragraph(f"<b>{item.category_name}</b>", label_val_bold),
                    Paragraph(f"<b>{item.amount:,.2f}</b>", label_val_bold)
                ])
        else:
            fee_table_data.append([
                Paragraph("1", label_val),
                Paragraph("<b>Fee Collection</b>", label_val_bold),
                Paragraph(f"<b>{receipt.total_amount:,.2f}</b>", label_val_bold)
            ])

        summary_rows_count = 0

        # Subtotal Row if discount or fine applied
        disc_amt = getattr(receipt, "discount_amount", 0.0) or 0.0
        fn_amt = getattr(receipt, "fine_amount", 0.0) or 0.0
        if disc_amt > 0 or fn_amt > 0:
            fee_table_data.append([
                "", Paragraph("Subtotal Calculated Fee", label_bold), Paragraph(f"Rs. {receipt.subtotal:,.2f}", label_val)
            ])
            summary_rows_count += 1

        # Optional Discount Row
        if disc_amt > 0:
            fee_table_data.append([
                "", Paragraph("<font color='#047857'><b>Discount (-)</b></font>", label_bold), Paragraph(f"<font color='#047857'><b>- Rs. {disc_amt:,.2f}</b></font>", label_bold)
            ])
            summary_rows_count += 1

        # Optional Fine Row
        if fn_amt > 0:
            fee_table_data.append([
                "", Paragraph("<font color='#b91c1c'><b>Fine / Penalty (+)</b></font>", label_bold), Paragraph(f"<font color='#b91c1c'><b>+ Rs. {fn_amt:,.2f}</b></font>", label_bold)
            ])
            summary_rows_count += 1

        # Total Paid Amount Row
        actual_paid = getattr(receipt, 'paid_amount', receipt.total_amount)
        if actual_paid is None:
            actual_paid = receipt.total_amount or 0.0
            
        fee_table_data.append([
            "", Paragraph("<b>Total Paid Amount</b>", label_bold), Paragraph(f"<b>Rs. {actual_paid:,.2f}</b>", label_bold)
        ])
        summary_rows_count += 1

        # Outstanding Due Row
        due_amt = getattr(receipt, 'due_amount', 0.0) or 0.0
        if due_amt > 0:
            fee_table_data.append([
                "", Paragraph("<font color='#dc2626'><b>Outstanding Due</b></font>", label_bold), Paragraph(f"<font color='#dc2626'><b>Rs. {due_amt:,.2f}</b></font>", label_bold)
            ])
        else:
            fee_table_data.append([
                "", Paragraph("<font color='#16a34a'><b>Outstanding Due</b></font>", label_bold), Paragraph("<font color='#16a34a'><b>Rs. 0.00 (PAID IN FULL)</b></font>", label_bold)
            ])
        summary_rows_count += 1

        fee_table = Table(fee_table_data, colWidths=[12*mm, 142*mm, 40*mm])
        fee_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('ALIGN', (2,0), (2,-1), 'RIGHT'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0, -summary_rows_count), (-1, -1), colors.HexColor("#eff6ff")),
            ('TOPPADDING', (0,0), (-1,-1), padding_sz),
            ('BOTTOMPADDING', (0,0), (-1,-1), padding_sz),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(fee_table)
        story.append(Spacer(1, spacer_sz))

        # Amount in Words Box
        words_box = [
            [Paragraph(f"<b>Amount Paid in Words:</b> {receipt.amount_in_words}", label_val)]
        ]
        words_table = Table(words_box, colWidths=[194*mm])
        words_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 1.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(words_table)
        story.append(Spacer(1, spacer_sz))

        # Payment Details Block (Dynamic Mode-Specific Fields)
        pay_details_lines = [f"<b>Payment Mode:</b> {receipt.payment_mode}"]
        pm_upper = receipt.payment_mode.upper()

        if "UPI" in pm_upper or "QR" in pm_upper:
            if receipt.utr_number:
                pay_details_lines.append(f"<b>UTR Number:</b> {receipt.utr_number}")
            if receipt.bank_name:
                pay_details_lines.append(f"<b>Bank Name:</b> {receipt.bank_name}")
            if receipt.payment_date:
                pay_details_lines.append(f"<b>Payment Date:</b> {format_date(receipt.payment_date)}")
        elif "CHEQUE" in pm_upper or "DD" in pm_upper or "DEMAND" in pm_upper:
            if receipt.cheque_number:
                pay_details_lines.append(f"<b>Cheque/DD No:</b> {receipt.cheque_number}")
            if receipt.cheque_date:
                pay_details_lines.append(f"<b>Cheque Date:</b> {format_date(receipt.cheque_date)}")
            if receipt.bank_name:
                pay_details_lines.append(f"<b>Bank Name:</b> {receipt.bank_name}")
        elif "NET" in pm_upper or "NEFT" in pm_upper or "ONLINE" in pm_upper or "CARD" in pm_upper:
            if receipt.utr_number or receipt.reference_no:
                pay_details_lines.append(f"<b>Txn/Ref No:</b> {receipt.utr_number or receipt.reference_no}")
            if receipt.bank_name:
                pay_details_lines.append(f"<b>Bank Name:</b> {receipt.bank_name}")
            if receipt.payment_date:
                pay_details_lines.append(f"<b>Payment Date:</b> {format_date(receipt.payment_date)}")
        else: # Cash or default
            if receipt.reference_no:
                pay_details_lines.append(f"<b>Reference:</b> {receipt.reference_no}")
            if receipt.payment_date:
                pay_details_lines.append(f"<b>Payment Date:</b> {format_date(receipt.payment_date)}")

        pay_details_str = " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(pay_details_lines)

        pay_details_box = [
            [Paragraph(f"<b>PAYMENT DETAILS:</b> {pay_details_str}", label_val)]
        ]
        pay_details_table = Table(pay_details_box, colWidths=[194*mm])
        pay_details_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
            ('TOPPADDING', (0,0), (-1,-1), 1.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(pay_details_table)
        story.append(Spacer(1, spacer_sz))

        # Remarks & Signatures
        sig_data = [
            [
                Paragraph(f"<b>Remarks:</b> {receipt.remarks or 'N/A'}", label_val),
                Paragraph("<b>Authorized Signatory / Cashier</b><br/><br/>______________________", label_val)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[124*mm, 70*mm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(sig_table)

        # Watermark Callback Function
        watermark_path = logo_path
        def draw_watermark(canvas, doc_obj):
            canvas.saveState()
            try:
                if watermark_path and Path(watermark_path).exists():
                    canvas.setFillAlpha(0.08)
                    w, h = 110 * mm, 110 * mm
                    x = (210 * mm - w) / 2
                    y = (297 * mm - h) / 2
                    canvas.drawImage(watermark_path, x, y, width=w, height=h, mask='auto', preserveAspectRatio=True)
                else:
                    canvas.setFont("Helvetica-Bold", 32)
                    canvas.setFillColor(colors.HexColor("#cbd5e1"))
                    canvas.setFillAlpha(0.08)
                    canvas.drawCentredString(105 * mm, 148.5 * mm, "DPS INTERNATIONAL")
            except Exception as e:
                logger.warning(f"Watermark draw error: {e}")
            canvas.restoreState()

        doc.build(story, onFirstPage=draw_watermark, onLaterPages=draw_watermark)
        logger.info(f"Generated PDF receipt with watermark: {output_path}")
        return output_path

    @staticmethod
    def generate_student_profile_pdf(student: Student, output_path: Optional[str] = None) -> str:
        """
        Generates a formal, printable single-page A4 Student Profile / Information Form PDF.
        """
        if not output_path:
            clean_adm = student.admission_no.replace('/', '_').replace(' ', '_')
            filename = f"Student_Profile_{clean_adm}.pdf"
            output_path = str(EXPORTS_DIR / filename)

        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

        school_info = SettingsController.get_school_info()
        school_name = school_info.school_name if school_info else "DPS International Public School"
        school_addr = school_info.address if school_info else "Plot 12, Sector 5, RK Puram, New Delhi - 110022"
        school_phone = school_info.phone if school_info else "+91 98765 43210, 011-26123456"
        school_email = school_info.email if school_info else "info@dpsschool.edu.in"

        # Determine Logo Path
        logo_path = school_info.logo_path if (school_info and school_info.logo_path and Path(school_info.logo_path).exists()) else None
        if not logo_path:
            default_logo = Path(__file__).resolve().parent.parent / "assets" / "school_logo.png"
            if default_logo.exists():
                logo_path = str(default_logo)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=12 * mm, rightMargin=12 * mm,
            topMargin=12 * mm, bottomMargin=12 * mm
        )

        styles = getSampleStyleSheet()

        subtitle_style = ParagraphStyle(
            'ProfileSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )
        title_badge = ParagraphStyle(
            'ProfileTitleBadge',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=1
        )
        sec_hdr_style = ParagraphStyle(
            'SecHdr',
            parent=styles['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#1e3a8a")
        )
        lbl_bold = ParagraphStyle(
            'LBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#1e293b")
        )
        lbl_val = ParagraphStyle(
            'LVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#334155")
        )

        story = []

        # School Header Block
        header_data = []
        if logo_path:
            try:
                img = Image(logo_path, width=22*mm, height=22*mm)
                header_data.append([img, Paragraph(f"<b><font size='13' color='#1e3a8a'>{school_name}</font></b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])
            except Exception:
                header_data.append([Paragraph(f"<b><font size='13' color='#1e3a8a'>{school_name}</font></b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])
        else:
            header_data.append([Paragraph(f"<b><font size='13' color='#1e3a8a'>{school_name}</font></b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])

        hdr_table = Table(header_data, colWidths=[186*mm] if not logo_path else [25*mm, 161*mm])
        hdr_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(hdr_table)
        story.append(Spacer(1, 2 * mm))
        story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#1e3a8a"), spaceAfter=2*mm))

        # Title Banner
        story.append(Paragraph("STUDENT INFORMATION FORM", title_badge))
        story.append(Spacer(1, 3 * mm))

        # Top Information Table with Student Photo on RIGHT
        photo_flowable = None
        if getattr(student, "photo_path", None):
            photo_file = STUDENT_PHOTOS_DIR / student.photo_path
            if not photo_file.exists():
                photo_file = Path(student.photo_path)
            if photo_file.exists():
                try:
                    photo_flowable = Image(str(photo_file), width=28*mm, height=36*mm)
                except Exception as e:
                    logger.warning(f"Error embedding student photo in PDF: {e}")

        if not photo_flowable:
            # Placeholder box text
            p_placeholder_data = [[Paragraph("<font color='#64748b' size='7'><b>STUDENT<br/>PHOTO<br/>(3:4 ID)</b></font>", subtitle_style)]]
            p_table = Table(p_placeholder_data, colWidths=[28*mm], rowHeights=[36*mm])
            p_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ]))
            photo_flowable = p_table

        # Student Key Information Grid
        dob_str = format_date(getattr(student, "date_of_birth", None)) if getattr(student, "date_of_birth", None) else "N/A"
        adm_date_str = format_date(student.admission_date) if student.admission_date else "N/A"
        status_color = "#166534" if student.status == "Active" else "#991b1b"

        info_grid_data = [
            [
                Paragraph("<b>Admission / Enrollment No:</b>", lbl_bold), Paragraph(f"<b>{student.admission_no}</b>", lbl_val),
                Paragraph("<b>Academic Session:</b>", lbl_bold), Paragraph(student.academic_session, lbl_val)
            ],
            [
                Paragraph("<b>Student Name:</b>", lbl_bold), Paragraph(f"<b>{student.name}</b>", lbl_val),
                Paragraph("<b>Date of Birth:</b>", lbl_bold), Paragraph(dob_str, lbl_val)
            ],
            [
                Paragraph("<b>Course / Program:</b>", lbl_bold), Paragraph(student.course or "General", lbl_val),
                Paragraph("<b>Branch / Dept:</b>", lbl_bold), Paragraph(student.branch or "General", lbl_val)
            ],
            [
                Paragraph("<b>Academic Year:</b>", lbl_bold), Paragraph(student.year or "N/A", lbl_val),
                Paragraph("<b>Semester:</b>", lbl_bold), Paragraph(student.semester or "N/A", lbl_val)
            ],
            [
                Paragraph("<b>Date of Admission:</b>", lbl_bold), Paragraph(adm_date_str, lbl_val),
                Paragraph("<b>Status:</b>", lbl_bold), Paragraph(f"<font color='{status_color}'><b>{student.status.upper()}</b></font>", lbl_val)
            ]
        ]

        grid_table = Table(info_grid_data, colWidths=[42*mm, 35*mm, 35*mm, 42*mm])
        grid_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ffffff")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))

        top_combined_data = [[grid_table, photo_flowable]]
        top_combined_table = Table(top_combined_data, colWidths=[155*mm, 31*mm])
        top_combined_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(top_combined_table)
        story.append(Spacer(1, 4 * mm))

        # Parent & Guardian Details Section
        story.append(Paragraph("<b>GUARDIAN & CONTACT DETAILS</b>", sec_hdr_style))
        story.append(Spacer(1, 1.5 * mm))

        guardian_data = [
            [
                Paragraph("<b>Father's Name:</b>", lbl_bold), Paragraph(student.father_name, lbl_val),
                Paragraph("<b>Mother's Name:</b>", lbl_bold), Paragraph(student.mother_name or "N/A", lbl_val)
            ],
            [
                Paragraph("<b>Mobile Number:</b>", lbl_bold), Paragraph(student.mobile, lbl_val),
                Paragraph("<b>Aadhaar Number:</b>", lbl_bold), Paragraph(getattr(student, "aadhaar_number", None) or "N/A", lbl_val)
            ],
            [
                Paragraph("<b>Residential Address:</b>", lbl_bold), Paragraph(student.address or "N/A", lbl_val),
                "", ""
            ]
        ]

        guardian_table = Table(guardian_data, colWidths=[38*mm, 55*mm, 38*mm, 55*mm])
        guardian_table.setStyle(TableStyle([
            ('SPAN', (1,2), (3,2)),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(guardian_table)
        story.append(Spacer(1, 4 * mm))

        # Fee Status & Payment History Summary Section
        story.append(Paragraph("<b>FEE & PAYMENT HISTORY SUMMARY</b>", sec_hdr_style))
        story.append(Spacer(1, 1.5 * mm))

        from config.database import get_db
        from models.receipt import Receipt
        db = get_db()
        tot_paid = 0.0
        tot_billed = 0.0
        curr_due = 0.0
        receipts = []
        try:
            receipts = db.query(Receipt).filter(Receipt.student_id == student.id).order_by(Receipt.id.desc()).all()
            for r in receipts:
                tot_paid += (r.paid_amount or 0.0)
                tot_billed += (r.total_amount or 0.0)
            if receipts:
                curr_due = receipts[0].due_amount or 0.0
        except Exception as ex:
            logger.warning(f"Error loading fee summary for profile PDF: {ex}")
        finally:
            db.close()

        due_text_color = "#b91c1c" if curr_due > 0 else "#166534"
        due_val_str = f"Rs. {curr_due:,.2f}" if curr_due > 0 else "Rs. 0.00 (PAID)"

        fee_summary_data = [
            [
                Paragraph("<b>TOTAL BILLED:</b>", lbl_bold), Paragraph(f"<b>Rs. {tot_billed:,.2f}</b>", lbl_val),
                Paragraph("<b>TOTAL PAID:</b>", lbl_bold), Paragraph(f"<b><font color='#166534'>Rs. {tot_paid:,.2f}</font></b>", lbl_val),
                Paragraph("<b>OUTSTANDING DUE:</b>", lbl_bold), Paragraph(f"<b><font color='{due_text_color}'>{due_val_str}</font></b>", lbl_val)
            ]
        ]
        fee_summary_table = Table(fee_summary_data, colWidths=[28*mm, 34*mm, 26*mm, 34*mm, 32*mm, 32*mm])
        fee_summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(fee_summary_table)
        story.append(Spacer(1, 2 * mm))

        if receipts:
            tbl_hdr_style = ParagraphStyle('TblHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.white)
            tbl_cell_style = ParagraphStyle('TblCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor("#1e293b"))
            
            rec_headers = ["Receipt No", "Date", "Session", "Payment Mode", "Amount Paid (Rs.)"]
            rec_table_data = [[Paragraph(f"<b>{h}</b>", tbl_hdr_style) for h in rec_headers]]
            for r in receipts[:3]:
                rec_table_data.append([
                    Paragraph(r.receipt_no, tbl_cell_style),
                    Paragraph(format_date(r.receipt_date), tbl_cell_style),
                    Paragraph(r.academic_session or "N/A", tbl_cell_style),
                    Paragraph(r.payment_mode or "Cash", tbl_cell_style),
                    Paragraph(f"Rs. {(r.paid_amount or 0.0):,.2f}", tbl_cell_style)
                ])

            rec_table = Table(rec_table_data, colWidths=[40*mm, 30*mm, 35*mm, 35*mm, 46*mm])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(rec_table)
        story.append(Spacer(1, 4 * mm))

        # Declaration & Signature Block
        dec_text = (
            "I hereby declare that all information provided in this student record is true, complete, and accurate "
            "to the best of my knowledge and belief. I agree to abide by all rules and regulations of the institution."
        )
        story.append(Paragraph(f"<i><font color='#475569' size='8'>{dec_text}</font></i>", lbl_val))
        story.append(Spacer(1, 10 * mm))

        sig_data = [
            [
                Paragraph("__________________________<br/><b>Student Signature</b>", lbl_val),
                Paragraph("__________________________<br/><b>Parent / Guardian Signature</b>", lbl_val),
                Paragraph("__________________________<br/><b>Principal / Authorized Signatory</b>", lbl_val)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[62*mm, 62*mm, 62*mm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ]))
        story.append(sig_table)

        # Watermark Callback
        watermark_path = logo_path
        def draw_watermark(canvas, doc_obj):
            canvas.saveState()
            try:
                if watermark_path and Path(watermark_path).exists():
                    canvas.setFillAlpha(0.08)
                    w, h = 110 * mm, 110 * mm
                    x = (210 * mm - w) / 2
                    y = (297 * mm - h) / 2
                    canvas.drawImage(watermark_path, x, y, width=w, height=h, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                logger.warning(f"Watermark draw error: {e}")
            canvas.restoreState()

        doc.build(story, onFirstPage=draw_watermark, onLaterPages=draw_watermark)
        logger.info(f"Generated student profile PDF: {output_path}")
        return output_path

    @staticmethod
    def generate_report_pdf(
        title: str,
        headers: List[str],
        rows: List[List[str]],
        total_info: Optional[Dict[str, str]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Generates tabular report PDF with clean 'Rs.' notation."""
        if not output_path:
            filename = f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = str(EXPORTS_DIR / filename)

        school_info = SettingsController.get_school_info()
        school_name = school_info.school_name if school_info else "DPS Modern School"

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=12 * mm, rightMargin=12 * mm,
            topMargin=12 * mm, bottomMargin=12 * mm
        )
        styles = getSampleStyleSheet()

        hdr_style = ParagraphStyle('HdrStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor("#1e3a8a"), alignment=1)
        sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#475569"), alignment=1)
        th_style = ParagraphStyle('THStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white)
        tb_style = ParagraphStyle('TBStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#1e293b"))

        story = [
            Paragraph(school_name, hdr_style),
            Paragraph(f"<b>{title}</b> | Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}", sub_style),
            Spacer(1, 3 * mm),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1e3a8a"), spaceAfter=3*mm)
        ]

        # Clean header text (replace '₹' with 'Rs.')
        clean_headers = [h.replace("₹", "Rs.") for h in headers]

        table_data = [[Paragraph(h, th_style) for h in clean_headers]]
        for row in rows:
            clean_row = [str(c).replace("₹", "Rs.") for c in row]
            table_data.append([Paragraph(c, tb_style) for c in clean_row])

        if total_info:
            tot_row = []
            for idx, h in enumerate(headers):
                if idx == 0:
                    tot_row.append(Paragraph("<b>TOTAL</b>", th_style))
                elif h in total_info:
                    tot_val = str(total_info[h]).replace("₹", "Rs.")
                    tot_row.append(Paragraph(f"<b>{tot_val}</b>", th_style))
                else:
                    tot_row.append(Paragraph("", th_style))
            table_data.append(tot_row)

        num_cols = len(headers)
        col_width = (186 / num_cols) * mm
        t = Table(table_data, colWidths=[col_width] * num_cols)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        if total_info:
            t.setStyle(TableStyle([('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#1e293b"))]))

        story.append(t)
        doc.build(story)
        logger.info(f"Generated report PDF: {output_path}")
        return output_path
