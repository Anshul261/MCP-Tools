"""
Custom File Generation Tools for Document Team Agent
Using the @tool() decorator pattern from Agno framework
"""

import json
import csv
from pathlib import Path
from typing import Optional, Union, List, Dict
from datetime import datetime

from agno.tools import tool

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


# Global output directory configuration
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _generate_filename(base_name: str, extension: str) -> str:
    """Generate a unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean the base name
    clean_name = "".join(
        c for c in base_name if c.isalnum() or c in (" ", "_", "-")
    ).strip()
    clean_name = clean_name.replace(" ", "_")
    filename = f"{clean_name}_{timestamp}.{extension}"
    return str(OUTPUT_DIR / filename)


@tool()
def generate_json_file(data: str, filename: str = "output") -> str:
    """Generate a JSON file from provided data.

    Args:
        data: JSON string or dictionary data to save
        filename: Base name for the file (without extension)

    Returns:
        Success message with the file path or error message
    """
    try:
        # Parse JSON string if needed
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON string provided"
        else:
            parsed_data = data

        filepath = _generate_filename(filename, "json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)

        return f"Successfully generated JSON file: {filepath}"

    except Exception as e:
        return f"Error generating JSON file: {str(e)}"


@tool()
def generate_csv_file(
    data: str, filename: str = "output", headers: Optional[str] = None
) -> str:
    """Generate a CSV file from tabular data.

    Args:
        data: CSV formatted string or comma-separated data
        filename: Base name for the file (without extension)
        headers: Optional comma-separated list of column headers

    Returns:
        Success message with the file path or error message
    """
    try:
        filepath = _generate_filename(filename, "csv")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            if headers:
                f.write(headers + "\n")
            f.write(data)

        return f"Successfully generated CSV file: {filepath}"

    except Exception as e:
        return f"Error generating CSV file: {str(e)}"


@tool()
def generate_pdf_file(
    content: str, filename: str = "output", title: Optional[str] = None
) -> str:
    """Generate a PDF file from text content with markdown-like formatting.

    Args:
        content: Text content to include in the PDF (supports markdown headings with #)
        filename: Base name for the file (without extension)
        title: Optional title for the document

    Returns:
        Success message with the file path or error message
    """
    if not HAS_REPORTLAB:
        return "Error: reportlab not installed. Install with: pip install reportlab"

    try:
        filepath = _generate_filename(filename, "pdf")

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title if provided
        if title:
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2 * inch))

        # Process content - split by paragraphs
        paragraphs = content.split("\n\n")

        for para in paragraphs:
            if para.strip():
                # Check if it's a heading (starts with #)
                if para.strip().startswith("#"):
                    # Determine heading level
                    level = len(para) - len(para.lstrip("#"))
                    heading_text = para.lstrip("#").strip()

                    if level == 1:
                        style = styles["Heading1"]
                    elif level == 2:
                        style = styles["Heading2"]
                    else:
                        style = styles["Heading3"]

                    story.append(Paragraph(heading_text, style))
                    story.append(Spacer(1, 0.1 * inch))
                else:
                    # Regular paragraph - clean markdown formatting
                    clean_para = para.replace("**", "<b>").replace("__", "<i>")
                    story.append(Paragraph(clean_para, styles["BodyText"]))
                    story.append(Spacer(1, 0.1 * inch))

        doc.build(story)

        return f"Successfully generated PDF file: {filepath}"

    except Exception as e:
        return f"Error generating PDF file: {str(e)}"


@tool()
def generate_text_file(content: str, filename: str = "output") -> str:
    """Generate a plain text file from string content.

    Args:
        content: Text content to save
        filename: Base name for the file (without extension)

    Returns:
        Success message with the file path or error message
    """
    try:
        filepath = _generate_filename(filename, "txt")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully generated text file: {filepath}"

    except Exception as e:
        return f"Error generating text file: {str(e)}"


# List of all file generation tools for easy import
FILE_GENERATION_TOOLS = [
    generate_json_file,
    generate_csv_file,
    generate_pdf_file,
    generate_text_file,
]


def set_output_directory(directory: str):
    """Set the output directory for file generation"""
    global OUTPUT_DIR
    OUTPUT_DIR = Path(directory)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
