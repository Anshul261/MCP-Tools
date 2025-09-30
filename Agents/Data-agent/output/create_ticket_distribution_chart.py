import matplotlib.pyplot as plt

# Data
persons = ['Imran S', 'Samaira K', 'Surendren M', 'Not Assigned']
ticket_counts = [50172, 50079, 49797, 49952]

# Create bar chart
plt.figure(figsize=(8,5))
plt.bar(persons, ticket_counts, color='skyblue')
plt.ylabel('Ticket Count')
plt.title('Ticket Distribution by Person Assigned')
plt.tight_layout()

# Save figure
filename = 'output/ticket_distribution_by_person.png'
plt.savefig(filename)
plt.close()

filename