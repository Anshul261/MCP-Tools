import os
from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template, get_chart_card_template

# Data from queries
total_tickets = 200000

# Monthly ticket counts
months = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08']
monthly_counts = [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]

# Ticket type distribution
ticket_types = ['Incident', 'Request', 'Change']
ticket_type_counts = [66589, 66582, 66829]

# Ticket category splits
categories = ['Access', 'Account Management', 'Hardware', 'Communication', 'Software', 'Network & Security']
category_counts = [33689, 33420, 33089, 32931, 33342, 33529]

# Prepare KPI cards HTML
stat_card_template = get_stat_card_template()
total_tickets_card = stat_card_template.replace('{{NUMBER}}', f'{total_tickets}').replace('{{LABEL}}', 'Total Tickets')

# Create the charts with Chart.js templates
line_chart_js = get_chart_js_template('lineChart', 'line', months, monthly_counts, 'Monthly Ticket Trends')
pie_chart_js = get_chart_js_template('pieChart', 'pie', ticket_types, ticket_type_counts, 'Ticket Type Distribution')
bar_chart_js = get_chart_js_template('barChart', 'bar', categories, category_counts, 'Ticket Category Splits')

# Create chart containers using chart_card_template
chart_card_template = get_chart_card_template()
line_chart_card = chart_card_template.replace('{{CHART_TITLE}}', 'Monthly Ticket Trends').replace('{{CHART_ID}}', 'lineChart')
pie_chart_card = chart_card_template.replace('{{CHART_TITLE}}', 'Ticket Type Distribution').replace('{{CHART_ID}}', 'pieChart')
bar_chart_card = chart_card_template.replace('{{CHART_TITLE}}', 'Ticket Category Splits').replace('{{CHART_ID}}', 'barChart')

# Prepare insights content
insights_content = '''<ul>
<li>Steady monthly ticket volumes, fluctuating between ~23,100 and ~26,000 tickets monthly.</li>
<li>Ticket types are almost evenly distributed among Incident, Request, and Change categories.</li>
<li>Categories are balanced with Access and Network & Security slightly leading.</li>
</ul>'''

# Compose final HTML
html_template = get_html_template()
final_html = html_template.replace(
    '{{STATS_CONTENT}}', total_tickets_card
).replace(
    '{{CHARTS_CONTENT}}', line_chart_card + pie_chart_card + bar_chart_card
).replace(
    '{{INSIGHTS_CONTENT}}', insights_content
).replace(
    '{{JAVASCRIPT_CONTENT}}', line_chart_js + pie_chart_js + bar_chart_js
)

# Save file
output_folder = 'output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
filepath = os.path.join(output_folder, 'ticket_dashboard.html')
with open(filepath, 'w') as f:
    f.write(final_html)

result = f'Successfully created dashboard at {filepath}'