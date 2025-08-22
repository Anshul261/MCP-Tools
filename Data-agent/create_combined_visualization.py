import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd

# Data from queries
sla_data = {
    "SLA_Violated": [False, True],
    "Ticket_Count": [4341, 128]
}
category_data = {
    "Category": ["Microsoft", "Reports", "End User Support", "Systems", "Information Security", "Microsoft", "Patch Management", "Network & Security", "End User Support", "Information Security", "End User Support", "End User Support", "Microsoft", "Information Security", "End User Support"],
    "Subcategory": ["Email Administration", "General", "Hardware", "Server", "Data Security", "O365", "Patch Deployment", "Firewall", "Laptops/Monitors/ Accessories", "Email Security", "Software", "Admin Access", "Email Creation/Modification", "Web Security", "Install / Uninstall"],
    "Ticket_Count": [1040, 1019, 240, 229, 158, 154, 124, 122, 103, 101, 95, 92, 90, 81, 78]
}
monthly_data = {
    "Month": ["2025-01", "2025-02", "2025-03", "2025-04"],
    "Ticket_Count": [1071, 1033, 1127, 1169]
}

# Convert to DataFrames
sla_df = pd.DataFrame(sla_data)
category_df = pd.DataFrame(category_data)
monthly_df = pd.DataFrame(monthly_data)

# Insights text
insights = """
Key Insights from Support Ticket Analysis (Jan-Apr 2025):

1. SLA Compliance:
- The overwhelming majority of support tickets (4341 out of 4469) met SLA deadlines, indicating strong SLA adherence.
- Only a small fraction (128 tickets) experienced overdue status indicating SLA violations.

2. Category and Subcategory Trends:
- Microsoft related tickets, especially for Email Administration and O365, dominate the ticket volume.
- The Reports category with a focus on General subcategory is also significant.
- End User Support spans multiple subcategories such as Hardware and Software showing broad user assistance needs.

3. Time-based Ticket Volume Trends:
- Ticket volumes steadily increased from January to April 2025.
- April saw the highest volume (1169 tickets), showing a rising demand for support services.
"""

# Create subplot figure for all charts, specify 'domain' type for pie chart
fig = sp.make_subplots(
    rows=3, cols=1,
    specs=[[{'type':'domain'}], [{'type':'xy'}], [{'type':'xy'}]],
    subplot_titles=("SLA Violation Status", "Top Categories and Subcategories by Ticket Volume", "Monthly Ticket Volume Trend (Jan-Apr 2025)"),
    vertical_spacing=0.15
)

# SLA Violation Pie Chart
fig.add_trace(go.Pie(
    labels=['SLA Met', 'SLA Violated'],
    values=sla_df['Ticket_Count'],
    hole=0.4,
    marker_colors=['#2ca02c', '#d62728'],
    textinfo='label+percent',
    name='SLA Status'
), row=1, col=1)

# Bar Chart for Category/Subcategory
fig.add_trace(go.Bar(
    x=category_df['Ticket_Count'],
    y=category_df['Category'] + " - " + category_df['Subcategory'],
    orientation='h',
    marker_color='#1f77b4'
), row=2, col=1)

# Line Chart for Monthly Ticket Volume
fig.add_trace(go.Scatter(
    x=monthly_df['Month'],
    y=monthly_df['Ticket_Count'],
    mode='lines+markers',
    line=dict(color='#ff7f0e', width=3),
    marker=dict(size=8),
    name='Tickets per Month'
), row=3, col=1)

# Update layout
fig.update_layout(
    height=900,
    showlegend=True,
    title_text="Support Ticket Trend Analysis and SLA Compliance (Jan-Apr 2025)",
    title_x=0.5,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial", size=12),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="center",
        x=0.5
    )
)

# Update yaxis for bar chart
fig.update_yaxes(
    categoryorder='total ascending',
    row=2, col=1
)

# Add insights annotation below all plots
fig.add_annotation(
    text=insights.replace('\n', '<br>'),
    xref='paper', yref='paper',
    x=0, y=-0.15,
    showarrow=False,
    align='left',
    font=dict(size=12),
    bordercolor='black',
    borderwidth=1,
    borderpad=10,
    bgcolor='white'
)

# Save as single html file
output_path = "output/support_ticket_analysis_combined.html"
fig.write_html(output_path)

output_path