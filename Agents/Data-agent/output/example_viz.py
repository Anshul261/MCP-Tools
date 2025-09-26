#!/usr/bin/env python3
"""
Working example of creating a pie chart that the agent can follow
"""
import matplotlib.pyplot as plt
import numpy as np

# Example data
categories = ['Network', 'Security', 'Software', 'Hardware', 'Other']
counts = [25, 30, 20, 15, 10]

# Create pie chart
plt.figure(figsize=(10, 8))
plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
plt.title('Ticket Categories Distribution')
plt.axis('equal')

# Save to output folder
plt.savefig('output/example_category_pie_chart.png', dpi=300, bbox_inches='tight')
plt.close()

print("✅ Example pie chart saved to: output/example_category_pie_chart.png")