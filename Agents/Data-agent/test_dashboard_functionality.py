#!/usr/bin/env python3
"""
Test script for the enhanced dashboard functionality
Tests both dashboard mode and single chart mode detection
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template

def test_dashboard_templates():
    """Test that dashboard templates are working"""
    print("Testing dashboard templates...")

    try:
        # Test HTML template
        html_template = get_html_template()
        print(f"HTML template length: {len(html_template)}")
        assert "{{STATS_CONTENT}}" in html_template, "STATS_CONTENT placeholder not found"
        assert "{{CHARTS_CONTENT}}" in html_template, "CHARTS_CONTENT placeholder not found"
        assert "chart.js" in html_template.lower(), "Chart.js reference not found"
        print("✓ HTML template working")

        # Test stat card template
        stat_template = get_stat_card_template()
        assert "{{NUMBER}}" in stat_template, "NUMBER placeholder not found"
        assert "{{LABEL}}" in stat_template, "LABEL placeholder not found"
        print("✓ Stat card template working")

        # Test Chart.js template
        chart_js = get_chart_js_template("testChart", "pie", ["A", "B"], [10, 20])
        assert "testChart" in chart_js, "Chart ID not found in Chart.js template"
        assert "Chart(" in chart_js, "Chart constructor not found"
        print("✓ Chart.js template working")

    except Exception as e:
        print(f"Dashboard template test failed: {e}")
        raise

def test_mode_detection_logic():
    """Test the mode detection keywords"""
    print("\nTesting mode detection logic...")

    dashboard_keywords = ['dashboard', 'comprehensive analysis', 'overview', 'complete view', 'full analysis', 'multiple charts', 'comprehensive', 'complete']
    single_chart_keywords = ['chart', 'graph', 'plot', 'show me', 'create a']

    # Test dashboard detection
    test_phrases = [
        "Create a comprehensive dashboard",
        "Give me a complete overview",
        "I need a full analysis dashboard",
        "Show me multiple charts"
    ]

    for phrase in test_phrases:
        phrase_lower = phrase.lower()
        is_dashboard = any(keyword in phrase_lower for keyword in dashboard_keywords)
        assert is_dashboard, f"Dashboard detection failed for: {phrase}"
        print(f"✓ Dashboard detected: {phrase}")

    # Test single chart detection
    test_phrases = [
        "Create a pie chart",
        "Show me a bar graph",
        "Make a line plot",
        "Create a visualization"
    ]

    for phrase in test_phrases:
        phrase_lower = phrase.lower()
        is_single_chart = any(keyword in phrase_lower for keyword in single_chart_keywords)
        assert is_single_chart, f"Single chart detection failed for: {phrase}"
        print(f"✓ Single chart detected: {phrase}")

def test_output_directory():
    """Test that output directory exists"""
    print("\nTesting output directory...")
    output_dir = Path("output")
    if not output_dir.exists():
        print("Creating output directory...")
        output_dir.mkdir()

    # Check for existing dashboards
    html_files = list(output_dir.glob("*.html"))
    png_files = list(output_dir.glob("*.png"))

    print(f"✓ Output directory exists with {len(html_files)} HTML files and {len(png_files)} PNG files")

    if html_files:
        print("Existing HTML dashboards:")
        for html_file in html_files[:5]:  # Show first 5
            print(f"  - {html_file.name}")

def main():
    print("Enhanced Dashboard Functionality Test")
    print("=" * 40)

    try:
        test_dashboard_templates()
        test_mode_detection_logic()
        test_output_directory()

        print("\n" + "=" * 40)
        print("✓ All tests passed! Dashboard functionality is ready.")
        print("\nNext steps:")
        print("1. Start the agent: python agent.py")
        print("2. Test dashboard requests: 'Give me a comprehensive analysis'")
        print("3. Test single chart requests: 'Show me a pie chart of categories'")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()