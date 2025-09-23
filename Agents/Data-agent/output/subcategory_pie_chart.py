import matplotlib.pyplot as plt

# Data for Subcategory
subcategories = ['Desktop', 'Laptop', 'Printer', 'OS Issue', 'Application', 'Connectivity', 'Bandwidth', 'Other Sub']
subcategory_percentages = [25, 15, 10, 20, 15, 10, 4, 1]

# Create pie chart for Subcategory
plt.figure(figsize=(10, 8))
plt.pie(subcategory_percentages, labels=subcategories, autopct='%1.1f%%', startangle=90)
plt.title('Ticket Distribution by Subcategory')
plt.axis('equal')
plt.savefig('output/subcategory_pie_chart.png', dpi=300, bbox_inches='tight')
plt.close()