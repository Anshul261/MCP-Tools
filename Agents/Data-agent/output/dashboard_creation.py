from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template, get_chart_card_template

# Data for visualizations
monthly_data = {
    'labels': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08'],
    'values': [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]
}

total_tickets = 200000

category_data = {
    'labels': ['Access', 'Network & Security', 'Account Management', 'Software', 'Hardware', 'Communication'],
    'values': [33689, 33529, 33420, 33342, 33089, 32931]
}

request_type_data = {
    'labels': ['Change', 'Incident', 'Request'],
    'values': [66829, 66589, 66582]
}

# Generate stat card HTML
kpi_card_html = get_stat_card_template().replace('{{NUMBER}}', str(total_tickets)).replace('{{LABEL}}', 'Total Tickets')

# Generate chart HTML containers
monthly_chart_html = get_chart_card_template().replace('{{CHART_TITLE}}', 'Monthly Ticket Volume Trend').replace('{{CHART_ID}}', 'chartMonthly')
category_chart_html = get_chart_card_template().replace('{{CHART_TITLE}}', 'Category-wise Ticket Distribution').replace('{{CHART_ID}}', 'chartCategory')
request_type_chart_html = get_chart_card_template().replace('{{CHART_TITLE}}', 'Request Type-wise Ticket Distribution').replace('{{CHART_ID}}', 'chartRequestType')

# Generate Chart.js scripts
monthly_chart_js = get_chart_js_template(
    chart_id='chartMonthly',
    chart_type='line',
    data_labels=monthly_data['labels'],
    data_values=monthly_data['values'],
    title='Monthly Ticket Volume'
)

category_chart_js = get_chart_js_template(
    chart_id='chartCategory',
    chart_type='bar',
    data_labels=category_data['labels'],
    data_values=category_data['values'],
    title='Tickets by Category'
)

request_type_chart_js = get_chart_js_template(
    chart_id='chartRequestType',
    chart_type='doughnut',
    data_labels=request_type_data['labels'],
    data_values=request_type_data['values'],
    title='Tickets by Request Type'
)

# Insights HTML
insights_html = '''<ul>
<li>Maximum monthly ticket volume was {} in July 2025.</li>
<li>'Access' category has the highest ticket volume with {} tickets.</li>
<li>Request types 'Change', 'Incident', and 'Request' are almost evenly distributed.</li>
</ul>'''.format(max(monthly_data['values']), category_data['values'][0])

# Assemble entire HTML
base_html = get_html_template()
full_html = base_html.replace('{{STATS_CONTENT}}', kpi_card_html)
full_html = full_html.replace('{{CHARTS_CONTENT}}', monthly_chart_html + category_chart_html + request_type_chart_html)
full_html = full_html.replace('{{INSIGHTS_CONTENT}}', insights_html)
full_html = full_html.replace('{{JAVASCRIPT_CONTENT}}', monthly_chart_js + category_chart_js + request_type_chart_js)

# Save to output file
output_path = 'output/ticket_volume_dashboard.html'
with open(output_path, 'w') as file:
    file.write(full_html)

output_path