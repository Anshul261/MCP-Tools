import matplotlib.pyplot as plt

# Data
request_types = ['Incident', 'Service Request', 'Preventive Maintenance', 'Security Incident', 'Request For Information', 'Change Requests']
counts = [2245, 2180, 20, 16, 5, 3]

# Create bar chart
plt.figure(figsize=(12, 8))
plt.bar(request_types, counts, color='skyblue')
plt.xlabel('Request Type')
plt.ylabel('Count of Tickets')
plt.title('Count of Tickets by Request Type')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('output/request_type_bar_chart.png', dpi=300, bbox_inches='tight')
plt.close()