import matplotlib.pyplot as plt
import pandas as pd
import duckdb

# Load CSV into DuckDB
con = duckdb.connect(database=':memory:')
con.execute("CREATE TABLE tickets AS SELECT * FROM read_csv_auto('realistic_ticket_data.csv')")

query = '''
SELECT strftime('%Y-%m', "Created Time") AS Month, Technician, COUNT(*) AS TicketCount 
FROM tickets 
WHERE Technician != 'Not Assigned' 
GROUP BY Month, Technician 
ORDER BY Month, Technician;
'''
df = con.execute(query).fetchdf()

# Pivot for easier plotting
pivot_df = df.pivot(index='Month', columns='Technician', values='TicketCount')

# Plot
plt.figure(figsize=(12, 7))
for technician in pivot_df.columns:
    plt.plot(pivot_df.index, pivot_df[technician], marker='o', label=technician)

plt.title('Monthly Ticket Trends by Technician')
plt.xlabel('Month')
plt.ylabel('Number of Tickets')
plt.xticks(rotation=45)
plt.legend(title='Technician')
plt.grid(True)
plt.tight_layout()

# Save the plot to output folder
output_path = 'output/monthly_ticket_trends_by_technician.png'
plt.savefig(output_path)
plt.close()

output_path