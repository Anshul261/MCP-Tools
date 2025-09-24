import matplotlib.pyplot as plt

# Data extracted from SQL query
Year = [2025, 2025, 2025, 2025, 2025, 2025, 2025, 2025]
Month = [1, 2, 3, 4, 5, 6, 7, 8]
Ticket_Count = [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]

# Create a month-year label for x-axis
labels = [f'{m}/{y}' for y, m in zip(Year, Month)]

plt.figure(figsize=(12, 6))
plt.plot(labels, Ticket_Count, marker='o', linestyle='-', color='b')
plt.title('Monthly Ticket Trends')
plt.xlabel('Month/Year')
plt.ylabel('Ticket Count')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('output/monthly_ticket_trends.png', dpi=300, bbox_inches='tight')
plt.close()

print('monthly_ticket_trends.png saved')