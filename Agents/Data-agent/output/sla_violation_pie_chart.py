import matplotlib.pyplot as plt

# Data
labels = ['SLA Violations', 'Non-Violations']
values = [69668, 130332]

# Colors for the pie chart
colors = ['#ff6666', '#66b3ff']

# Create pie chart
plt.figure(figsize=(8, 8))
plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'fontsize': 14})
plt.title('SLA Violations vs Non-Violations', fontsize=16)

# Save to PNG
output_path = 'output/sla_violation_pie_chart.png'
plt.savefig(output_path)
plt.close()

# Return the path of the file saved
output_path