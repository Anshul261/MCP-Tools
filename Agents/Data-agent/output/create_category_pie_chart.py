import matplotlib.pyplot as plt

# Provided category counts and percentages
categories = ['Category A', 'Category B', 'Category C', 'Category D']
percentages = [25, 35, 20, 20]

# Create pie chart
plt.figure(figsize=(10, 8))
plt.pie(percentages, labels=categories, autopct='%1.1f%%', startangle=90)
plt.title('Category Distribution')
plt.axis('equal')
plt.savefig('output/category_distribution_pie_chart.png', dpi=300, bbox_inches='tight')
plt.close()

print('output/category_distribution_pie_chart.png saved')