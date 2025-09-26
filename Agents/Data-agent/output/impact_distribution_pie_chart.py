import matplotlib.pyplot as plt

# Data
categories = ['Medium Impact', 'Low Impact', 'High Impact']
counts = [66907, 66833, 66260]

# Plot
plt.figure(figsize=(10, 8))
plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
plt.title('Ticket Distribution by Impact Category')
plt.axis('equal')
plt.savefig('output/impact_distribution_pie_chart.png', dpi=300, bbox_inches='tight')
plt.close()