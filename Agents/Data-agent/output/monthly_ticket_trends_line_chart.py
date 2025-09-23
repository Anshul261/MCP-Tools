import matplotlib.pyplot as plt

# Data
dates = ['January 2025', 'February 2025', 'March 2025', 'April 2025']
tickets = [1071, 1033, 1127, 1238]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(dates, tickets, marker='o', linestyle='-', color='b')
plt.title('Monthly Ticket Trends (Jan - Apr 2025)')
plt.xlabel('Month')
plt.ylabel('Number of Tickets')
plt.grid(True)

# Save
plt.savefig('output/monthly_ticket_trends_2025.png', dpi=300, bbox_inches='tight')
plt.close()