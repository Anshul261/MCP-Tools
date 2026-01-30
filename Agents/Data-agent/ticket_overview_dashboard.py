from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template, get_chart_card_template

# Priority Data
priority_labels = ['P1', 'P3', 'P2']
priority_counts = [84501, 76038, 39461]

# Category Data
category_labels = ['Access', 'Network & Security', 'Account Management', 'Software', 'Hardware', 'Communication']
category_counts = [33689, 33529, 33420, 33342, 33089, 32931]

# Subcategory Data
subcategory_labels = [
    'Password reset', 'Account locked', 'VPN connectivity', 'Hardware failure', 'Software crash',
    'Data retrieval', 'Performance issue', 'Software installation error', 'Device onboarding', 'Email not syncing'
]
subcategory_counts = [20117, 20109, 20088, 20064, 20047, 19970, 19947, 19939, 19861, 19858]

# Monthly Ticket Trend Data
months = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08']
monthly_counts = [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]

# KPI values
total_tickets = 200000
unique_priorities = 3
unique_categories = 6
unique_subcategories = 10

html_template = get_html_template()
stat_card_template = get_stat_card_template()
chart_card_template = get_chart_card_template()

# Create KPI summary cards
stats_html = ''
stats_html += stat_card_template.replace('{{NUMBER}}', str(total_tickets)).replace('{{LABEL}}', 'Total Tickets')
stats_html += stat_card_template.replace('{{NUMBER}}', str(unique_priorities)).replace('{{LABEL}}', 'Unique Priorities')
stats_html += stat_card_template.replace('{{NUMBER}}', str(unique_categories)).replace('{{LABEL}}', 'Unique Categories')
stats_html += stat_card_template.replace('{{NUMBER}}', str(unique_subcategories)).replace('{{LABEL}}', 'Unique Subcategories')

# Create pie charts
priority_chart_js = get_chart_js_template('priorityChart', 'pie', priority_labels, priority_counts, 'Ticket Distribution by Priority')
category_chart_js = get_chart_js_template('categoryChart', 'pie', category_labels, category_counts, 'Ticket Distribution by Category')
subcategory_chart_js = get_chart_js_template('subcategoryChart', 'pie', subcategory_labels, subcategory_counts, 'Ticket Distribution by Subcategory')

# Create line chart for monthly trend
monthly_chart_js = get_chart_js_template('monthlyTrendChart', 'line', months, monthly_counts, 'Monthly Ticket Counts Over Time')

# Create chart containers
charts_html = ''
charts_html += chart_card_template.replace('{{CHART_TITLE}}', 'Ticket Distribution by Priority').replace('{{CHART_ID}}', 'priorityChart')
charts_html += chart_card_template.replace('{{CHART_TITLE}}', 'Ticket Distribution by Category').replace('{{CHART_ID}}', 'categoryChart')
charts_html += chart_card_template.replace('{{CHART_TITLE}}', 'Ticket Distribution by Subcategory').replace('{{CHART_ID}}', 'subcategoryChart')
charts_html += chart_card_template.replace('{{CHART_TITLE}}', 'Monthly Ticket Counts Over Time').replace('{{CHART_ID}}', 'monthlyTrendChart')

# Insights
insights_html = '''
<h3>Insights</h3>
<ul>
  <li>Total tickets handled: 200,000.</li>
  <li>Priority P1 tickets form the largest priority group with 42.3% of tickets.</li>
  <li>Categories are evenly distributed, each with approximately 5.5% to 6% of tickets.</li>
  <li>Subcategories show fairly even distribution with top 3 subcategories close in ticket count (about 20,000 tickets each).</li>
  <li>Monthly ticket volume remains consistent, with small fluctuations from 23,133 to 25,973 tickets per month.</li>
</ul>
'''

# Assemble final HTML
final_html = html_template.replace('{{STATS_CONTENT}}', stats_html).replace('{{CHARTS_CONTENT}}', charts_html).replace('{{INSIGHTS_CONTENT}}', insights_html).replace('{{JAVASCRIPT_CONTENT}}', priority_chart_js + category_chart_js + subcategory_chart_js + monthly_chart_js)

# Save to output folder
with open('output/ticket_overview_dashboard.html', 'w') as f:
    f.write(final_html)

result = 'Dashboard generated and saved as output/ticket_overview_dashboard.html'