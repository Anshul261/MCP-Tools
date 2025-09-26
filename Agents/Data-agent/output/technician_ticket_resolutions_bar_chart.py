import matplotlib.pyplot as plt

# Data
technicians = ['Imran S', 'Samaira K', 'Surendren M']
tickets_resolved = [50172, 50079, 49797]

# Plotting bar chart
plt.figure(figsize=(10, 6))
plt.bar(technicians, tickets_resolved, color=['blue', 'green', 'red'])
plt.xlabel('Technician Names')
plt.ylabel('Number of Tickets Resolved')
plt.title('Tickets Resolved by Technicians')
plt.tight_layout()
plt.savefig('output/technician_ticket_resolutions_bar_chart.png', dpi=300, bbox_inches='tight')
plt.close()