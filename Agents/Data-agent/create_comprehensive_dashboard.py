import json

# Import the dashboard templates
from dashboard_templates import get_html_template, get_stat_card_template, get_chart_card_template, get_insight_template, get_chart_js_template

# Data for dashboard charts and KPIs
category_data = [
    {"Category": "Access", "count": 33689},
    {"Category": "Network & Security", "count": 33529},
    {"Category": "Account Management", "count": 33420},
    {"Category": "Software", "count": 33342},
    {"Category": "Hardware", "count": 33089},
    {"Category": "Communication", "count": 32931}
]

subcategory_data = [
    {"Category": "Access", "Subcategory": "Performance issue", "count": 3462},
    {"Category": "Access", "Subcategory": "Software crash", "count": 3408},
    {"Category": "Access", "Subcategory": "VPN connectivity", "count": 3408},
    {"Category": "Access", "Subcategory": "Password reset", "count": 3395},
    {"Category": "Access", "Subcategory": "Hardware failure", "count": 3382},
    {"Category": "Access", "Subcategory": "Data retrieval", "count": 3375},
    {"Category": "Access", "Subcategory": "Email not syncing", "count": 3370},
    {"Category": "Access", "Subcategory": "Software installation error", "count": 3351},
    {"Category": "Access", "Subcategory": "Account locked", "count": 3289},
    {"Category": "Access", "Subcategory": "Device onboarding", "count": 3249},
    {"Category": "Account Management", "Subcategory": "Performance issue", "count": 3364},
    {"Category": "Account Management", "Subcategory": "Password reset", "count": 3362},
    {"Category": "Account Management", "Subcategory": "Account locked", "count": 3356},
    {"Category": "Account Management", "Subcategory": "Device onboarding", "count": 3353},
    {"Category": "Account Management", "Subcategory": "Data retrieval", "count": 3340},
    {"Category": "Account Management", "Subcategory": "Email not syncing", "count": 3340},
    {"Category": "Account Management", "Subcategory": "Hardware failure", "count": 3334},
    {"Category": "Account Management", "Subcategory": "Software crash", "count": 3333},
    {"Category": "Account Management", "Subcategory": "VPN connectivity", "count": 3333},
    {"Category": "Account Management", "Subcategory": "Software installation error", "count": 3305},
    {"Category": "Communication", "Subcategory": "Account locked", "count": 3454},
    {"Category": "Communication", "Subcategory": "VPN connectivity", "count": 3374},
    {"Category": "Communication", "Subcategory": "Software crash", "count": 3338},
    {"Category": "Communication", "Subcategory": "Data retrieval", "count": 3297},
    {"Category": "Communication", "Subcategory": "Password reset", "count": 3279},
    {"Category": "Communication", "Subcategory": "Email not syncing", "count": 3269},
    {"Category": "Communication", "Subcategory": "Device onboarding", "count": 3248},
    {"Category": "Communication", "Subcategory": "Performance issue", "count": 3244},
    {"Category": "Communication", "Subcategory": "Hardware failure", "count": 3231},
    {"Category": "Communication", "Subcategory": "Software installation error", "count": 3197},
    {"Category": "Hardware", "Subcategory": "Hardware failure", "count": 3473},
    {"Category": "Hardware", "Subcategory": "Data retrieval", "count": 3355},
    {"Category": "Hardware", "Subcategory": "Account locked", "count": 3340},
    {"Category": "Hardware", "Subcategory": "Software installation error", "count": 3331},
    {"Category": "Hardware", "Subcategory": "Password reset", "count": 3304},
    {"Category": "Hardware", "Subcategory": "Device onboarding", "count": 3285},
    {"Category": "Hardware", "Subcategory": "Software crash", "count": 3277},
    {"Category": "Hardware", "Subcategory": "Performance issue", "count": 3271},
    {"Category": "Hardware", "Subcategory": "Email not syncing", "count": 3238},
    {"Category": "Hardware", "Subcategory": "VPN connectivity", "count": 3215},
    {"Category": "Network & Security", "Subcategory": "Password reset", "count": 3441},
    {"Category": "Network & Security", "Subcategory": "VPN connectivity", "count": 3398},
    {"Category": "Network & Security", "Subcategory": "Software crash", "count": 3383},
    {"Category": "Network & Security", "Subcategory": "Device onboarding", "count": 3356},
    {"Category": "Network & Security", "Subcategory": "Software installation error", "count": 3354},
    {"Category": "Network & Security", "Subcategory": "Email not syncing", "count": 3349},
    {"Category": "Network & Security", "Subcategory": "Hardware failure", "count": 3337},
    {"Category": "Network & Security", "Subcategory": "Account locked", "count": 3337},
    {"Category": "Network & Security", "Subcategory": "Performance issue", "count": 3320},
    {"Category": "Network & Security", "Subcategory": "Data retrieval", "count": 3254},
    {"Category": "Software", "Subcategory": "Software installation error", "count": 3401},
    {"Category": "Software", "Subcategory": "Device onboarding", "count": 3370},
    {"Category": "Software", "Subcategory": "VPN connectivity", "count": 3360},
    {"Category": "Software", "Subcategory": "Data retrieval", "count": 3349},
    {"Category": "Software", "Subcategory": "Password reset", "count": 3336},
    {"Category": "Software", "Subcategory": "Account locked", "count": 3333},
    {"Category": "Software", "Subcategory": "Software crash", "count": 3308},
    {"Category": "Software", "Subcategory": "Hardware failure", "count": 3307},
    {"Category": "Software", "Subcategory": "Email not syncing", "count": 3292},
    {"Category": "Software", "Subcategory": "Performance issue", "count": 3286},
]

monthly_trends = [
    {"month": "2025-01", "count": 25373},
    {"month": "2025-02", "count": 23133},
    {"month": "2025-03", "count": 25472},
    {"month": "2025-04", "count": 24582},
    {"month": "2025-05", "count": 25597},
    {"month": "2025-06", "count": 24612},
    {"month": "2025-07", "count": 25903},
    {"month": "2025-08", "count": 25328}
]

total_tickets = 200000
unique_requesters = 155507
avg_resolution_days = 1.547

# Prepare data for category chart
category_labels = json.dumps([item['Category'] for item in category_data])
category_counts = json.dumps([item['count'] for item in category_data])

# Prepare data for monthly trends line chart
monthly_labels = json.dumps([item['month'] for item in monthly_trends])
monthly_counts = json.dumps([item['count'] for item in monthly_trends])

# Prepare subcategory data grouped by category
subcategory_categories = sorted(list(set([item['Category'] for item in subcategory_data])))
subcategory_subcats = sorted(list(set([item['Subcategory'] for item in subcategory_data])))

# Build dictionary: {subcat: [counts grouped by category index]}
subcategory_dict = {subcat: [0]*len(subcategory_categories) for subcat in subcategory_subcats}
for item in subcategory_data:
    cat_idx = subcategory_categories.index(item['Category'])
    subcategory_dict[item['Subcategory']][cat_idx] = item['count']

# Limit to first 10 subcategories for visual clarity
limited_subcats = subcategory_subcats[:10]

# Generate datasets for Chart.js stacked bar
colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#fd7e14', '#20c997', '#6f42c1', '#d63384']
datasets = []
for i, subcat in enumerate(limited_subcats):
    datasets.append({
        'label': subcat,
        'backgroundColor': colors[i],
        'data': subcategory_dict[subcat]
    })

# Convert datasets to JSON string
import json
datasets_json = json.dumps(datasets)
categories_json = json.dumps(subcategory_categories)

# Generate stat cards HTML
stat_cards_html = ''
stat_template = get_stat_card_template()

stat_cards = [
    {"NUMBER": f"{total_tickets:,}", "LABEL": "Total Tickets"},
    {"NUMBER": f"{unique_requesters:,}", "LABEL": "Unique Requesters"},
    {"NUMBER": f"{avg_resolution_days:.2f}", "LABEL": "Avg Resolution Days"}
]

for stat in stat_cards:
    card = stat_template.replace('{{NUMBER}}', stat['NUMBER']).replace('{{LABEL}}', stat['LABEL'])
    stat_cards_html += card

# Generate chart cards HTML
chart_template = get_chart_card_template()

category_chart_html = chart_template.replace('{{CHART_TITLE}}', 'Tickets by Category').replace('{{CHART_ID}}', 'ticketsCategory')
subcategory_chart_html = chart_template.replace('{{CHART_TITLE}}', 'Tickets by Subcategory (Top 10)').replace('{{CHART_ID}}', 'ticketsSubcategory')
monthly_chart_html = chart_template.replace('{{CHART_TITLE}}', 'Monthly Ticket Trend').replace('{{CHART_ID}}', 'ticketsMonthlyTrend')

# Insights
insight_template = get_insight_template()
insights = [
    {"INSIGHT_TITLE": "Total tickets handled", "INSIGHT_TEXT": f"{total_tickets:,} across {unique_requesters:,} unique requesters."},
    {"INSIGHT_TITLE": "Average resolution time", "INSIGHT_TEXT": f"Approximately {avg_resolution_days:.2f} days, indicating timely resolution."},
    {"INSIGHT_TITLE": "Dominant categories", "INSIGHT_TEXT": "Access and Network & Security have the highest ticket counts."},
    {"INSIGHT_TITLE": "Monthly trends", "INSIGHT_TEXT": "Ticket volumes show minor fluctuations but overall remain stable."},
    {"INSIGHT_TITLE": "Category issue distribution", "INSIGHT_TEXT": "Stacked bar chart reveals common issue distribution across categories."}
]
insights_html = ''
for i in insights:
    insights_html += insight_template.replace('{{INSIGHT_TITLE}}', i['INSIGHT_TITLE']).replace('{{INSIGHT_TEXT}}', i['INSIGHT_TEXT'])

# Chart JS Scripts
charts_js = f"""
{get_chart_js_template('ticketsCategory', 'bar', category_labels, category_counts, 'Tickets by Category')}

// Stacked bar requires custom code
const ctxSubcat = document.getElementById('ticketsSubcategory').getContext('2d');
const stackedBarChart = new Chart(ctxSubcat, {{
    type: 'bar',
    data: {{
        labels: {categories_json},
        datasets: {datasets_json}
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
            x: {{ stacked: true }},
            y: {{ stacked: true, beginAtZero: true }}
        }},
        plugins: {{
            legend: {{ position: 'bottom' }}
        }}
    }}
}});

{get_chart_js_template('ticketsMonthlyTrend', 'line', monthly_labels, monthly_counts, 'Monthly Ticket Trend')}
"""

# Final HTML
html_template = get_html_template()
final_html = html_template.replace('{{STATS_CONTENT}}', stat_cards_html)
final_html = final_html.replace('{{CHARTS_CONTENT}}', category_chart_html + subcategory_chart_html + monthly_chart_html)
final_html = final_html.replace('{{INSIGHTS_CONTENT}}', insights_html)
final_html = final_html.replace('{{JAVASCRIPT_CONTENT}}', charts_js)

# Save to output
with open('output/comprehensive_dashboard.html', 'w') as f:
    f.write(final_html)

'output/comprehensive_dashboard.html'