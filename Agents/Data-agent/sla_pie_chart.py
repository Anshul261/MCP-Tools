import matplotlib.pyplot as plt

# Data
labels = ['High SLA', 'Low SLA', 'Medium SLA']
sizes = [66809, 66740, 66451]
colors = ['#4CAF50', '#FF5722', '#FFC107']

# Create pie chart
plt.figure(figsize=(8, 6))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140, shadow=True)
plt.title('SLA Ticket Distribution')
plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular

# Save as PNG
plt.savefig('output/sla_ticket_distribution_pie_chart.png')
plt.close()

print('sla_ticket_distribution_pie_chart.png created')