"""
ReportLab Commercial A4 PDF Fee Receipt & Financial Report Generation Service.
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

from config.app_config import EXPORTS_DIR
from models.receipt import Receipt
from controllers.settings_controller import SettingsController
from utils.helpers import format_date
from utils.logger import logger

class PDFService:
    @staticmethod
    def generate_receipt_pdf(receipt: Receipt, output_path: Optional[str] = None) -> str:
        """
        Generates a commercial A4 single-page Fee Receipt PDF.
        """
        if not output_path:
            filename = f"Receipt_{receipt.receipt_no.replace('/', '_')}.pdf"
            output_path = str(EXPORTS_DIR / filename)

        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

        school_info = SettingsController.get_school_info()
        school_name = school_info.school_name if school_info else "DPS International School"
        school_addr = school_info.address if school_info else "123 Education Street, New Delhi, India"
        school_phone = school_info.phone if school_info else "+91 11 2345 6789"
        school_email = school_info.email if school_info else "info@school.edu.in"
        receipt_footer = school_info.receipt_footer if school_info else "This is a computer generated receipt. Signature not required."
        logo_path = school_info.logo_path if (school_info and school_info.logo_path and Path(school_info.logo_path).exists()) else None

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=15 * mm, rightMargin=15 * mm,
            topMargin=15 * mm, bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()
        
        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            'SchoolTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            'SchoolSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
            alignment=1
        )
        badge_style = ParagraphStyle(
            'ReceiptBadge',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=1
        )
        label_bold = ParagraphStyle(
            'LabelBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1e293b")
        )
        label_val = ParagraphStyle(
            'LabelVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155")
        )
        table_hdr = ParagraphStyle(
            'TableHdr',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.white
        )

        story = []

        # Header Block
        header_data = []
        if logo_path:
            try:
                img = Image(logo_path, width=50*mm, height=20*mm)
                header_data.append([img, Paragraph(f"<b>{school_name}</b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])
            except Exception:
                header_data.append([Paragraph(f"<b>{school_name}</b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])
        else:
            header_data.append([Paragraph(f"<b>{school_name}</b><br/>{school_addr}<br/>Ph: {school_phone} | Email: {school_email}", subtitle_style)])

        hdr_table = Table(header_data, colWidths=[180*mm] if not logo_path else [30*mm, 150*mm])
        hdr_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(hdr_table)
        story.append(Spacer(1, 4 * mm))

        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=4*mm))

        # Receipt Title Badge
        story.append(Paragraph("FEE PAYMENT RECEIPT", badge_style))
        story.append(Spacer(1, 4 * mm))

        # Student & Receipt Details Table
        student = receipt.student
        student_info_data = [
            [
                Paragraph("<b>Receipt No:</b>", label_bold), Paragraph(receipt.receipt_no, label_val),
                Paragraph("<b>Date:</b>", label_bold), Paragraph(format_date(receipt.receipt_date), label_val)
            ],
            [
                Paragraph("<b>Admission No:</b>", label_bold), Paragraph(student.admission_no, label_val),
                Paragraph("<b>Academic Session:</b>", label_bold), Paragraph(receipt.academic_session, label_val)
            ],
            [
                Paragraph("<b>Student Name:</b>", label_bold), Paragraph(student.name, label_val),
                Paragraph("<b>Class / Sec:</b>", label_bold), Paragraph(f"{student.class_name} ({student.section or 'A'})", label_val)
            ],
            [
                Paragraph("<b>Father's Name:</b>", label_bold), Paragraph(student.father_name, label_val),
                Paragraph("<b>Mobile No:</b>", label_bold), Paragraph(student.mobile, label_val)
            ],
            [
                Paragraph("<b>Payment Mode:</b>", label_bold), Paragraph(receipt.payment_mode + (f" ({receipt.reference_no})" if receipt.reference_no else ""), label_val),
                Paragraph("<b>Status:</b>", label_bold), Paragraph(f"<b>{receipt.status}</b>", label_val)
            ]
        ]

        info_table = Table(student_info_data, colWidths=[30*mm, 60*mm, 35*mm, 55*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 5 * mm))

        # Fee Items Table with 'Rs.' Notation (Prevents ■ square box rendering)
        fee_table_data = [
            [Paragraph("S.No.", table_hdr), Paragraph("Fee Particulars / Head", table_hdr), Paragraph("Amount (Rs.)", table_hdr)]
        ]

        for idx, item in enumerate(receipt.items, 1):
            fee_table_data.append([
                Paragraph(str(idx), label_val),
                Paragraph(item.category_name, label_val),
                Paragraph(f"{item.amount:,.2f}", label_val)
            ])

        # Summary Rows
        fee_table_data.append([
            "", Paragraph("<b>Subtotal</b>", label_bold), Paragraph(f"<b>{receipt.subtotal:,.2f}</b>", label_bold)
        ])
        if receipt.discount_amount > 0:
            fee_table_data.append([
                "", Paragraph("Discount (-)", label_val), Paragraph(f"-{receipt.discount_amount:,.2f}", label_val)
            ])
        if receipt.fine_amount > 0:
            fee_table_data.append([
                "", Paragraph("Fine / Late Fee (+)", label_val), Paragraph(f"+{receipt.fine_amount:,.2f}", label_val)
            ])
        fee_table_data.append([
            "", Paragraph("<b>TOTAL PAID AMOUNT</b>", label_bold), Paragraph(f"<b>Rs. {receipt.total_amount:,.2f}</b>", label_bold)
        ])

        fee_table = Table(fee_table_data, colWidths=[15*mm, 125*mm, 40*mm])
        fee_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('ALIGN', (0,0), (0,-1), 'CENTER'),
            ('ALIGN', (2,0), (2,-1), 'RIGHT'),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#eff6ff")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(fee_table)
        story.append(Spacer(1, 5 * mm))

        # Amount in Words & Footer Signatures
        words_box = [
            [Paragraph(f"<b>Amount in Words:</b> {receipt.amount_in_words}", label_val)]
        ]
        words_table = Table(words_box, colWidths=[180*mm])
        words_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(words_table)
        story.append(Spacer(1, 10 * mm))

        # Remarks & Signatures
        sig_data = [
            [
                Paragraph(f"<b>Remarks:</b> {receipt.remarks or 'N/A'}", label_val),
                Paragraph("<b>Authorized Signatory / Cashier</b><br/><br/>______________________", label_val)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[110*mm, 70*mm])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ]))
        story.append(sig_table)
        story.append(Spacer(1, 8 * mm))

        # Footer Notice
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=3*mm))
        story.append(Paragraph(receipt_footer, subtitle_style))

        doc.build(story)
        logger.info(f"Generated PDF receipt: {output_path}")
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
            leftMargin=15 * mm, rightMargin=15 * mm,
            topMargin=15 * mm, bottomMargin=15 * mm
        )
        styles = getSampleStyleSheet()

        hdr_style = ParagraphStyle('HdrStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor("#1e3a8a"), alignment=1)
        sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.HexColor("#475569"), alignment=1)
        th_style = ParagraphStyle('THStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
        tb_style = ParagraphStyle('TBStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=colors.HexColor("#1e293b"))

        story = [
            Paragraph(school_name, hdr_style),
            Paragraph(f"<b>{title}</b> | Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}", sub_style),
            Spacer(1, 4 * mm),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1e3a8a"), spaceAfter=4*mm)
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
        col_width = (180 / num_cols) * mm
        t = Table(table_data, colWidths=[col_width] * num_cols)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        if total_info:
            t.setStyle(TableStyle([('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#1e293b"))]))

        story.append(t)
        doc.build(story)
        logger.info(f"Generated report PDF: {output_path}")
        return output_path
