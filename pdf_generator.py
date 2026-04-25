"""
pdf_generator.py — Generate a downloadable PDF report using reportlab.
"""
import io
from loguru import logger

def generate_pdf(plan, assessments) -> bytes:
    """Generate a professional PDF report from the learning plan.
    
    Returns bytes that can be used with st.download_button.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm, cm
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, HRFlowable
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        logger.error("reportlab not installed. Cannot generate PDF.")
        raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    # Colors
    C_STRONG = HexColor("#639922")
    C_DEVELOPING = HexColor("#EF9F27")
    C_GAP = HexColor("#E24B4A")
    C_ACCENT = HexColor("#7C6AF7")
    C_BG = HexColor("#0F172A")
    C_MUTED = HexColor("#64748B")

    def cat_color(cat):
        return {"STRONG": C_STRONG, "DEVELOPING": C_DEVELOPING, "GAP": C_GAP}.get(cat, C_MUTED)

    # Styles
    styles = getSampleStyleSheet()
    s_title = ParagraphStyle("Title2", parent=styles["Title"], fontSize=28, spaceAfter=4,
                             textColor=black, fontName="Helvetica-Bold")
    s_subtitle = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=12, spaceAfter=12,
                                textColor=C_MUTED, fontName="Helvetica")
    s_heading = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=16, spaceAfter=8,
                               spaceBefore=16, textColor=black, fontName="Helvetica-Bold")
    s_body = ParagraphStyle("Body2", parent=styles["Normal"], fontSize=10, spaceAfter=6,
                            leading=14, textColor=black)
    s_small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, textColor=C_MUTED,
                             leading=12)
    s_center = ParagraphStyle("Center", parent=styles["Normal"], fontSize=11, alignment=TA_CENTER,
                              textColor=C_MUTED, spaceAfter=8)

    elements = []

    # ═══ PAGE 1 — Header + Readiness ═══
    elements.append(Paragraph(plan.candidate_name, s_title))
    elements.append(Paragraph(f"{plan.target_role}  |  {plan.assessment_date}", s_subtitle))
    elements.append(Spacer(1, 6*mm))

    # Metrics row
    gaps = sum(1 for sp in plan.skill_plans if sp.category == "GAP")
    total_hrs = sum(r.estimated_hours for sp in plan.skill_plans for r in sp.resources)
    metrics = [
        ["Duration", "Skills", "Gaps", "Study Hours", "Readiness"],
        [f"{plan.total_duration_weeks} weeks", f"{len(plan.skill_plans)}", f"{gaps}",
         f"{total_hrs} hrs", f"{plan.readiness_score}%"]
    ]
    t = Table(metrics, colWidths=[90, 70, 60, 80, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F1F5F9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_MUTED),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 14),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 8*mm))

    # Summary
    elements.append(Paragraph("Executive Summary", s_heading))
    elements.append(Paragraph(plan.summary, s_body))
    elements.append(Spacer(1, 6*mm))

    # Priority order
    if plan.priority_order:
        elements.append(Paragraph(f"Priority: {' → '.join(plan.priority_order)}", s_small))

    # ═══ PAGE 2 — Skill Assessment Table ═══
    elements.append(PageBreak())
    elements.append(Paragraph("Skill Assessment Breakdown", s_heading))
    elements.append(Spacer(1, 4*mm))

    table_data = [["Skill", "Assessed", "Required", "Gap", "Category"]]
    row_colors = []
    for sp in plan.skill_plans:
        table_data.append([
            sp.skill_name,
            str(sp.assessed_level),
            str(sp.required_level),
            f"{sp.gap_score:+d}",
            sp.category
        ])
        row_colors.append(cat_color(sp.category))

    t2 = Table(table_data, colWidths=[120, 60, 60, 50, 80])
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F1F5F9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_MUTED),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
    ]
    for i, c in enumerate(row_colors):
        style_cmds.append(("TEXTCOLOR", (4, i + 1), (4, i + 1), c))
        style_cmds.append(("FONTNAME", (4, i + 1), (4, i + 1), "Helvetica-Bold"))
    t2.setStyle(TableStyle(style_cmds))
    elements.append(t2)

    # Adjacent leverage
    if plan.adjacent_leverages:
        elements.append(Spacer(1, 8*mm))
        elements.append(Paragraph("Skill Leverage Insights", s_heading))
        for lev in plan.adjacent_leverages:
            elements.append(Paragraph(
                f"<b>{lev.existing_skill} → {lev.unlocks_skill}</b>: {lev.message} "
                f"({lev.weeks_with_leverage}w with leverage vs {lev.weeks_without_leverage}w without)",
                s_body
            ))

    # ═══ PAGE 3+ — Per-skill deep dives ═══
    for sp in plan.skill_plans:
        if sp.category == "STRONG":
            continue

        elements.append(PageBreak())
        elements.append(Paragraph(f"{sp.skill_name}  —  {sp.category}", s_heading))
        elements.append(Paragraph(
            f"Level: {sp.assessed_level} → {sp.required_level}  |  {sp.estimated_weeks} weeks  |  Weeks {sp.start_week}–{sp.end_week}",
            s_small
        ))
        elements.append(Spacer(1, 4*mm))

        # Why this matters
        elements.append(Paragraph(f"<b>Why This Matters:</b> {sp.why_this_matters}", s_body))
        elements.append(Spacer(1, 4*mm))

        # Resources table
        if sp.resources:
            res_data = [["Resource", "Type", "Hours", "Why"]]
            for r in sp.resources:
                res_data.append([r.title, r.type.upper(), f"{r.estimated_hours}h", r.why_this_resource])
            t_res = Table(res_data, colWidths=[130, 50, 40, 160])
            t_res.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F1F5F9")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(t_res)
            elements.append(Spacer(1, 4*mm))

        # Weekly breakdown
        if sp.weekly_breakdown:
            elements.append(Paragraph("<b>Week-by-Week Plan</b>", s_body))
            for wb in sp.weekly_breakdown:
                elements.append(Paragraph(
                    f"<b>Week {wb.week} — {wb.focus}</b>", s_body
                ))
                elements.append(Paragraph(f"Goal: {wb.goal}", s_small))
                if wb.daily_tasks:
                    for task in wb.daily_tasks:
                        elements.append(Paragraph(f"    {task}", s_small))
                elements.append(Spacer(1, 2*mm))

        # Assessment reasoning
        if sp.assessment_reasoning:
            elements.append(Spacer(1, 4*mm))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0")))
            elements.append(Spacer(1, 2*mm))
            elements.append(Paragraph(f"<i>Assessment: {sp.assessment_reasoning}</i>", s_small))

    # ═══ LAST PAGE — Motivational Summary ═══
    elements.append(PageBreak())
    elements.append(Paragraph("Your Path Forward", s_heading))
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph(plan.summary, s_body))
    elements.append(Spacer(1, 8*mm))

    if plan.priority_order:
        elements.append(Paragraph(
            f"<b>Recommended Priority:</b> {' → '.join(plan.priority_order)}", s_body
        ))

    elements.append(Spacer(1, 12*mm))
    elements.append(Paragraph(
        f"Generated by NeuralHire — Autonomous Skill Assessment Engine",
        s_center
    ))

    # Build
    doc.build(elements)
    return buf.getvalue()
