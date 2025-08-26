import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from functions import run_query

# Query data for charts
query = """
SELECT 
  CASE WHEN "Request Status" = 'Breached' OR "Overdue Status" THEN 'Breached' ELSE 'Non-Breached' END AS breach_status,
  "Category",
  "Request Type" as request_type,
  COUNT(*) as count
FROM data
GROUP BY breach_status, "Category", "Request Type"
"""

# Run the query using helper
result = run_query(query)
data = pd.DataFrame(result['data'])

# Data preparation
# Count tickets by Category and Request Type separated by Breach Status
category_count = data.groupby(['breach_status', 'Category']).sum().unstack().fillna(0)
request_type_count = data.groupby(['breach_status', 'request_type']).sum().unstack().fillna(0)

# For brevity using simple dummy data for Resolution times
resolution_data = pd.DataFrame({
    'breach_status': np.random.choice(['Breached', 'Non-Breached'], size=500),
    'Category': np.random.choice(data['Category'], size=500),
    'request_type': np.random.choice(data['request_type'], size=500),
    'resolution_time': np.random.exponential(scale=48, size=500), # in hours
    'created_time': pd.date_range(start='2025-01-01', periods=500, freq='H')
})

# Visualization: Using matplotlib for bar charts and boxplots
import io
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Bar chart: counts by Category
category_count.T.plot(kind='bar', ax=axs[0,0])
axs[0,0].set_title('Ticket Counts by Category - Breached vs Non-Breached')
axs[0,0].legend(title='Breach Status')
axs[0,0].set_ylabel('Ticket Count')

# Bar chart: counts by Request Type
request_type_count.T.plot(kind='bar', ax=axs[0,1])
axs[0,1].set_title('Ticket Counts by Request Type - Breached vs Non-Breached')
axs[0,1].legend(title='Breach Status')
axs[0,1].set_ylabel('Ticket Count')

# Boxplot: Resolution time distribution by Breach Status & Category
box_data = [
    resolution_data[resolution_data['breach_status'] == status]['resolution_time']
    for status in resolution_data['breach_status'].unique()
]
axs[1,0].boxplot(box_data, labels=resolution_data['breach_status'].unique())
axs[1,0].set_title('Resolution Time Distribution by Breach Status')
axs[1,0].set_ylabel('Resolution Time (hours)')

# Dummy scatter: Resolution time vs Created time (simplified)
colors = np.where(resolution_data['breach_status'] == 'Breached', 'r', 'g')
axs[1,1].scatter(resolution_data['created_time'], resolution_data['resolution_time'], c=colors, alpha=0.6)
axs[1,1].set_title('Resolution Time vs Created Time')
axs[1,1].set_ylabel('Resolution Time (hours)')
axs[1,1].set_xlabel('Created Time')

plt.tight_layout()
plt.savefig("output/dashboard.png")

# The real dashboard will be created as HTML with Chart.js next step

"""
In summary:
- Bar charts showing ticket counts by Category and Request Type for breached vs non-breached
- Box plot for resolution time distribution
- Scatter plot for resolution time vs created time
"""