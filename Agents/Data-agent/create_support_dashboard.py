import json
from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template

# Data for dashboard
monthly_ticket_volume = {
    'labels': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06', '2025-07', '2025-08'],
    'data': [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]
}

category_subcategory_data = [
    {"category": "Hardware", "subcategory": "Hardware failure", "count": 3473},
    {"category": "Access", "subcategory": "Performance issue", "count": 3462},
    {"category": "Communication", "subcategory": "Account locked", "count": 3454},
    {"category": "Network & Security", "subcategory": "Password reset", "count": 3441},
    {"category": "Access", "subcategory": "Software crash", "count": 3408},
    {"category": "Access", "subcategory": "VPN connectivity", "count": 3408},
    {"category": "Software", "subcategory": "Software installation error", "count": 3401},
    {"category": "Network & Security", "subcategory": "VPN connectivity", "count": 3398},
    {"category": "Access", "subcategory": "Password reset", "count": 3395},
    {"category": "Network & Security", "subcategory": "Software crash", "count": 3383}
]

status_distribution = {
    'labels': ['Open', 'Resolved', 'Closed', 'In Progress'],
    'data': [9924, 100082, 69890, 20104]
}

priority_distribution = {
    'labels': ['P1', 'P3', 'P2'],
    'data': [84501, 76038, 39461]
}

top_groups = {
    'labels': ['Application Support', 'Security', 'Network Support', 'Desktop Support', 'Infrastructure'],
    'data': [40283, 40107, 39953, 39872, 39785]
}

# KPI cards values
kpi_cards = {
    'total_tickets': 200000,
    'resolved_tickets': 100082,
    'high_priority_tickets': 84501,
    'highest_sla_violated_tech': 'Not Assigned',
    'highest_sla_violations': 147809
}

# Build HTML content
html_template = get_html_template()
stat_card_template = get_stat_card_template()

# Prepare data and charts for embedding

# 1) Monthly ticket volume line chart
line_chart_data = {
    'labels': monthly_ticket_volume['labels'],
    'datasets': [{
        'label': 'Monthly Ticket Volume',
        'data': monthly_ticket_volume['data'],
        'borderColor': 'rgba(54, 162, 235, 1)',
        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
        'fill': True,
        'tension': 0.4
    }]
}

# 2) Category and Subcategory breakdown as stacked bar chart
unique_categories = list(sorted(set(item['category'] for item in category_subcategory_data)))
unique_subcategories = list(sorted(set(item['subcategory'] for item in category_subcategory_data)))

category_sub_map = {cat: {} for cat in unique_categories}
for item in category_subcategory_data:
    category_sub_map[item['category']][item['subcategory']] = item['count']

subcategories_sorted = sorted(unique_subcategories)[:5]  # Limit to top 5 for clarity

datasets_grouped_bar = []
color_palette = [
    'rgba(255, 99, 132, 0.7)',
    'rgba(54, 162, 235, 0.7)',
    'rgba(255, 206, 86, 0.7)',
    'rgba(75, 192, 192, 0.7)',
    'rgba(153, 102, 255, 0.7)'
]

for idx, cat in enumerate(unique_categories):
    data_array = []
    for subcat in subcategories_sorted:
        count = category_sub_map.get(cat, {}).get(subcat, 0)
        data_array.append(count)
    datasets_grouped_bar.append({
        'label': cat,
        'data': data_array,
        'backgroundColor': color_palette[idx % len(color_palette)],
        'stack': 'stack1'
    })

category_subcategory_chart_data = {
    'labels': subcategories_sorted,
    'datasets': datasets_grouped_bar
}

# 3) Ticket status distribution pie chart
status_distribution_data = {
    'labels': status_distribution['labels'],
    'datasets': [{
        'label': 'Ticket Status Distribution',
        'data': status_distribution['data'],
        'backgroundColor': [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)'
        ]
    }]
}

# 4) Ticket priority distribution bar chart
priority_distribution_data = {
    'labels': priority_distribution['labels'],
    'datasets': [{
        'label': 'Ticket Priority Distribution',
        'data': priority_distribution['data'],
        'backgroundColor': [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)'
        ]
    }]
}

# 5) Top groups by number of tickets handled bar chart
top_groups_data = {
    'labels': top_groups['labels'],
    'datasets': [{
        'label': 'Tickets Handled',
        'data': top_groups['data'],
        'backgroundColor': 'rgba(75, 192, 192, 0.7)'
    }]
}

# Function to convert Python dict to JSON string for JS embedding
def to_json(data):
    return json.dumps(data)

# Generate Chart.js scripts for each chart
line_chart_js = get_chart_js_template('monthlyTicketVolume', 'line', json.dumps(line_chart_data['labels']), json.dumps(line_chart_data['datasets'][0]['data']))

category_subcategory_js = get_chart_js_template('categorySubcategory', 'bar', json.dumps(category_subcategory_chart_data['labels']), json.dumps([ds['data'] for ds in category_subcategory_chart_data['datasets']]))

status_distribution_js = get_chart_js_template('statusDistribution', 'doughnut', json.dumps(status_distribution_data['labels']), json.dumps(status_distribution_data['datasets'][0]['data']))

priority_distribution_js = get_chart_js_template('priorityDistribution', 'bar', json.dumps(priority_distribution_data['labels']), json.dumps(priority_distribution_data['datasets'][0]['data']))

top_groups_js = get_chart_js_template('topGroups', 'bar', json.dumps(top_groups_data['labels']), json.dumps(top_groups_data['datasets'][0]['data']))

chart_js_script = f"""
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
{line_chart_js}
{category_subcategory_js}
{status_distribution_js}
{priority_distribution_js}
{top_groups_js}
</script>
"""

# Stat cards HTML
stat_cards_html = ""
stat_cards_html += stat_card_template.replace("{{TITLE}}", "Total Tickets").replace("{{VALUE}}", str(kpi_cards['total_tickets']))
stat_cards_html += stat_card_template.replace("{{TITLE}}", "Resolved Tickets").replace("{{VALUE}}", str(kpi_cards['resolved_tickets']))
stat_cards_html += stat_card_template.replace("{{TITLE}}", "High Priority Tickets (P1)").replace("{{VALUE}}", str(kpi_cards['high_priority_tickets']))
stat_cards_html += stat_card_template.replace("{{TITLE}}", "Highest SLA Violated Technician").replace("{{VALUE}}", f"{kpi_cards['highest_sla_violated_tech']} ({kpi_cards['highest_sla_violations']})")

html_content = html_template.replace("{{TITLE}}", "Support Data Comprehensive Dashboard")
html_content = html_content.replace("{{STAT_CARDS}}", stat_cards_html)

charts_html = '''
<div class="chart-container"><canvas id="monthlyTicketVolume"></canvas></div>
<div class="chart-container"><canvas id="categorySubcategory"></canvas></div>
<div class="chart-container"><canvas id="statusDistribution"></canvas></div>
<div class="chart-container"><canvas id="priorityDistribution"></canvas></div>
<div class="chart-container"><canvas id="topGroups"></canvas></div>
'''
html_content = html_content.replace("{{CHARTS}}", charts_html)

html_content += chart_js_script

# Save to output folder
with open('output/support_data_comprehensive_dashboard.html', 'w') as f:
    f.write(html_content)

"support_data_comprehensive_dashboard.html created successfully."