import matplotlib.pyplot as plt
import pandas as pd

# Data from the query result
months = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08']
sla_violations = [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]

plt.figure(figsize=(10, 6))
plt.plot(months, sla_violations, marker='o', linestyle='-', color='b')
plt.title('SLA Violations by Month in 2025')
plt.xlabel('Month')
plt.ylabel('Number of SLA Violations')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig('output/sla_violations_2025_line_chart.png')
plt.close()

'sla_violations_2025_line_chart.png'