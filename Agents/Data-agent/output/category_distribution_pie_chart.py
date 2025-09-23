import matplotlib.pyplot as plt

# Categories and their counts
categories = ['Microsoft', 'Reports', 'End User Support', 'Information Security', 'Systems',
              'Network & Security', 'Patch Management', 'Application', 'Telecom',
              'Preventive Maintenance', 'License Changes', 'Cloud Services',
              'Infra Monitoring', 'Microsoft Dynamics 365 - Barton', 'Procurement']
counts = [1356, 1021, 873, 391, 349, 170, 135, 66, 40, 26, 14, 11, 8, 6, 3]

# Calculate percentages
total = sum(counts)
percentages = [count / total * 100 for count in counts]

# Plot pie chart
plt.figure(figsize=(10, 8))
plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 9})
plt.title('Ticket Category Distribution with Percentages')
plt.tight_layout()

# Save the figure
chart_path = 'category_distribution_pie_chart.png'
plt.savefig(chart_path)
plt.close()

chart_path