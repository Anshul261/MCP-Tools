# PPT Agent Enhancement Guide

## Overview

This guide explains the enhancements made to the PPT Agent system to enable professional presentation generation with PptxGenJS, including themes, animations, and reliable execution via AgentOS ShellTools.

## What's New

### 1. ShellTools Integration ✅
- **File**: `ppt_agent_pptxgenjs.py` (updated)
- **Change**: Added `ShellTools` to PresentationDesigner agent
- **Benefit**: Agents can now directly execute Node.js scripts for PptxGenJS via shell commands
- **Implementation**:
  ```python
  from agno.tools.shell import ShellTools

  designer_agent = Agent(
      name="PresentationDesigner",
      role="Visual Design Specialist using PptxGenJS",
      model=llm,
      instructions=design_instructions,
      tools=[PythonTools(), ShellTools()],  # ← ShellTools added
      markdown=True,
  )
  ```

### 2. Professional Themes ✅
- **File**: `config/themes.json`
- **Themes Included**: 8 professional themes
  1. **corporate_blue** - Corporate, Finance, Business presentations
  2. **tech_modern** - Technology, Startups, Innovation
  3. **premium_dark** - Executive, Premium, Luxury brands
  4. **modern_minimalist** - Creative, Design, Art
  5. **healthcare** - Medical, Healthcare, Pharmaceutical
  6. **academic** - University, Research, Educational
  7. **creative** - Design, Marketing, Creative agencies
  8. **financial** - Finance, Banking, Investment

**Each theme includes**:
- Color palette (primary, secondary, accent, text colors)
- Typography settings (font family, sizes)
- Use case recommendations

**Example**:
```json
{
  "corporate_blue": {
    "name": "Corporate Blue",
    "colors": {
      "primary": "1F4E79",
      "secondary": "4472C4",
      "accent": "F3A612"
    },
    "typography": {
      "title_size": 54,
      "font_family": "Calibri"
    }
  }
}
```

### 3. Animation & Transition Support ✅
- **File**: `config/animations.json`
- **Features**:
  - **Entrance Animations**: Fade, Slide, Zoom, Grow
  - **Exit Animations**: Fade, Slide, Shrink
  - **Emphasis Effects**: Pulse, Glow, Color Wave
  - **Slide Transitions**: Fade, Push, Wipe, Cover, Uncover

**Preset Animation Styles**:
1. **subtle** - Professional, minimal animations
2. **dynamic** - Energetic animations for engagement
3. **professional** - Business-appropriate animations
4. **creative** - Bold, creative animations

**Example**:
```javascript
// In PptxGenJS code
slide.addText("Content", {
    x: 0.5, y: 1.5, w: 9, h: 1,
    fontSize: 18,
    animate: {
        type: "fade",
        duration: 0.5
    }
});
```

### 4. Enhanced Agent System ✅
- **File**: `ppt_agent_enhanced.py` (NEW)
- **Features**:
  - Loads themes from JSON configuration
  - Loads animations from JSON configuration
  - Theme and animation recommendations from Content Synthesizer
  - Full PptxGenJS support with ShellTools execution

**Usage**:
```python
from ppt_agent_enhanced import create_presentation

create_presentation(
    topic="Artificial Intelligence in Healthcare",
    output_filename="healthcare_ai.pptx",
    theme="healthcare",              # Select theme
    animation_preset="professional", # Select animation style
    num_slides=7
)
```

## File Structure

```
ppt-agent/
├── agent.py                          # Simple baseline agent
├── ppt_agent_team.py                 # python-pptx version (unchanged)
├── ppt_agent_pptxgenjs.py            # UPDATED: Added ShellTools
├── ppt_agent_enhanced.py             # NEW: Full-featured with themes
├── main.py                           # Interactive CLI
├── config/
│   ├── themes.json                   # NEW: Theme definitions
│   └── animations.json               # NEW: Animation presets
└── ENHANCEMENT_GUIDE.md              # This file
```

## How to Use

### Option 1: Use Enhanced Agent with Theme Selection

```python
from ppt_agent_enhanced import create_presentation

# Create a healthcare presentation with healthcare theme
create_presentation(
    topic="Medical AI Applications",
    output_filename="medical_ai.pptx",
    theme="healthcare",
    animation_preset="professional",
    num_slides=7
)
```

### Option 2: Use Updated PptxGenJS Agent (with ShellTools)

```python
from ppt_agent_pptxgenjs import create_presentation_pptxgenjs

# Creates presentation and executes via ShellTools
create_presentation_pptxgenjs(
    topic="Artificial Intelligence in Healthcare",
    output_filename="healthcare_ai.pptx",
    num_slides=7
)
```

### Option 3: Manual Theme Configuration

```python
import json
from pathlib import Path

# Load themes
with open('config/themes.json', 'r') as f:
    themes = json.load(f)

# Get corporate blue theme
corporate_blue = themes['themes']['corporate_blue']
print(corporate_blue['colors'])
# Output: {'primary': '1F4E79', 'secondary': '4472C4', ...}
```

## Execution Flow

### Diagram: Enhanced Presentation Generation

```
┌─────────────────────────────────────────────────────────┐
│           Create Presentation Request                   │
│  Topic: "AI in Healthcare"                              │
│  Theme: "healthcare"                                    │
│  Animation: "professional"                              │
└──────────────────┬──────────────────────────────────────┘
                   │
       ┌───────────▼────────────┐
       │   Research Agent       │
       │ (DuckDuckGo searches)  │
       └────────────┬───────────┘
                    │
        ┌───────────▼──────────────────┐
        │  Content Synthesizer         │
        │ (Recommends theme)           │
        │ (Recommends animation)       │
        └────────────┬─────────────────┘
                     │
         ┌───────────▼──────────────────┐
         │ Presentation Designer        │
         │ (Generates PptxGenJS code)   │
         │ (Applies theme + animations) │
         └────────────┬─────────────────┘
                      │
         ┌────────────▼──────────────┐
         │   PythonTools            │
         │ (Write JS to file)        │
         └────────────┬──────────────┘
                      │
         ┌────────────▼──────────────┐
         │    ShellTools            │
         │ (node create_pptx.js)    │
         │ Executes PptxGenJS       │
         └────────────┬──────────────┘
                      │
         ┌────────────▼──────────────┐
         │  PPTX File Created       │
         │ (healthcare_ai.pptx)     │
         └──────────────────────────┘
```

## Configuration Management

### Adding a New Theme

1. Edit `config/themes.json`
2. Add theme configuration:
```json
{
  "your_theme": {
    "name": "Your Theme Name",
    "description": "Theme description",
    "colors": {
      "primary": "XXXXXX",
      "secondary": "XXXXXX",
      "accent": "XXXXXX",
      "dark": "XXXXXX",
      "light": "XXXXXX",
      "white": "FFFFFF",
      "text": "XXXXXX"
    },
    "typography": {
      "title_size": 54,
      "header_size": 40,
      "body_size": 18,
      "font_family": "Arial"
    },
    "use_case": "Presentation types suited for this theme"
  }
}
```
3. Update Content Synthesizer instructions to include new theme

### Adding a New Animation Preset

1. Edit `config/animations.json`
2. Add preset configuration:
```json
{
  "your_preset": {
    "name": "Your Preset",
    "description": "Preset description",
    "entrance": "fade",
    "exit": "fade",
    "emphasis": "pulse",
    "transition": "push"
  }
}
```

## Execution Methods

### Method 1: ShellTools (Recommended)
- **Pros**: Native AgentOS integration, clean execution, proper error handling
- **Cons**: Requires shell access

```python
# Agent uses ShellTools internally
agent.print_response("Generate presentation", markdown=True)
```

### Method 2: PythonTools (Fallback)
- **Pros**: Works without shell access, Python-friendly
- **Cons**: Requires manual subprocess management

```python
import subprocess

with open('create_pptx.js', 'w') as f:
    f.write(js_code)
result = subprocess.run(['node', 'create_pptx.js'], capture_output=True)
```

## Quality Improvements

### What Changed

| Aspect | Before | After |
|--------|--------|-------|
| **Design Options** | Limited python-pptx capabilities | 8+ professional themes |
| **Animation Support** | None | Full entrance, exit, emphasis, transition |
| **Execution** | Manual subprocess | ShellTools integration + fallback |
| **Theme Consistency** | Manual configuration | JSON-based, agent-recommended |
| **Color Management** | Ad-hoc RGB values | Theme-based color palettes |
| **Typography** | Manual sizing | Theme-based hierarchy |

### Benefits

1. **Professional Output**: Themes ensure consistent, professional-looking presentations
2. **Faster Development**: Agents recommend appropriate themes automatically
3. **Flexible Styling**: Easy to create and apply new themes
4. **Better Animations**: Smooth transitions enhance engagement
5. **Reliable Execution**: ShellTools + fallback ensures robust code generation

## Testing the Enhancement

### Quick Test: Verify ShellTools Integration

```python
from agno.agent import Agent
from agno.tools.shell import ShellTools

agent = Agent(tools=[ShellTools()])
response = agent.print_response("Run 'node -v' to check Node.js version")
print(response)  # Should show Node.js version
```

### Full Test: Create Sample Presentation

```bash
# From ppt-agent directory
python ppt_agent_enhanced.py
```

This will:
1. Create a presentation on "Artificial Intelligence in Healthcare"
2. Apply the "corporate_blue" theme
3. Use "professional" animation preset
4. Generate and execute PptxGenJS code via ShellTools
5. Output: `healthcare_ai_corporate.pptx`

### Verify Files

```bash
# Check if theme configuration loaded
python -c "from ppt_agent_enhanced import THEMES; print(list(THEMES.keys()))"

# Output should show: corporate_blue, tech_modern, etc.
```

## Troubleshooting

### Issue: "Node.js not found"
**Solution**:
- Install Node.js from https://nodejs.org/
- Verify: `node -v` in terminal

### Issue: "pptxgenjs module not found"
**Solution**:
- Install via npm: `npm install pptxgenjs`
- Or let agent run: `npm install pptxgenjs` automatically

### Issue: ShellTools not executing
**Solution**:
- Verify shell access is available
- Fallback to PythonTools with subprocess
- Check agent has both PythonTools() and ShellTools() in tools list

### Issue: Theme colors not applying
**Solution**:
- Verify theme exists in `config/themes.json`
- Check theme name matches exactly in agent prompt
- Ensure Content Synthesizer recommends valid theme

## Next Steps & Roadmap

### Completed ✅
- ShellTools integration
- 8 professional themes
- Animation presets
- Enhanced agent system
- JSON configuration management

### Future Enhancements (Optional)
- [ ] Web UI for theme customization
- [ ] Live theme preview
- [ ] Custom animation timeline builder
- [ ] Template library with pre-made slide layouts
- [ ] Presentation analytics and metrics
- [ ] Version control for presentations
- [ ] Collaborative editing support
- [ ] Real-time preview via browser

## Files Modified

### Updated Files
- **ppt_agent_pptxgenjs.py**: Added ShellTools import and integration

### New Files
- **ppt_agent_enhanced.py**: Full-featured agent with themes and animations
- **config/themes.json**: 8 professional theme definitions
- **config/animations.json**: Animation presets and effects
- **ENHANCEMENT_GUIDE.md**: This documentation

### Unchanged
- **agent.py**: Simple baseline agent
- **ppt_agent_team.py**: python-pptx version
- **main.py**: Interactive CLI

## Support & Documentation

### AgentOS Documentation
- [ShellTools](https://docs.agno.com/concepts/tools/toolkits/local/shell)
- [PythonTools](https://docs.agno.com/concepts/tools/toolkits/local/python)
- [Team Coordination](https://docs.agno.com/concepts/team)

### PptxGenJS Documentation
- [Official Docs](https://gitbrent.github.io/PptxGenJS/)
- [GitHub](https://github.com/gitbrent/PptxGenJS)
- [Demo Slides](https://gitbrent.github.io/PptxGenJS/demo/)

### Color Tools
- [HEX to RGB Converter](https://www.rapidtables.com/convert/color/hex-to-rgb.html)
- [Color Palette Generator](https://coolors.co/)
- [Accessible Color Contrast](https://webaim.org/resources/contrastchecker/)

## Summary

The PPT Agent has been enhanced with:
1. **ShellTools Integration** - Direct Node.js execution from agents
2. **Professional Themes** - 8 configurable design systems
3. **Animation Support** - 4 preset animation styles with customizable effects
4. **Configuration Management** - JSON-based theme and animation configuration
5. **Enhanced Agent** - Full-featured `ppt_agent_enhanced.py` with all features

This enables the agent to generate professional, visually consistent, animated presentations with minimal user configuration while maintaining full flexibility for customization.

---

**Version**: 1.0
**Last Updated**: 2025-10-27
**Status**: Ready for Production
