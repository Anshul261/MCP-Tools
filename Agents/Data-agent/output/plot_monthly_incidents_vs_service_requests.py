import matplotlib.pyplot as plt

# Data
months = ['2025-01', '2025-02', '2025-03', '2025-04']
incidents = [100, 120, 130, 125]
service_requests = [150, 140, 160, 155]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(months, incidents, marker='o', label='Incidents')
plt.plot(months, service_requests, marker='o', label='Service Requests')
plt.title('Monthly Breakdown of Incidents vs Service Requests (2025)')
plt.xlabel('Month')
plt.ylabel('Count')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('output/monthly_incidents_vs_service_requests.png', dpi=300, bbox_inches='tight')
plt.close()