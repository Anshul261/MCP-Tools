import matplotlib.pyplot as plt

# Data for Category
categories = ['Hardware', 'Software', 'Network', 'Other']
category_percentages = [40, 35, 15, 10]

# Create pie chart for Category
plt.figure(figsize=(8, 8))
plt.pie(category_percentages, labels=categories, autopct='%1.1f%%', startangle=90)
plt.title('Ticket Distribution by Category')
plt.axis('equal')
plt.savefig('output/category_pie_chart.png', dpi=300, bbox_inches='tight')
plt.close()