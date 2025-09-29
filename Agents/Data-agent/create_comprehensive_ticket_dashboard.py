from dashboard_templates import get_html_template, get_stat_card_template, get_chart_card_template, get_chart_js_template, get_insight_template

# Data from queries
line_chart_data = {
    "labels": ["2025-01-01", "2025-02-01", "2025-03-01", "2025-04-01", "2025-05-01", "2025-06-01", "2025-07-01", "2025-08-01"],
    "data": [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]
}

pie_chart_data = {
    "labels": ["Change", "Incident", "Request"],
    "data": [66829, 66589, 66582]
}

bar_chart_data = {
    "labels": ["Access", "Account Management", "Hardware", "Software", "Network & Security", "Communication"],
    "data": [33689, 33420, 33089, 33342, 33529, 32931]
}


total_tickets = 200000

# Prepare KPI card HTML
stat_card_html = get_stat_card_template().replace("{{NUMBER}}", f"{total_tickets:,}").replace("{{LABEL}}", "Total Tickets")

# Prepare Chart cards HTML
line_chart_card = get_chart_card_template().replace("{{CHART_TITLE}}", "Monthly Ticket Trends Over Time").replace("{{CHART_ID}}", "lineChart")
pie_chart_card = get_chart_card_template().replace("{{CHART_TITLE}}", "Ticket Type Distribution").replace("{{CHART_ID}}", "pieChart")
bar_chart_card = get_chart_card_template().replace("{{CHART_TITLE}}", "Ticket Category Splits").replace("{{CHART_ID}}", "barChart")

charts_html = line_chart_card + pie_chart_card + bar_chart_card

# Prepare insights HTML
insight1 = get_insight_template().replace("{{INSIGHT_TITLE}}", "Trend Insight").replace("{{INSIGHT_TEXT}}", "Monthly ticket volume is relatively stable with a peak in July 2025.")
insight2 = get_insight_template().replace("{{INSIGHT_TITLE}}", "Type Distribution").replace("{{INSIGHT_TEXT}}", "Ticket types Change, Incident, and Request have nearly equal shares.")
insight3 = get_insight_template().replace("{{INSIGHT_TITLE}}", "Category Distribution").replace("{{INSIGHT_TEXT}}", "Ticket categories have close counts with Access highest and Communication lowest.")
insights_html = insight1 + insight2 + insight3

# Prepare JS for charts
line_chart_js = get_chart_js_template(
    chart_id="lineChart",
    chart_type="line",
    data_labels=line_chart_data["labels"],
    data_values=line_chart_data["data"],
    title="Monthly Ticket Trends"
)
pie_chart_js = get_chart_js_template(
    chart_id="pieChart",
    chart_type="pie",
    data_labels=pie_chart_data["labels"],
    data_values=pie_chart_data["data"],
    title="Ticket Type Distribution"
)
bar_chart_js = get_chart_js_template(
    chart_id="barChart",
    chart_type="bar",
    data_labels=bar_chart_data["labels"],
    data_values=bar_chart_data["data"],
    title="Ticket Category Splits"
)

# Compose final HTML by replacing placeholders
html_template = get_html_template()
html_filled = html_template.replace("{{STATS_CONTENT}}", stat_card_html)
html_filled = html_filled.replace("{{CHARTS_CONTENT}}", charts_html)
html_filled = html_filled.replace("{{INSIGHTS_CONTENT}}", insights_html)
js_content = line_chart_js + pie_chart_js + bar_chart_js
html_filled = html_filled.replace("{{JAVASCRIPT_CONTENT}}", js_content)

# Save the file to output
output_path = "output/comprehensive_ticket_dashboard.html"
with open(output_path, "w") as f:
    f.write(html_filled)

output_path