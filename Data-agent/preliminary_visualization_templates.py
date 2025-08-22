import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np

# Monthly ticket volumes - placeholder data
dates_monthly = pd.date_range(start='2023-01-01', periods=12, freq='M')
monthly_volumes = np.random.randint(100, 500, size=12)

fig_monthly = go.Figure()
fig_monthly.add_trace(go.Scatter(x=dates_monthly, y=monthly_volumes, mode='lines+markers', name='Monthly Tickets'))
fig_monthly.update_layout(title='Monthly Ticket Volumes (Placeholder)', xaxis_title='Month', yaxis_title='Number of Tickets', template='plotly_white')
fig_monthly.write_html('output/monthly_ticket_volumes.html')

# Daily ticket volumes - placeholder data
dates_daily = pd.date_range(start='2023-06-01', periods=30, freq='D')
daily_volumes = np.random.randint(10, 50, size=30)

fig_daily = go.Figure()
fig_daily.add_trace(go.Scatter(x=dates_daily, y=daily_volumes, mode='lines+markers', name='Daily Tickets'))
fig_daily.update_layout(title='Daily Ticket Volumes (Placeholder)', xaxis_title='Date', yaxis_title='Number of Tickets', template='plotly_white')
fig_daily.write_html('output/daily_ticket_volumes.html')

# Category and Subcategory counts - placeholder data
categories = ['Software', 'Hardware', 'Network', 'Other']
subcategories = ['Bug', 'Request', 'Installation', 'Maintenance']
category_counts = np.random.randint(50, 200, size=len(categories))
subcategory_counts = np.random.randint(20, 150, size=len(subcategories))

fig_cat = sp.make_subplots(rows=1, cols=2, subplot_titles=('Category Counts', 'Subcategory Counts'))

# Category bar chart
fig_cat.add_trace(go.Bar(x=categories, y=category_counts, marker_color='indianred'), row=1, col=1)

# Subcategory bar chart
fig_cat.add_trace(go.Bar(x=subcategories, y=subcategory_counts, marker_color='lightsalmon'), row=1, col=2)

fig_cat.update_layout(title_text='Ticket Counts by Category and Subcategory (Placeholder)', showlegend=False, template='plotly_white')
fig_cat.write_html('output/category_subcategory_counts.html')

""" 
Preliminary visualization templates created:
- output/monthly_ticket_volumes.html
- output/daily_ticket_volumes.html
- output/category_subcategory_counts.html

These can be updated easily with real data once available.
"""