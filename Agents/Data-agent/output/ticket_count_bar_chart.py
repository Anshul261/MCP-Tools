import matplotlib.pyplot as plt
import pandas as pd

# Data from query result
data = {
    'Category': ['Access', 'Access', 'Access', 'Account Management', 'Account Management', 'Account Management', 'Communication', 'Communication', 'Communication', 'Hardware', 'Hardware', 'Hardware', 'Network & Security', 'Network & Security', 'Network & Security', 'Software', 'Software', 'Software'],
    'Priority': ['P1', 'P2', 'P3', 'P1', 'P2', 'P3', 'P1', 'P2', 'P3', 'P1', 'P2', 'P3', 'P1', 'P2', 'P3', 'P1', 'P2', 'P3'],
    'ticket_count': [14349, 6591, 12749, 14045, 6643, 12732, 13868, 6491, 12572, 14017, 6534, 12538, 14089, 6747, 12693, 14133, 6455, 12754]
}

df = pd.DataFrame(data)

# Pivot the data to get counts for each Category by Priority
pivot_df = df.pivot(index='Category', columns='Priority', values='ticket_count')

# Plotting
ax = pivot_df.plot(kind='bar', figsize=(12, 8), colormap='viridis')
ax.set_title('Count of Tickets for each Category grouped by Priority')
ax.set_xlabel('Category')
ax.set_ylabel('Count of Tickets')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Priority')
plt.tight_layout()
plt.savefig('output/ticket_count_by_category_priority_bar_chart.png', dpi=300)
plt.close()