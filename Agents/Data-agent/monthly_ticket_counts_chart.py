import matplotlib.pyplot as plt

# Data
months = ['January', 'February', 'March', 'April']
ticket_counts = [1071, 1033, 1127, 1238]

# Plot
plt.figure(figsize=(8, 5))
plt.plot(months, ticket_counts, marker='o', linestyle='-', color='blue')
plt.title('Monthly Ticket Counts (Jan - Apr 2025)')
plt.xlabel('Month')
plt.ylabel('Ticket Count')
plt.grid(True)
plt.tight_layout()

# Save the chart
plt.savefig('output/monthly_ticket_counts_line_chart.png')
plt.close()

# Return filename
'output/monthly_ticket_counts_line_chart.png'