import matplotlib.pyplot as plt

# Data
categories = ['Microsoft', 'Reports', 'End User Support', 'Information Security', 'Systems', 'Network & Security', 'Patch Management', 'Application', 'Telecom', 'Preventive Maintenance', 'License Changes', 'Cloud Services', 'Infra Monitoring', 'Microsoft Dynamics 365 - Barton', 'Procurement']
counts = [1356, 1021, 873, 391, 349, 170, 135, 66, 40, 26, 14, 11, 8, 6, 3]

# Plotting pie chart
plt.figure(figsize=(10, 8))
plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 9})
plt.title('Ticket Categories Distribution')
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig('ticket_category_pie_chart.png')
plt.close()