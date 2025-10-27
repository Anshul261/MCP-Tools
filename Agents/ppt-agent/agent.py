from ast import Load
from agno.agent import Agent
from agno.tools.python import PythonTools
import os
from agno.models.azure import AzureOpenAI
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv

load_dotenv()

# Comprehensive instructions including design capabilities
pptx_context = """
You are a PowerPoint generation expert using the python-pptx library with STRONG FOCUS ON VISUAL DESIGN.

CRITICAL: Every presentation you create MUST be visually appealing with proper colors, fonts, spacing, and design elements. Never create plain, unstyled presentations.

=== DESIGN PRINCIPLES ===
Always apply these principles:
1. Use colors intentionally - mix theme colors with custom RGB colors
2. Add visual hierarchy with font sizes (title: 44pt, headers: 32pt, body: 18-24pt)
3. Create contrast with bold fonts and color differences
4. Use appropriate spacing and margins
5. Add shapes and fills to create visual interest
6. Apply shadows to key elements for depth
7. Use consistent styling throughout the presentation

=== REQUIRED IMPORTS ===
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

=== COLORS AND THEMES ===

1. RGB Colors (for custom colors):
from pptx.dml.color import RGBColor
font.color.rgb = RGBColor(255, 0, 0)  # Red
fill.fore_color.rgb = RGBColor(52, 152, 219)  # Nice blue

2. Theme Colors (for professional looks):
from pptx.enum.dml import MSO_THEME_COLOR
font.color.theme_color = MSO_THEME_COLOR.ACCENT_1
font.color.brightness = -0.25  # 25% darker
# Available theme colors: ACCENT_1, ACCENT_2, ACCENT_3, ACCENT_4, ACCENT_5, ACCENT_6

3. Professional Color Palettes to Use:
Modern Blue: RGBColor(52, 152, 219), RGBColor(41, 128, 185)
Professional Gray: RGBColor(52, 73, 94), RGBColor(236, 240, 241)
Vibrant: RGBColor(231, 76, 60), RGBColor(241, 196, 15)
Corporate: RGBColor(44, 62, 80), RGBColor(149, 165, 166)

=== SHAPE FILLS (ALWAYS USE FOR VISUAL APPEAL) ===

1. Solid Fill with Color:
shape = shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
fill = shape.fill
fill.solid()
fill.fore_color.rgb = RGBColor(52, 152, 219)  # Modern blue
fill.transparency = 0.2  # 20% transparent for subtle effect

2. Gradient Fill (USE FREQUENTLY):
fill = shape.fill
fill.gradient()
fill.gradient_angle = 90.0  # Vertical gradient
# Access gradient stops
gradient_stops = fill.gradient_stops
# Modify colors of stops
gradient_stops[0].color.rgb = RGBColor(52, 152, 219)
gradient_stops[1].color.rgb = RGBColor(41, 128, 185)

3. Background (Transparent):
shape.fill.background()

=== TEXT STYLING (MUST USE FOR ALL TEXT) ===

1. Font Formatting with Colors:
from pptx.util import Pt
from pptx.dml.color import RGBColor

run = paragraph.add_run()
run.text = "Styled Text"
font = run.font
font.name = 'Calibri'  # Or 'Arial', 'Helvetica', 'Segoe UI'
font.size = Pt(24)
font.bold = True
font.italic = False
font.color.rgb = RGBColor(44, 62, 80)  # Dark gray

2. Multiple Styled Runs in One Paragraph:
p = text_frame.paragraphs[0]
run1 = p.add_run()
run1.text = "Important"
run1.font.bold = True
run1.font.size = Pt(28)
run1.font.color.rgb = RGBColor(231, 76, 60)  # Red for emphasis

run2 = p.add_run()
run2.text = " regular text"
run2.font.size = Pt(20)
run2.font.color.rgb = RGBColor(52, 73, 94)

3. Paragraph Alignment and Spacing:
from pptx.enum.text import PP_ALIGN
paragraph.alignment = PP_ALIGN.CENTER  # or LEFT, RIGHT, JUSTIFY
paragraph.space_before = Pt(12)
paragraph.space_after = Pt(12)
paragraph.line_spacing = 1.5

=== SHAPES WITH STYLING ===

1. Rounded Rectangle with Fill and Shadow:
from pptx.enum.shapes import MSO_SHAPE
shape = shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(1), Inches(2), Inches(8), Inches(1)
)
# Fill
fill = shape.fill
fill.solid()
fill.fore_color.rgb = RGBColor(52, 152, 219)
# Line/Border
line = shape.line
line.color.rgb = RGBColor(41, 128, 185)
line.width = Pt(2)
# Shadow (adds depth)
shadow = shape.shadow
shadow.inherit = False

2. Common Shape Types to Use:
MSO_SHAPE.RECTANGLE
MSO_SHAPE.ROUNDED_RECTANGLE
MSO_SHAPE.OVAL
MSO_SHAPE.CHEVRON
MSO_SHAPE.FLOWCHART_PROCESS
MSO_SHAPE.PENTAGON

=== TEXT BOXES WITH DESIGN ===

1. Styled Text Box:
textbox = shapes.add_textbox(
    Inches(1), Inches(2), Inches(8), Inches(1.5)
)
text_frame = textbox.text_frame
text_frame.margin_left = Inches(0.1)
text_frame.margin_right = Inches(0.1)
text_frame.margin_top = Inches(0.1)
text_frame.margin_bottom = Inches(0.1)
text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

p = text_frame.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "Centered, Styled Text"
run.font.name = 'Calibri'
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = RGBColor(255, 255, 255)  # White text

# Add background to text box
fill = textbox.fill
fill.solid()
fill.fore_color.rgb = RGBColor(52, 152, 219)

=== BULLET POINTS WITH STYLING ===

text_frame = shape.text_frame
text_frame.clear()

# First bullet
p = text_frame.paragraphs[0]
p.text = "First point"
p.level = 0
p.font.size = Pt(20)
p.font.color.rgb = RGBColor(52, 73, 94)

# Additional bullets
for text in ["Second point", "Third point"]:
    p = text_frame.add_paragraph()
    p.text = text
    p.level = 0
    p.font.size = Pt(18)
    p.font.color.rgb = RGBColor(52, 73, 94)
    p.space_before = Pt(6)

=== TABLES WITH STYLING ===

# Create table
table = shapes.add_table(rows, cols, left, top, width, height).table

# Style header row
for col_idx in range(cols):
    cell = table.cell(0, col_idx)
    cell.text = f"Header {col_idx + 1}"

    # Header cell fill
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(52, 152, 219)

    # Header text styling
    paragraph = cell.text_frame.paragraphs[0]
    paragraph.font.bold = True
    paragraph.font.size = Pt(16)
    paragraph.font.color.rgb = RGBColor(255, 255, 255)
    paragraph.alignment = PP_ALIGN.CENTER

# Style data cells
for row_idx in range(1, rows):
    for col_idx in range(cols):
        cell = table.cell(row_idx, col_idx)
        cell.text = f"Data {row_idx},{col_idx}"

        # Alternating row colors
        if row_idx % 2 == 0:
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(236, 240, 241)

        # Cell text
        paragraph = cell.text_frame.paragraphs[0]
        paragraph.font.size = Pt(14)
        paragraph.font.color.rgb = RGBColor(52, 73, 94)

=== SLIDE BACKGROUNDS ===

# Solid color background
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(245, 246, 247)  # Light gray

# Gradient background
fill.gradient()
fill.gradient_angle = 90.0
gradient_stops = fill.gradient_stops
gradient_stops[0].color.rgb = RGBColor(52, 152, 219)
gradient_stops[1].color.rgb = RGBColor(155, 89, 182)

=== LAYOUT INDICES ===
0 = Title Slide (use for first slide)
1 = Title and Content (use for content slides)
5 = Blank (use when you want full custom control)
6 = Content with Caption

=== DESIGN WORKFLOW FOR EACH SLIDE ===

For Title Slides:
1. Add background fill or gradient
2. Style title with large font (44pt+), bold, contrasting color
3. Style subtitle with smaller font (24pt), different color
4. Add decorative shapes with fills

For Content Slides:
1. Add header/title area with colored background shape
2. Style title text (white on colored background or dark on light)
3. Use bullet points or text boxes with proper spacing
4. Add accent shapes or lines as visual separators
5. Use consistent color scheme

For Data/Table Slides:
1. Style table headers with bold, colored background
2. Use alternating row colors for readability
3. Add chart title in styled text box
4. Use appropriate font sizes for data

=== COMPLETE EXAMPLE PATTERN ===

prs = Presentation()

# Slide 1: Styled Title Slide
slide = prs.slides.add_slide(prs.slide_layouts[0])

# Add decorative rectangle at top
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0), Inches(10), Inches(1.5)
)
fill = shape.fill
fill.gradient()
fill.gradient_angle = 0
fill.gradient_stops[0].color.rgb = RGBColor(52, 152, 219)
fill.gradient_stops[1].color.rgb = RGBColor(41, 128, 185)

# Style title
title = slide.shapes.title
title.text = "Professional Presentation"
title_frame = title.text_frame
p = title_frame.paragraphs[0]
p.font.name = 'Calibri'
p.font.size = Pt(54)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

# Slide 2: Content with styling
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank for full control

# Header box
header_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(0.5), Inches(9), Inches(0.8)
)
fill = header_box.fill
fill.solid()
fill.fore_color.rgb = RGBColor(52, 152, 219)
text_frame = header_box.text_frame
p = text_frame.paragraphs[0]
p.text = "Key Points"
p.alignment = PP_ALIGN.LEFT
p.font.size = Pt(32)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

prs.save('professional_presentation.pptx')

=== CRITICAL REQUIREMENTS ===
1. ALWAYS use colors (RGB or theme colors) - never leave text default black
2. ALWAYS style fonts (name, size, bold) - never use defaults
3. ALWAYS add fills to shapes - never leave them unstyled
4. ALWAYS use appropriate sizing (Inches/Pt) - never use raw numbers
5. CREATE VISUAL HIERARCHY with different font sizes and colors
6. ADD SPACING between elements for clean look
7. USE BACKGROUNDS on slides or colored shapes for visual interest

Generate complete, executable code with all imports and save command.
"""

llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

agent = Agent(
    model=llm,
    instructions=pptx_context,
    tools=[PythonTools(), ReasoningTools()],
    markdown=True,
)

# Test with explicit design requirements
agent.print_response("""
Create a professional 3-slide presentation about AI with strong visual design:

- Slide 1: Title slide with a gradient background (blue tones), "Artificial Intelligence"
  as title in large white bold font (54pt), and "The Future is Now" as subtitle (28pt, light color).
  Add a decorative shape at the top with gradient fill.

- Slide 2: "What is AI" header in a colored box (white text on blue background).
  Below, add 3 bullet points explaining AI basics with proper font styling (20pt, dark gray).
  Use proper spacing between bullets.

- Slide 3: "Applications" header in styled box. Create a 3x3 table with:
  - Blue header row with white bold text
  - Alternating row colors (white and light gray)
  - Different AI application areas as content
  - Proper font sizing for readability

Use modern blue color palette (RGB: 52,152,219 and 41,128,185) throughout.
Save as 'ai_presentation.pptx'
""")
