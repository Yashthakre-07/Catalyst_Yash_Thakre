from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import random

def generate_plan_pdf(plan):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    
    # ── Master Palette (Neon Cyberpunk) ──
    C_BG = colors.HexColor("#020617")
    C_SURFACE = colors.HexColor("#0F172A")
    C_ACCENT = colors.HexColor("#7C6AF7")
    C_ACCENT_GLOW = colors.Color(124/255, 106/255, 247/255, alpha=0.1)
    C_EMERALD = colors.HexColor("#10B981")
    C_GOLD = colors.HexColor("#F59E0B")
    C_CRIMSON = colors.HexColor("#EF4444")
    C_TEXT = colors.HexColor("#F8FAFC")
    C_MUTED = colors.HexColor("#64748B")
    
    # ── Pro Typography ──
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=42,
        textColor=C_TEXT,
        alignment=0,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    tagline_style = ParagraphStyle(
        'TaglineStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=C_ACCENT,
        fontName='Helvetica-Bold',
        letterSpacing=2,
        textTransform='uppercase'
    )
    
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=C_ACCENT,
        spaceBefore=30,
        spaceAfter=15,
        fontName='Helvetica-Bold',
        letterSpacing=1.5
    )
    
    node_title = ParagraphStyle(
        'NodeTitle',
        parent=styles['Heading3'],
        fontSize=26,
        textColor=C_TEXT,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=C_TEXT,
        leading=16,
        fontName='Helvetica'
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=C_MUTED,
        leading=14,
        fontName='Helvetica'
    )

    # ── Background Logic ──
    def draw_master_frame(canvas, doc):
        canvas.saveState()
        # 1. Dark Base
        canvas.setFillColor(C_BG)
        canvas.rect(0, 0, A4[0], A4[1], fill=1)
        
        # 2. Left Border Accent
        canvas.setFillColor(C_ACCENT)
        canvas.rect(0, 0, 5, A4[1], fill=1)
        
        # 3. Decorative "Grid" (Subtle)
        canvas.setStrokeColor(colors.Color(1,1,1,alpha=0.03))
        canvas.setLineWidth(1)
        for i in range(0, int(A4[0]), 50):
            canvas.line(i, 0, i, A4[1])
        for i in range(0, int(A4[1]), 50):
            canvas.line(0, i, A4[0], i)
            
        # 4. Neural Nodes (First Page Only)
        if canvas.getPageNumber() == 1:
            canvas.setStrokeColor(C_ACCENT_GLOW)
            for _ in range(15):
                x1, y1 = random.randint(300, 500), random.randint(500, 800)
                x2, y2 = random.randint(300, 500), random.randint(500, 800)
                canvas.circle(x1, y1, 3, fill=1)
                canvas.line(x1, y1, x2, y2)
        
        canvas.restoreState()

    elements = []

    # ── Page 01: The Identity ──
    elements.append(Paragraph("AI SKILL ASSESSMENT // NODE REPORT", tagline_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(getattr(plan, 'candidate_name', 'UNKNOWN'), title_style))
    elements.append(Paragraph(f"TARGET ROLE: {getattr(plan, 'target_role', 'UNDEFINED')}", body_style))
    elements.append(Spacer(1, 40))

    # Master Metrics Box
    score = getattr(plan, 'readiness_score', 0)
    score_color = C_EMERALD if score > 70 else C_GOLD if score > 40 else C_CRIMSON
    
    m_data = [[
        Paragraph(f"<font color='#64748B' size='9'>SYSTEM READINESS</font><br/><font color='{score_color.hexval()}' size='36'><b>{score}%</b></font>", body_style),
        Paragraph(f"<font color='#64748B' size='9'>TOTAL NODES</font><br/><font color='#F8FAFC' size='36'><b>{len(plan.skills)}</b></font>", body_style),
        Paragraph(f"<font color='#64748B' size='9'>TIMELINE</font><br/><font color='#F8FAFC' size='36'><b>{getattr(plan, 'total_weeks', 0)}W</b></font>", body_style)
    ]]
    m_table = Table(m_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_SURFACE),
        ('BOX', (0,0), (-1,-1), 1, colors.Color(1,1,1,alpha=0.1)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
    ]))
    elements.append(m_table)
    elements.append(Spacer(1, 40))

    # Executive Summary
    elements.append(Paragraph("◈ NEURAL SYNTHESIS", section_title))
    s_data = [[Paragraph(getattr(plan, 'summary', ''), body_style)]]
    s_table = Table(s_data, colWidths=[doc.width - 20])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.Color(1,1,1,alpha=0.02)),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('LINESTART', (0,0), (0,0), 3, C_ACCENT),
    ]))
    elements.append(s_table)
    
    # Skill Analysis Table
    elements.append(Paragraph("◈ NODE ASSESSMENT GRID", section_title))
    grid_data = [[
        Paragraph("<b>COGNITIVE NODE</b>", meta_style), 
        Paragraph("<b>CURRENT</b>", meta_style), 
        Paragraph("<b>TARGET</b>", meta_style), 
        Paragraph("<b>STATUS</b>", meta_style)
    ]]
    for s in plan.skills:
        sc = C_EMERALD if s.category == "STRONG" else C_GOLD if s.category == "DEVELOPING" else C_CRIMSON
        grid_data.append([
            Paragraph(s.skill_name, body_style),
            Paragraph(str(s.current_level), body_style),
            Paragraph(str(s.target_level), body_style),
            Paragraph(f"<font color='{sc.hexval()}'><b>{s.category}</b></font>", body_style)
        ])
    
    grid_table = Table(grid_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch])
    grid_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, C_ACCENT),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.Color(1,1,1,alpha=0.05)),
    ]))
    elements.append(grid_table)
    elements.append(PageBreak())

    # ── Page 02 onwards: The Roadmap ──
    for s in plan.skills:
        if s.category == "STRONG": continue
        
        elements.append(Paragraph(f"DEEP DIVE: {s.skill_name}", section_title))
        
        for topic in s.topics:
            elements.append(Spacer(1, 10))
            # Week Header
            w_data = [[
                Paragraph(f"<font color='#7C6AF7'><b>WEEK {topic.week_label if hasattr(topic, 'week_label') else '0'}</b></font>", body_style),
                Paragraph(f"<b>{topic.title}</b>", body_style)
            ]]
            w_table = Table(w_data, colWidths=[1*inch, doc.width - 1*inch])
            w_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (0,0), colors.Color(1,1,1,alpha=0.05)),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(w_table)
            
            # Details
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>OBJECTIVE:</b> {topic.objective}", body_style))
            
            # Resource Box (Visual Intelligence)
            yt = topic.youtube
            yt_data = [
                [Paragraph("<b>VISUAL INTEL (EASY)</b>", meta_style), Paragraph("<b>VISUAL INTEL (HARD)</b>", meta_style)],
                [Paragraph(yt.easy.title, body_style), Paragraph(yt.hard.title, body_style)],
                [Paragraph(f"<font color='#7C6AF7'>{yt.easy.url}</font>", meta_style), Paragraph(f"<font color='#7C6AF7'>{yt.hard.url}</font>", meta_style)]
            ]
            yt_table = Table(yt_data, colWidths=[2.8*inch, 2.8*inch])
            yt_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.Color(1,1,1,alpha=0.02)),
                ('BOX', (0,0), (-1,-1), 1, colors.Color(1,1,1,alpha=0.1)),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
            ]))
            elements.append(Spacer(1, 10))
            elements.append(yt_table)
            
            # Milestone
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>TACTICAL EXECUTION:</b> {topic.hands_on}", body_style))
            elements.append(Paragraph(f"<b>MILESTONE:</b> <font color='#10B981'>{topic.milestone}</font>", body_style))
            elements.append(Spacer(1, 20))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.Color(1,1,1,alpha=0.1)))

    # Build PDF
    doc.build(elements, onFirstPage=draw_master_frame, onLaterPages=draw_master_frame)
    buffer.seek(0)
    return buffer
