"""
PPT Agent Team with PptxGenJS Backend

Uses PptxGenJS JavaScript library for superior presentation quality.
The agent generates JavaScript code that's executed via Node.js.

This provides:
- Much higher quality output than python-pptx
- More professional design capabilities
- Better animation and transition support
- Cleaner, more modern presentations
"""

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.python import PythonTools
from agno.models.azure import AzureOpenAI
from agno.team import Team
import os
import subprocess
import json

from dotenv import load_dotenv

load_dotenv()

llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# ============================================================================
# RESEARCH AGENT
# ============================================================================

research_instructions = """
You are a Research Specialist Agent for PowerPoint presentations.

TASK: Perform comprehensive research on a given topic using DuckDuckGo.

SEARCH STRATEGY:
- Perform 8-10+ searches covering different angles
- Search for: overview, statistics, trends, examples, expert insights, challenges, future outlook
- Focus on recent data (2023-2024)
- Gather specific numbers, percentages, and real-world examples

OUTPUT:
Provide findings organized as JSON with:
- overview: 2-3 sentence summary
- key_statistics: Top 3-5 statistics
- key_points: Main insights (5-7 points)
- recent_developments: Recent developments (3-4 items)
- real_world_examples: Case studies and examples (3-4 items)
- expert_insights: Expert perspectives (2-3 items)
- challenges: Key challenges (2-3 items)
- future_outlook: Future predictions (1-2 sentences)

Be thorough, specific, and focus on presentation-worthy content.
"""

research_agent = Agent(
    name="ResearchAgent",
    role="Deep Research Specialist",
    model=llm,
    instructions=research_instructions,
    tools=[DuckDuckGoTools(fixed_max_results=10)],
    markdown=True,
)

# ============================================================================
# CONTENT SYNTHESIZER
# ============================================================================

synthesis_instructions = """
You are a Content Synthesis Specialist for high-quality presentations.

TASK: Transform research findings into structured presentation content.

CONTENT RULES:
- Create 5-7 compelling slides
- Each slide: title (6-8 words), 3-5 bullet points (max 15 words each)
- Include specific statistics and real-world examples
- Ensure logical flow and narrative progression
- Add speaker notes for presenter context

SLIDE STRUCTURE:
1. Title Slide: Topic + hook
2. Overview: Problem/opportunity + key statistic
3-4. Key Points: Main insights with data
5-6. Applications: Real-world examples
7. Conclusion: Key insight + takeaway

OUTPUT FORMAT:
```json
{
    "title": "Presentation Title",
    "slides": [
        {
            "slide_number": 1,
            "title": "Slide Title",
            "type": "title",
            "bullets": ["bullet1", "bullet2"],
            "statistic": "specific data or example",
            "speaker_notes": "presenter context",
            "design_hint": "visual suggestion"
        }
    ]
}
```

CRITICAL FOR JAVASCRIPT GENERATION:
When creating bullet points and content:
- Avoid double quotes inside text: use "text" not "text with "quotes""
- Use simple, clear language without excessive punctuation
- Replace quotes with apostrophes where possible: "don't" instead of "do not"
- Keep bullet points concise (max 15 words)
- Avoid special characters that need escaping

Example bullet points (good for JavaScript):
"AI improves diagnostic accuracy by 40 percent"
"Machine learning models analyze imaging 3x faster"
"Personalized treatment reduces hospital readmission by 15 percent"

Focus on clarity, impact, and content quality.
"""

content_agent = Agent(
    name="ContentSynthesizer",
    role="Content Creation Specialist",
    model=llm,
    instructions=synthesis_instructions,
    markdown=True,
)

# ============================================================================
# PRESENTATION DESIGNER - PPTXGENJS VERSION
# ============================================================================

design_instructions = """
You are a Professional Presentation Designer using PptxGenJS JavaScript library.

PptxGenJS provides superior presentation quality with:
- Beautiful typography and layouts
- Professional color management
- Smooth animations and transitions
- High-quality rendering
- Modern design patterns

YOUR TASK:
1. Read the slide content provided
2. Generate complete JavaScript code using PptxGenJS
3. The code will be executed by Python to create the PPTX file

PPTXGENJS BASICS:

Installation (already done):
npm install pptxgenjs

Import:
const PptxGenJS = require("pptxgenjs");
let pres = new PptxGenJS();

DESIGN APPROACH:

Color Palette (Choose ONE - use consistently):
const colors = {
    primary: "1F4E79",      // Deep blue
    secondary: "4472C4",    // Light blue
    accent: "F3A612",       // Gold
    dark: "2C3E50",         // Dark gray
    light: "ECF0F1",        // Light gray
    white: "FFFFFF",
    text: "333333"
};

Typography Hierarchy:
- Title Slides: Bold, 54pt, white on gradient
- Headers: Bold, 40pt, white on colored background
- Body: Regular, 18-20pt, dark text
- Fonts: "Calibri", "Arial", "Helvetica"

SLIDE TEMPLATES:

Title Slide:
let slide = pres.addSlide();
slide.background = { color: colors.primary };
let gradient = { type: "solid", color: colors.secondary, transparency: 30 };
slide.background = { fill: "1F4E79" };

// Add gradient effect
slide.addShape(pres.ShapeType.rect, {
    x: 0, y: 0, w: "100%", h: "50%",
    fill: { color: "1F4E79" },
    line: { type: "none" }
});

slide.addText("Presentation Title", {
    x: 0.5, y: 2, w: 9, h: 1,
    fontSize: 54, bold: true, color: "FFFFFF",
    align: "center", fontFace: "Calibri"
});

slide.addText("Subtitle Here", {
    x: 0.5, y: 3.2, w: 9, h: 0.6,
    fontSize: 32, color: "F3A612",
    align: "center", fontFace: "Calibri"
});

Content Slide with Header:
let slide = pres.addSlide();

// Header bar
slide.addShape(pres.ShapeType.rect, {
    x: 0, y: 0, w: "100%", h: 1,
    fill: { color: "1F4E79" },
    line: { type: "none" }
});

// Header text
slide.addText("Slide Title", {
    x: 0.4, y: 0.25, w: 8.6, h: 0.6,
    fontSize: 40, bold: true, color: "FFFFFF",
    align: "left", fontFace: "Calibri"
});

// Body content
slide.addText("Bullet point content", {
    x: 0.5, y: 1.3, w: 9, h: 4,
    fontSize: 18, color: "333333",
    align: "left", fontFace: "Calibri"
});

Table:
let tableData = [
    [{ text: "Header 1" }, { text: "Header 2" }],
    [{ text: "Data 1" }, { text: "Data 2" }]
];

slide.addTable(tableData, {
    x: 0.5, y: 1.5, w: 9, h: 3,
    colW: [4.5, 4.5],
    border: { pt: 1, color: "CCCCCC" },
    fill: { color: "ECF0F1" },
    fontSize: 14,
    rowH: [0.5, 0.4]
});

Chart (Bar Chart):
slide.addChart(pres.ChartType.bar, [
    {
        name: "Series 1",
        labels: ["Q1", "Q2", "Q3", "Q4"],
        data: [10, 20, 30, 40]
    }
], {
    x: 0.5, y: 1.5, w: 9, h: 3.5,
    chartColors: ["1F4E79", "4472C4"]
});

Image:
slide.addImage({
    path: "image.jpg",
    x: 0.5, y: 1.5, w: 9, h: 4
});

FULL CODE STRUCTURE:

```javascript
const PptxGenJS = require("pptxgenjs");
let pres = new PptxGenJS();

// Set presentation properties
pres.defineLayout({ name: "BLANK", master: true });
pres.defineLayout({ name: "TITLE", master: true });

// Define master slide with design
let layoutMaster = pres.defineLayout({ name: "MASTER", master: true });
layoutMaster.background = { color: "FFFFFF" };

// Color palette
const colors = {
    primary: "1F4E79",
    secondary: "4472C4",
    accent: "F3A612",
    text: "333333"
};

// Slide 1: Title
let slide1 = pres.addSlide();
slide1.background = { color: colors.primary };
slide1.addText("Title", { x: 0.5, y: 2, fontSize: 54, bold: true, color: "FFFFFF" });

// Slide 2: Content
let slide2 = pres.addSlide();
slide2.background = { color: "FFFFFF" };
// Add header, content, etc.

// Save
pres.writeFile({ fileName: "presentation.pptx" });
```

QUALITY GUIDELINES:
- Use consistent spacing (0.5 inch margins)
- Professional typography hierarchy
- Color palette applied consistently
- Clear visual separation between sections
- Proper alignment and whitespace
- Charts with clear labels
- Professional imagery
- Readable font sizes

CRITICAL - YOU MUST EXECUTE THE JAVASCRIPT CODE:
1. Generate COMPLETE JavaScript code using PptxGenJS
2. Write the code to a file (create_pptx.js)
3. Execute it using Node.js via Python subprocess
4. The PPTX file will be created

EXECUTION TEMPLATE (Use PythonTools to run this):
```python
import subprocess

js_code = '''
const PptxGenJS = require("pptxgenjs");
let pres = new PptxGenJS();
const colors = { primary: "1F4E79", secondary: "4472C4", accent: "F3A612" };
let slide = pres.addSlide();
slide.background = { color: "FFFFFF" };
slide.addText("Hello World", { x: 0.5, y: 0.5, w: 9, h: 1, fontSize: 44, bold: true, color: colors.primary });
pres.writeFile({ fileName: "output.pptx" });
'''

with open('create_pptx.js', 'w') as f:
    f.write(js_code)

result = subprocess.run(['node', 'create_pptx.js'], capture_output=True, text=True)
print("Success!" if result.returncode == 0 else f"Error: {result.stderr}")
```

EXAMPLE COMPLETE JavaScript CODE STRUCTURE:
const PptxGenJS = require("pptxgenjs");
let pres = new PptxGenJS();
const colors = { primary: "1F4E79", secondary: "4472C4", accent: "F3A612" };

// All 7 slides here...
let slide1 = pres.addSlide();
// ... content for each slide ...

pres.writeFile({ fileName: "healthcare_ai.pptx" });

MOST IMPORTANT: After generating the JavaScript code, you MUST use your PythonTools
to write it to a file and execute it with Node.js. This is what creates the actual PPTX file.
Do not just show code - EXECUTE IT!

STRING ESCAPING REQUIREMENTS - CRITICAL:
The generated JavaScript code MUST have properly escaped strings to avoid syntax errors.

When adding text content, ALWAYS escape quotes:
CORRECT:
  slide.addText("First point", { ... });
  slide.addText("Use single quotes for text", { ... });
  slide.addText("Escape double quotes like this: \\"text\\"", { ... });
  slide.addText("AI enhances diagnostics, personalization, and operational efficiency.", { ... });

WRONG (These cause Node.js syntax errors):
  slide.addText("text with "unescaped" quotes", { ... });  // WRONG - will fail
  slide.addText('text with 'apostrophes' here', { ... });  // WRONG - will fail

For multi-line content with special characters:
Use template literals with backticks and escape internal quotes:
```javascript
const bullets = "- First point\n- Second point with \\"special\\" chars\n- Third point";
slide.addText(bullets, { ... });
```

Or use array format with proper escaping:
```javascript
const content = [
  { text: "Bullet 1", options: { fontSize: 18 } },
  { text: "Bullet 2 with \\"quotes\\"", options: { fontSize: 18 } }
];
slide.addText(content, { ... });
```

ALWAYS check that:
1. All double quotes inside strings are escaped with backslash: \\"
2. All single quotes are either at string boundaries or escaped
3. Newlines use \\n not actual line breaks
4. Special characters like apostrophes are handled correctly
"""

designer_agent = Agent(
    name="PresentationDesigner",
    role="Visual Design Specialist using PptxGenJS",
    model=llm,
    instructions=design_instructions,
    tools=[PythonTools()],
    markdown=True,
)

# ============================================================================
# TEAM
# ============================================================================

ppt_team = Team(
    name="PPT Agent Team with PptxGenJS",
    description="Multi-agent system creating presentations with superior quality using PptxGenJS",
    model=llm,
    members=[research_agent, content_agent, designer_agent],
    markdown=True,
    instructions="""
    Team Workflow:
    1. ResearchAgent: Deep research using DuckDuckGo (8-10+ searches)
    2. ContentSynthesizer: Create structured slide content
    3. PresentationDesigner: Generate JavaScript code with PptxGenJS and execute it

    The designer agent will create a Node.js script that uses PptxGenJS to generate
    a high-quality PowerPoint presentation. The Python agent will execute this via subprocess.

    Final output: A professional PPTX file created by PptxGenJS.
    """,
)


def create_presentation_pptxgenjs(
    topic: str, output_filename: str, num_slides: int = 7
):
    """
    Create a presentation using PptxGenJS for superior quality

    Args:
        topic: Presentation topic
        output_filename: Output PPTX filename
        num_slides: Number of slides (default 7)
    """

    print("\n" + "=" * 80)
    print(f"Creating Presentation with PptxGenJS: {topic}")
    print(f"Output: {output_filename}")
    print(f"Slides: {num_slides}")
    print("=" * 80 + "\n")

    prompt = f"""
    Create a professional PowerPoint presentation on: {topic}

    Workflow:
    1. Research Agent: Conduct comprehensive research using at least 10 DuckDuckGo searches
       covering overview, statistics, recent developments, examples, expert insights, and challenges.
       Return findings as structured JSON.

    2. Content Synthesizer: Based on research, create {num_slides} slides with:
       - Compelling titles and bullet points
       - Specific statistics and real-world examples (2023-2024)
       - Speaker notes and design hints
       Return as JSON with slide structure.

    3. Presentation Designer: Using PptxGenJS, generate JavaScript code that:
       - Creates a professional presentation file
       - Uses consistent color palette (Primary: 1F4E79, Secondary: 4472C4, Accent: F3A612)
       - Applies professional typography hierarchy
       - Includes all slide content with proper styling
       - Saves as '{output_filename}'

    Generate COMPLETE JavaScript code and execute it to create the PPTX file.
    Focus on professional quality and visual excellence.
    """

    try:
        response = ppt_team.print_response(prompt, markdown=True, stream=True)

        print("\n" + "=" * 80)
        print("Presentation creation workflow completed!")
        print(f"Check for: {output_filename}")
        print("=" * 80 + "\n")

        return response
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    create_presentation_pptxgenjs(
        topic="Artificial Intelligence in Healthcare",
        output_filename="healthcare_ai.pptx",
        num_slides=7,
    )
