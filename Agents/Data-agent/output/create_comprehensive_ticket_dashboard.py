import json
from dashboard_templates import (
    get_html_template, get_chart_js_template, get_stat_card_template, get_chart_card_template
)

# Data from queries

# KPI
kpi_total_tickets = 200000

# Monthly ticket trends for line chart
monthly_ticket_data = {
    'labels': [
        '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08', '2025-09'
    ],
    'values': [25337, 23124, 25481, 24589, 25590, 24624, 25899, 25310, 46]
}

# Ticket type distribution pie chart
ticket_type_data = {
    'labels': ['Change', 'Incident', 'Request'],
    'values': [66829, 66589, 66582]
}

# Category distribution bar chart
category_data = {
    'labels': [
        'Access', 'Network & Security', 'Account Management', 'Software', 'Hardware', 'Communication'
    ],
    'values': [33689, 33529, 33420, 33342, 33089, 32931]
}

# Create KPI cards
stat_card_template = get_stat_card_template()
kpi_cards_html = """
"""
kpi_cards_html += stat_card_template.replace('{{NUMBER}}', f'{kpi_total_tickets}').replace('{{LABEL}}', 'Total Tickets')

# Create charts JS
chart1_js = get_chart_js_template(
    'lineChart',
    'line',
    monthly_ticket_data['labels'],
    monthly_ticket_data['values'],
    'Monthly Ticket Trends'
)

chart2_js = get_chart_js_template(
    'pieChart',
    'pie',
    ticket_type_data['labels'],
    ticket_type_data['values'],
    'Ticket Type Distribution'
)

chart3_js = get_chart_js_template(
    'barChart',
    'bar',
    category_data['labels'],
    category_data['values'],
    'Ticket Category Distribution'
)

# Create chart cards
chart_card_template = get_chart_card_template()
chart1_html = chart_card_template.replace('{{CHART_TITLE}}', 'Monthly Ticket Trends').replace('{{CHART_ID}}', 'lineChart')
chart2_html = chart_card_template.replace('{{CHART_TITLE}}', 'Ticket Type Distribution').replace('{{CHART_ID}}', 'pieChart')
chart3_html = chart_card_template.replace('{{CHART_TITLE}}', 'Ticket Category Distribution').replace('{{CHART_ID}}', 'barChart')

charts_html = chart1_html + chart2_html + chart3_html

# Insights section
insights_html = """
<h3>Key Insights</h3>
<ul>
  <li>Total tickets handled: 200,000 across multiple categories and request types.</li>
  <li>Ticket volume shows variability month to month but generally consistent, with a drop-off in latest month data.</li>
  <li>Ticket types are evenly distributed, Change requests slightly outnumber others.</li>
  <li>Category distribution among tickets is also very balanced among the six main categories.</li>
</ul>
"""

# Final HTML template
html_template = get_html_template()
final_html = html_template.replace('{{STATS_CONTENT}}', kpi_cards_html)
final_html = final_html.replace('{{CHARTS_CONTENT}}', charts_html)
final_html = final_html.replace('{{INSIGHTS_CONTENT}}', insights_html)
final_html = final_html.replace('{{JAVASCRIPT_CONTENT}}', chart1_js + chart2_js + chart3_js)

# Save to output
output_path = 'output/comprehensive_ticket_dashboard.html'
with open(output_path, 'w') as f:
    f.write(final_html)

output_path