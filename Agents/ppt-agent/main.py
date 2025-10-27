#!/usr/bin/env python3
"""
PPT Agent Team - Interactive Terminal Interface

Create professional, research-backed PowerPoint presentations through a conversational interface.

The team automatically orchestrates:
1. ResearchAgent: Deep web research using DuckDuckGo
2. ContentSynthesizer: Transform research into presentation content
3. PresentationDesigner: Create visually stunning presentations with charts/graphs

Usage:
    python main.py
"""

from ppt_agent_team import create_presentation, ppt_agent_team
import os


def print_header():
    """Print application header"""
    print("\n" + "=" * 80)
    print("  PPT AGENT TEAM - AI-Powered Presentation Generator".center(80))
    print("=" * 80)
    print("\nCreate professional presentations with:")
    print("  • Deep web research via DuckDuckGo")
    print("  • High-quality synthesized content")
    print("  • Professional visual design with charts and graphs")
    print("\n" + "-" * 80)


def print_menu():
    """Print interactive menu"""
    print("\nOptions:")
    print("  1. Create presentation from topic")
    print("  2. Ask team a question")
    print("  3. View available commands")
    print("  4. Exit")
    print("\nEnter your choice (1-4): ", end="")


def create_presentation_interactive():
    """Interactive presentation creation"""
    print("\n" + "-" * 80)
    print("CREATE PRESENTATION")
    print("-" * 80)

    topic = input("\nEnter presentation topic: ").strip()
    if not topic:
        print("✗ Topic cannot be empty")
        return

    # Get filename
    output_filename = input("Enter output filename (default: presentation.pptx): ").strip()
    if not output_filename:
        output_filename = "presentation.pptx"
    elif not output_filename.endswith(".pptx"):
        output_filename += ".pptx"

    # Get number of slides
    num_slides_input = input("Enter number of slides (default: 7): ").strip()
    try:
        num_slides = int(num_slides_input) if num_slides_input else 7
        if num_slides < 3:
            print("✗ Minimum 3 slides required")
            return
        if num_slides > 15:
            print("⚠ Warning: More than 15 slides may take longer to process")
    except ValueError:
        print("✗ Invalid number of slides")
        return

    print(f"\n{'='*80}")
    print(f"Creating presentation: {topic}")
    print(f"Output: {output_filename}")
    print(f"Slides: {num_slides}")
    print(f"{'='*80}\n")

    try:
        create_presentation(
            topic=topic,
            output_filename=output_filename,
            num_slides=num_slides,
        )
        print(f"\n{'='*80}")
        print(f"✓ SUCCESS: Presentation created as '{output_filename}'")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("Please check your API configuration and try again.\n")


def ask_team_question():
    """Ask the team a direct question"""
    print("\n" + "-" * 80)
    print("ASK THE TEAM")
    print("-" * 80)
    print("\nAsk the team any question about presentations, content, design, or research.")
    print("Type 'back' to return to main menu.\n")

    while True:
        question = input("Your question: ").strip()

        if question.lower() == "back":
            break

        if not question:
            print("Please enter a valid question\n")
            continue

        print(f"\n{'='*80}")
        print("Team Response:")
        print(f"{'='*80}\n")

        try:
            response = ppt_agent_team.print_response(
                f"""
                User Question: {question}

                Please provide a comprehensive, helpful response to this question.
                If it relates to presentations, provide specific examples and best practices.
                If it relates to research or content, provide actionable insights.
                If it relates to design, provide specific styling recommendations.
                """,
                markdown=True,
            )
            print("\n" + "=" * 80)
            print("End of response")
            print("=" * 80 + "\n")
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}\n")


def show_commands():
    """Show available commands and examples"""
    print("\n" + "-" * 80)
    print("AVAILABLE COMMANDS & EXAMPLES")
    print("-" * 80)

    commands = {
        "Create Presentations": [
            "Topic: Any subject (e.g., 'AI in Healthcare', 'Cloud Computing', 'Digital Marketing')",
            "Customize: Choose number of slides (3-15)",
            "Output: Save as any .pptx filename",
            "Includes: Research, content synthesis, professional design, charts/graphs",
        ],
        "Ask Questions": [
            "Content questions: 'What makes a good slide layout?'",
            "Design questions: 'How do I choose colors for presentations?'",
            "Research questions: 'How to find recent statistics on AI?'",
            "Technical questions: 'What chart types work best for financial data?'",
        ],
        "Examples": [
            "✓ Create a 7-slide presentation on 'Machine Learning Basics'",
            "✓ Ask: 'What are the best practices for presenting data?'",
            "✓ Ask: 'How do I make presentations more engaging?'",
            "✓ Create a 10-slide presentation on 'Cybersecurity Trends 2024'",
        ],
    }

    for category, items in commands.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")

    print("\n" + "-" * 80)


def show_features():
    """Show system features"""
    print("\n" + "=" * 80)
    print("SYSTEM FEATURES")
    print("=" * 80)

    features = [
        ("Research Agent", "Performs deep web searches via DuckDuckGo (8-10+ searches per topic)"),
        ("Content Synthesizer", "Transforms research into clear, compelling, presentation-ready content"),
        ("Presentation Designer", "Creates professional designs with colors, fonts, layouts, and styling"),
        ("Chart Generation", "Adds professional charts, graphs, and data visualizations"),
        ("Team Orchestration", "Automatically coordinates all agents for seamless workflow"),
        ("Interactive Terminal", "Conversational interface for easy interaction"),
    ]

    for i, (feature, description) in enumerate(features, 1):
        print(f"\n{i}. {feature}")
        print(f"   └─ {description}")

    print("\n" + "=" * 80)


def main():
    """Main interactive loop"""
    os.system("clear") if os.name == "posix" else os.system("cls")
    print_header()

    while True:
        print_menu()

        choice = input().strip()

        if choice == "1":
            create_presentation_interactive()
        elif choice == "2":
            ask_team_question()
        elif choice == "3":
            show_commands()
            show_features()
        elif choice == "4":
            print("\n" + "=" * 80)
            print("Thank you for using PPT Agent Team!".center(80))
            print("=" * 80 + "\n")
            break
        else:
            print("✗ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("Exiting PPT Agent Team...".center(80))
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        print("\nPlease check your configuration and try again.")
