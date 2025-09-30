import json
from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template

# Data from queries
monthly_data = {
    "labels": ["Jan 2025", "Feb 2025", "Mar 2025", "Apr 2025", "May 2025", "Jun 2025", "Jul 2025", "Aug 2025"],
    "values": [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]
}
ticket_type_data = {
    "labels": ["Incident", "Change", "Request"],
    "values": [66589, 66829, 66582]
}
ticket_category_data = {
    "labels": ["Access", "Account Management", "Hardware", "Software", "Communication", "Network & Security"],
    "values": [33689, 33420, 33089, 33342, 32931, 33529]
}
kpis = {
    "total_tickets": 200000,
    "unique_ticket_types": 3,
    "unique_ticket_categories": 6
}

html_template = get_html_template()
stat_card_template = get_stat_card_template()

# Create KPI cards
stats_html = ""
stats_html += stat_card_template.replace('{{NUMBER}}', f'{kpis["total_tickets"]}').replace('{{LABEL}}', 'Total Tickets')
stats_html += stat_card_template.replace('{{NUMBER}}', f'{kpis["unique_ticket_types"]}').replace('{{LABEL}}', 'Unique Ticket Types')
stats_html += stat_card_template.replace('{{NUMBER}}', f'{kpis["unique_ticket_categories"]}').replace('{{LABEL}}', 'Unique Ticket Categories')

# Create charts

# Line chart - Monthly Ticket Volumes
chart1_js = get_chart_js_template(
    'chart1', 'line', monthly_data['labels'], monthly_data['values'], 'Monthly Ticket Volumes Over Time'
)

# Pie chart - Ticket Type Distribution
chart2_js = get_chart_js_template(
    'chart2', 'pie', ticket_type_data['labels'], ticket_type_data['values'], 'Ticket Type Distribution'
)

# Pie chart - Ticket Category Splits
chart3_js = get_chart_js_template(
    'chart3', 'pie', ticket_category_data['labels'], ticket_category_data['values'], 'Ticket Category Distribution'
)

# Insights
insights_html = """
<h3>Insights</h3>
<ul>
<li>The total number of tickets processed is 200,000 across the dataset.</li>
<li>Ticket volumes show slight monthly fluctuations with peaks in July and May 2025.</li>
<li>Ticket types are evenly distributed across Incident, Change, and Request types.</li>
<li>Ticket categories are fairly balanced with each category contributing approximately 16-17% of tickets.</li>
</ul>
"""

# Compose final html
final_html = html_template.replace('{{STATS_CONTENT}}', stats_html)
final_html = final_html.replace('{{CHARTS_CONTENT}}',
                                f'<canvas id="chart1"></canvas><canvas id="chart2"></canvas><canvas id="chart3"></canvas>')
final_html = final_html.replace('{{INSIGHTS_CONTENT}}', insights_html)

final_html = final_html.replace('{{JAVASCRIPT_CONTENT}}',
                                chart1_js + '\n' + chart2_js + '\n' + chart3_js)

# Save to file
output_path = 'output/comprehensive_ticket_dashboard.html'
with open(output_path, 'w') as f:
    f.write(final_html)

output_path