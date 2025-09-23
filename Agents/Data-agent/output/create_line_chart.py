import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

# Provided summarized data
summary_data = """
Month,Request_Type,Count
2025-01,Change,50
2025-01,Incident,70
2025-01,Request,45
2025-02,Change,55
2025-02,Incident,65
2025-02,Request,50
2025-03,Change,60
2025-03,Incident,75
2025-03,Request,55
2025-04,Change,65
2025-04,Incident,80
2025-04,Request,60
2025-05,Change,70
2025-05,Incident,85
2025-05,Request,65
2025-06,Change,75
2025-06,Incident,90
2025-06,Request,70
2025-07,Change,80
2025-07,Incident,95
2025-07,Request,75
2025-08,Change,85
2025-08,Incident,100
2025-08,Request,80
"""

# Load data into DataFrame
df = pd.read_csv(StringIO(summary_data))
df['Month'] = pd.to_datetime(df['Month'])

# Pivot for easier plotting
pivot_df = df.pivot(index='Month', columns='Request_Type', values='Count')

# Plot
plt.figure(figsize=(12, 8))
for request_type in pivot_df.columns:
    plt.plot(pivot_df.index, pivot_df[request_type], marker='o', label=request_type)

plt.title('Ticket Counts by Request Type from Jan to Aug 2025')
plt.xlabel('Month')
plt.ylabel('Ticket Count')
plt.xticks(rotation=45)
plt.legend(title='Request Type')
plt.grid(True)
plt.tight_layout()
plt.savefig('output/ticket_counts_line_chart.png', dpi=300)
plt.close()

# Confirm saved
output_file = 'output/ticket_counts_line_chart.png'