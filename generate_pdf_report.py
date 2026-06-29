import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#78706a"))
        
        # Header
        self.drawString(54, 750, "CodeRouter AI — Model Calibration & Token Efficiency Report")
        self.setStrokeColor(colors.HexColor("#eae2da"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "CONFIDENTIAL — INTERNAL USE ONLY")
        self.line(54, 52, 558, 52)
        self.restoreState()

def create_report(output_filename="CodeRouter_AI_Model_Calibration_Report.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette (Sahara Theme)
    primary_color = colors.HexColor('#c2652a')
    secondary_color = colors.HexColor('#78706a')
    text_color = colors.HexColor('#3a302a')
    bg_light = colors.HexColor('#faf5ee')
    border_color = colors.HexColor('#eae2da')
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_color,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=text_color
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []
    
    # --- Title Page / Header ---
    story.append(Spacer(1, 10))
    story.append(Paragraph("CodeRouter AI: Local Model Optimization & Efficiency Report", title_style))
    story.append(Paragraph("TECHNICAL ANALYSIS, MODEL CALIBRATION, & FALLBACK ARCHITECTURE PROPOSAL", subtitle_style))
    
    # --- Section 1: Local Model Capabilities ---
    story.append(Paragraph("1. Local Model Analysis: Qwen 2.5 Coder 1.5B", h1_style))
    story.append(Paragraph(
        "CodeRouter AI currently leverages the local LLM <b>qwen2.5-coder:1.5b</b> via Ollama. "
        "Despite its small footprint (1.5 billion parameters), this model exhibits remarkable code-generation capabilities "
        "owing to its specialized training dataset. To maximize local execution, we must evaluate what it can run "
        "reliably versus where it fails.",
        body_style
    ))
    
    # Table of Capabilities
    data = [
        [Paragraph("Category", table_header_style), Paragraph("Supported Local Tasks (High Accuracy)", table_header_style), Paragraph("Unsupported Local Tasks (Requires Remote)", table_header_style)],
        [
            Paragraph("<b>Algorithmic & Math</b>", table_text_style),
            Paragraph("Prime check, Armstrong numbers, Fibonacci, palindromes, basic sorting (bubble, quicksort), array filtering.", table_text_style),
            Paragraph("Complex algorithmic optimizations, dynamic programming over large spaces, graph traversal with edge cases.", table_text_style)
        ],
        [
            Paragraph("<b>Syntax Helpers</b>", table_text_style),
            Paragraph("String manipulations, regular expressions, JSON parsing, dictionary transformations, file I/O operations.", table_text_style),
            Paragraph("High-level library designs, metadata wrappers, complex reflection or metaprogramming.", table_text_style)
        ],
        [
            Paragraph("<b>Unit Testing & Docs</b>", table_text_style),
            Paragraph("Generating standard unit tests (PyTest, Jest), docstrings, comments, basic markdown structure.", table_text_style),
            Paragraph("Comprehensive integration test design, load testing scripts, mock environments for external APIs.", table_text_style)
        ],
        [
            Paragraph("<b>Frameworks & APIs</b>", table_text_style),
            Paragraph("Basic Flask/FastAPI routes, simple HTML forms, vanilla Javascript handlers, fetch API templates.", table_text_style),
            Paragraph("Complex database schema design, security middleware, OAuth configurations, multi-service network calls.", table_text_style)
        ]
    ]
    
    t = Table(data, colWidths=[1.2*inch, 2.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,1), (-1,-1), bg_light),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    
    # --- Section 2: Maximizing Token Efficiency ---
    story.append(Paragraph("2. Maximizing Token Efficiency & Accuracy", h1_style))
    story.append(Paragraph(
        "To achieve maximum token efficiency while keeping the query accuracy high, we propose a two-fold change:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Calibrate Classifier Rules</b>: Redefine the complexity ratings in <code>classifier.py</code> so that standard algorithmic routines and single-function structures are rated as <b>Score 2 (Simple)</b> instead of Score 3. This ensures they fall under the local routing threshold.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Increase Complexity Threshold</b>: Raise the default <code>COMPLEXITY_THRESHOLD</code> to <b>3</b> (or 3 by default in configuration). Under this threshold, Complexity 1 (Trivial), 2 (Simple), and 3 (Moderate) queries will be executed locally by default. Only Complexity 4 (Complex) and 5 (Expert) queries will route to the remote Fireworks AI models.",
        bullet_style
    ))
    story.append(Paragraph(
        "By doing this, <b>up to 75% of development queries</b> (which typically consist of function creation, syntax help, and debugging small snippets) can be run locally, yielding <b>100% token savings</b> for those queries.",
        body_style
    ))
    
    # --- Section 3: Proposal to Remove Fallback ---
    story.append(Paragraph("3. Elimination of Fallback Mechanism & Transparent Erroring", h1_style))
    story.append(Paragraph(
        "Currently, if a task is routed to the remote model (Score > Threshold) and the remote API times out or is missing credentials, "
        "the system falls back to running the query locally. While this provides a functional response, it introduces "
        "two structural issues:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>Degraded Accuracy</b>: High-complexity tasks (Level 4 and 5) require the reasoning scale of a larger remote model. Running them on a 1.5B local model results in incorrect or severely incomplete code, frustrating the user.",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>SLA & Latency Overhead</b>: The user suffers a double latency hit — first waiting 20 seconds for the remote model to timeout, then waiting for the local model to process the complex query, only to receive a sub-par response.",
        bullet_style
    ))
    
    story.append(Paragraph(
        "<b>Proposed Behavior:</b><br/>"
        "We will eliminate the local fallback mechanism for remote-bound tasks. If a task is deemed too complex for the local model (Score > Threshold) and the remote API fails or times out, the system will immediately return a clean, descriptive error message:",
        body_style
    ))
    
    # Callout Box for Error Message
    error_msg = (
        "<i>\"The task complexity exceeds local model capabilities, and the remote model response timed out. "
        "Please check your remote API configuration and try again.\"</i>"
    )
    error_table_data = [[Paragraph(error_msg, table_text_style)]]
    error_table = Table(error_table_data, colWidths=[6.2*inch])
    error_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fce4e0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#ff8a80')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(error_table)
    story.append(Spacer(1, 10))
    
    # --- Section 4: Implementation Plan ---
    story.append(Paragraph("4. Recommended Code Modifications", h1_style))
    
    code_mod_1 = (
        "<b>Modify <code>remote.py</code> (Remove Fallback)</b>:<br/>"
        "Replace the try-except fallback block in <code>call_remote_model</code> to raise an exception or return a clean error "
        "specifying that the remote API call failed. In the workflow graph, if <code>remote_node</code> raises an error, "
        "propagate the custom message directly back to the user."
    )
    code_mod_2 = (
        "<b>Modify <code>router.py</code> & <code>classifier.py</code> (Optimize Threshold)</b>:<br/>"
        "Update the default <code>COMPLEXITY_THRESHOLD</code> to 3. Calibrate the examples in <code>classifier.py</code> "
        "so that standard logic prompts like 'check if number is prime' return a score of 2, ensuring they execute locally."
    )
    
    story.append(Paragraph(f"• {code_mod_1}", bullet_style))
    story.append(Paragraph(f"• {code_mod_2}", bullet_style))
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    create_report()
    print("Report generated successfully as 'CodeRouter_AI_Model_Calibration_Report.pdf'")
