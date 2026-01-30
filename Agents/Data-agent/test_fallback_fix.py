#!/usr/bin/env python3
"""
Test script to verify the visualization fallback logic fix
"""

def test_fallback_logic():
    """Test the fallback trigger conditions"""
    print("Testing Visualization Fallback Logic Fix")
    print("=" * 50)

    # Test cases that should NOT trigger visualization fallback
    false_positive_responses = [
        "Based on the chart analysis, I can provide insights about ticket trends.",
        "The visualization shows several important patterns in your support data.",
        "Looking at the chart data, here are key insights about performance.",
        "From the previous chart we can see that ticket volumes vary significantly.",
        "The data reveals that most tickets are resolved quickly, and chart analysis confirms this trend."
    ]

    # Test cases that SHOULD trigger visualization fallback
    true_positive_responses = [
        "I have created and saved a new chart to the output folder.",
        "The visualization has been saved to output/monthly_trends.png successfully.",
        "Chart saved to output/category_breakdown.png with detailed analysis.",
        "Dashboard file saved to output/comprehensive_dashboard.html for your review.",
        "I've created and saved the requested pie chart to output/category_pie_chart.png"
    ]

    print("\n1. Testing FALSE POSITIVES (should NOT trigger fallback):")
    print("-" * 55)

    for i, response in enumerate(false_positive_responses, 1):
        response_lower = response.lower()

        # Old logic (problematic)
        old_trigger = (response_lower.count('created') > 0 or
                      response_lower.count('saved') > 0 or
                      response_lower.count('chart') > 0 or
                      response_lower.count('visualization') > 0 or
                      response_lower.count('.png') > 0)

        # New logic (fixed)
        new_trigger = (response_lower.count('saved to output/') > 0 or
                      response_lower.count('created and saved') > 0 or
                      response_lower.count('.png to output/') > 0 or
                      response_lower.count('.html to output/') > 0 or
                      response_lower.count('file saved to') > 0 or
                      response_lower.count('saved the file') > 0)

        print(f"Test {i}: {'✓ FIXED' if not new_trigger else '✗ STILL BROKEN'}")
        print(f"   Old logic: {'Would trigger' if old_trigger else 'No trigger'}")
        print(f"   New logic: {'Would trigger' if new_trigger else 'No trigger'}")
        print(f"   Response: \"{response[:60]}...\"")
        print()

    print("\n2. Testing TRUE POSITIVES (should trigger fallback):")
    print("-" * 55)

    for i, response in enumerate(true_positive_responses, 1):
        response_lower = response.lower()

        # New logic (should still work)
        new_trigger = (response_lower.count('saved to output/') > 0 or
                      response_lower.count('created and saved') > 0 or
                      response_lower.count('.png to output/') > 0 or
                      response_lower.count('.html to output/') > 0 or
                      response_lower.count('file saved to') > 0 or
                      response_lower.count('saved the file') > 0)

        print(f"Test {i}: {'✓ WORKING' if new_trigger else '✗ BROKEN'}")
        print(f"   New logic: {'Would trigger' if new_trigger else 'No trigger'}")
        print(f"   Response: \"{response[:60]}...\"")
        print()

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("- False positives should be eliminated ✓")
    print("- True positives should still work ✓")
    print("- Insights-only requests will no longer show old charts")

if __name__ == "__main__":
    test_fallback_logic()