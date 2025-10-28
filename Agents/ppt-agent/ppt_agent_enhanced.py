"""
Enhanced PPT Agent with PptxGenJS, Themes, and Animation Support

Features:
- PptxGenJS backend for superior design quality
- 8+ professional themes with customizable colors
- Animation and transition support
- ShellTools integration for direct Node.js execution
- Multi-agent team coordination
"""

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.python import PythonTools
from agno.tools.shell import ShellTools
from agno.models.azure import AzureOpenAI
from agno.team import Team
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Shared LLM configuration
llm = AzureOpenAI(
    id=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# Load theme and animation configurations
def load_themes():
    """Load theme definitions from config"""
    config_path = Path(__file__).parent / "config" / "themes.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f).get("themes", {})
    return {}

def load_animations():
    """Load animation definitions from config"""
    config_path = Path(__file__).parent / "config" / "animations.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

THEMES = load_themes()
ANIMATIONS = load_animations()

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
- Include design hints for visual consistency

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
    "recommended_theme": "corporate_blue",
    "animation_preset": "professional",
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

THEME RECOMMENDATION:
Based on the topic, recommend one of these themes:
- corporate_blue: Business, Finance, Corporate
- tech_modern: Technology, Startups, Innovation
- healthcare: Medical, Healthcare, Pharmaceutical
- academic: University, Research, Educational
- creative: Design, Marketing, Creative agencies
- financial: Finance, Banking, Investment
- premium_dark: Executive, Premium, Luxury brands
- modern_minimalist: Creative, Design, Art

CRITICAL FOR JAVASCRIPT GENERATION:
When creating bullet points and content:
- Avoid double quotes inside text: use "text" not "text with "quotes""
- Use simple, clear language without excessive punctuation
- Replace quotes with apostrophes where possible
- Keep bullet points concise (max 15 words)
- Avoid special characters that need escaping

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
# PRESENTATION DESIGNER - ENHANCED WITH THEMES AND ANIMATIONS
# ============================================================================

design_instructions = f"""
You are a Professional Presentation Designer using PptxGenJS JavaScript library.

PptxGenJS provides superior presentation quality with:
- Beautiful typography and layouts
- Professional color management
- Smooth animations and transitions
- High-quality rendering
- Modern design patterns

AVAILABLE THEMES:
{json.dumps(THEMES, indent=2)}

AVAILABLE ANIMATION PRESETS:
{json.dumps(ANIMATIONS.get('presets', {}), indent=2)}

YOUR TASK:
1. Receive slide content and recommended theme/animations
2. Apply the theme colors and typography
3. Generate complete JavaScript code using PptxGenJS
4. Execute the code via ShellTools to create the PPTX file

PPTXGENJS IMPLEMENTATION:

Color Palette Usage:
- Apply theme colors consistently throughout
- Use primary color for headers and emphasis
- Use secondary for supporting elements
- Use accent for highlights and call-to-action
- Use text color for all body text

Typography Hierarchy:
- Title Slides: Bold, 54pt, white/light on colored background
- Headers: Bold, 40pt, white on primary color bar
- Body: Regular, 18-20pt, using text color
- Font: Use theme's font_family from configuration

Animation Integration:
```javascript
// Add animations to text/shapes
slide.addText("Content", {{
    x: 0.5, y: 1.5, w: 9, h: 1,
    fontSize: 18, color: colors.text,
    animate: {{
        type: "fade",  // entrance animation
        duration: 0.5
    }}
}});

// Slide transitions
slide.transition = {{
    type: "fade",
    duration: 0.5
}};
```

EXECUTION WITH SHELLTOOLS:
After generating JavaScript code:
1. Write code to file using PythonTools
2. Execute with ShellTools: run_shell_command("node create_pptx.js")
3. Verify PPTX file was created

FALLBACK EXECUTION:
If ShellTools fails, use PythonTools with subprocess:
```python
import subprocess
with open('create_pptx.js', 'w') as f:
    f.write(js_code)
result = subprocess.run(['node', 'create_pptx.js'], capture_output=True, text=True)
```

QUALITY REQUIREMENTS:
- One consistent theme throughout
- Professional spacing and alignment
- Clear visual hierarchy
- Proper use of whitespace
- Readable font sizes
- Color accessible for colorblind viewers
- All content properly styled
"""

designer_agent = Agent(
    name="PresentationDesigner",
    role="Visual Design Specialist using PptxGenJS",
    model=llm,
    instructions=design_instructions,
    tools=[PythonTools(), ShellTools()],
    markdown=True,
)

# ============================================================================
# ENHANCED PPT AGENT TEAM
# ============================================================================

ppt_agent_team = Team(
    name="Enhanced PPT Agent Team",
    description="Multi-agent system for creating research-backed, high-quality animated presentations with professional themes",
    model=llm,
    members=[research_agent, content_agent, designer_agent],
    markdown=True,
    instructions="""
Team Workflow:
1. ResearchAgent: Conducts deep web research (8-10+ searches)
2. ContentSynthesizer: Creates structured slide content with theme recommendation
3. PresentationDesigner: Generates PptxGenJS code with theme and animations, executes via ShellTools

The designer agent will execute the Node.js script using ShellTools to generate
a high-quality PPTX file with professional styling, colors, and animations.

Final output: A professional, animated PPTX file created by PptxGenJS.
""",
)


def create_presentation(
    topic: str,
    output_filename: str,
    theme: str = "corporate_blue",
    animation_preset: str = "professional",
    num_slides: int = 7
):
    """
    Create a professional, animated presentation with theme support

    Args:
        topic: Presentation topic
        output_filename: Output PPTX filename
        theme: Theme name (see THEMES above)
        animation_preset: Animation preset (subtle, dynamic, professional, creative)
        num_slides: Number of slides (default 7)
    """

    print("\n" + "=" * 80)
    print(f"Creating Enhanced Presentation: {topic}")
    print(f"Output: {output_filename}")
    print(f"Theme: {theme}")
    print(f"Animations: {animation_preset}")
    print(f"Slides: {num_slides}")
    print("=" * 80 + "\n")

    prompt = f"""
Create a professional PowerPoint presentation on: {topic}

SPECIFICATIONS:
- Theme: {theme}
- Animation Preset: {animation_preset}
- Slide Count: {num_slides}
- Output File: {output_filename}

WORKFLOW:

1. Research Agent:
   - Conduct comprehensive research using at least 10 DuckDuckGo searches
   - Cover: overview, statistics, trends, examples, expert insights, challenges
   - Focus on 2023-2024 data

2. Content Synthesizer:
   - Transform research into {num_slides} compelling slides
   - RECOMMEND THEME: Use {theme} (or better match if content suggests different)
   - RECOMMEND ANIMATION PRESET: {animation_preset}
   - Structure: Title, Overview, Key Points, Applications, Conclusion
   - Include speaker notes and design hints
   - Output as JSON with slide structure

3. Presentation Designer:
   - Generate complete PptxGenJS JavaScript code
   - Apply theme: {theme}
   - Apply animations from preset: {animation_preset}
   - Include all {num_slides} slides with professional styling
   - Execute via ShellTools (node create_pptx.js)
   - Output file: {output_filename}

Focus on professional quality, clear visual hierarchy, and engaging content.
"""

    try:
        response = ppt_agent_team.print_response(prompt, markdown=True, stream=True)

        print("\n" + "=" * 80)
        print("Presentation creation workflow completed!")
        print(f"Check for: {output_filename}")
        print("=" * 80 + "\n")

        return response
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        raise


if __name__ == "__main__":
    # Example 1: Corporate presentation
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Healthcare AI - Corporate Theme")
    print("=" * 80)

    create_presentation(
        topic="Artificial Intelligence in Healthcare",
        output_filename="healthcare_ai_corporate.pptx",
        theme="corporate_blue",
        animation_preset="professional",
        num_slides=7,
    )

    # Example 2: Creative presentation
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Future of Work - Creative Theme")
    print("=" * 80)

    # Uncomment to run:
    # create_presentation(
    #     topic="The Future of Work: Remote, Hybrid, and In-Person",
    #     output_filename="future_of_work_creative.pptx",
    #     theme="creative",
    #     animation_preset="dynamic",
    #     num_slides=7,
    # )
