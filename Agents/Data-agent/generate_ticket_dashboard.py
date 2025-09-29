from dashboard_templates import get_html_template, get_chart_js_template, get_stat_card_template, get_chart_card_template, get_insight_template
import json

# Data from queries
monthly_ticket_trends = {
    "labels": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08"],
    "data": [25373, 23133, 25472, 24582, 25597, 24612, 25903, 25328]
}

request_type_distribution = {
    "labels": ["Request", "Change", "Incident"],
    "data": [66582, 66829, 66589]
}

sla_violation_distribution = {
    "labels": ["Violated", "Not Violated"],
    "data": [69668, 130332]
}

sla_name_distribution = {
    "labels": ["High SLA", "Low SLA", "Medium SLA"],
    "data": [66809, 66740, 66451]
}

summary_stats = {
    "total_tickets": 200000,
    "open_tickets": 9924,
    "resolved_tickets": 100082,
    "closed_tickets": 69890,
    "in_progress_tickets": 20104,
    "avg_resolution_hours": 37.12
}

html_template = get_html_template()
stat_card_template = get_stat_card_template()
chart_card_template = get_chart_card_template()
insight_template = get_insight_template()

# KPI Cards HTML
stats_html = ""
stats_html += stat_card_template.replace("{{NUMBER}}", str(summary_stats['total_tickets'])).replace("{{LABEL}}", "Total Tickets")
stats_html += stat_card_template.replace("{{NUMBER}}", str(summary_stats['open_tickets'])).replace("{{LABEL}}", "Open Tickets")
stats_html += stat_card_template.replace("{{NUMBER}}", str(summary_stats['resolved_tickets'])).replace("{{LABEL}}", "Resolved Tickets")
stats_html += stat_card_template.replace("{{NUMBER}}", str(summary_stats['closed_tickets'])).replace("{{LABEL}}", "Closed Tickets")
stats_html += stat_card_template.replace("{{NUMBER}}", str(summary_stats['in_progress_tickets'])).replace("{{LABEL}}", "In Progress Tickets")
stats_html += stat_card_template.replace("{{NUMBER}}", f"{summary_stats['avg_resolution_hours']:.2f} hours").replace("{{LABEL}}", "Avg Resolution Time")

# Charts HTML
line_chart_html = chart_card_template.replace("{{CHART_TITLE}}", "Monthly Ticket Trends Over Time").replace("{{CHART_ID}}", "lineChart")
bar_chart_request_type_html = chart_card_template.replace("{{CHART_TITLE}}", "Ticket Type Distribution").replace("{{CHART_ID}}", "barChartRequestType")
pie_chart_sla_violation_html = chart_card_template.replace("{{CHART_TITLE}}", "SLA Violation Status").replace("{{CHART_ID}}", "pieChartSlaViolation")
bar_chart_sla_name_html = chart_card_template.replace("{{CHART_TITLE}}", "SLA Name Distribution").replace("{{CHART_ID}}", "barChartSlaName")

charts_html = line_chart_html + bar_chart_request_type_html + pie_chart_sla_violation_html + bar_chart_sla_name_html

# Insights HTML
insights = []
insights.append(insight_template.replace("{{INSIGHT_TITLE}}", "Monthly Ticket Volume").replace("{{INSIGHT_TEXT}}", f"Ticket counts per month shows a consistent range between {min(monthly_ticket_trends['data'])} and {max(monthly_ticket_trends['data'])} tickets."))
insights.append(insight_template.replace("{{INSIGHT_TITLE}}", "Ticket Type Distribution").replace("{{INSIGHT_TEXT}}", f"Request, Change, and Incident are almost evenly distributed across the dataset."))
sla_violated_pct = summary_stats['total_tickets'] and (69668 / summary_stats['total_tickets']) * 100
insights.append(insight_template.replace("{{INSIGHT_TITLE}}", "SLA Violation Overview").replace("{{INSIGHT_TEXT}}", f"Approximately {sla_violated_pct:.2f}% of tickets have SLA violations."))
insights.append(insight_template.replace("{{INSIGHT_TITLE}}", "SLA Names").replace("{{INSIGHT_TEXT}}", f"High, Low, and Medium SLAs are nearly evenly distributed with around 66k tickets each."))
insights.append(insight_template.replace("{{INSIGHT_TITLE}}", "Ticket Status Summary").replace("{{INSIGHT_TEXT}}", f"Tickets have varied statuses with a majority being Resolved ({summary_stats['resolved_tickets']}) and Closed ({summary_stats['closed_tickets']})."))

insights_html = "".join(insights)

# Compose final HTML by replacing placeholders
final_html = html_template.replace("{{STATS_CONTENT}}", stats_html).replace("{{CHARTS_CONTENT}}", charts_html).replace("{{INSIGHTS_CONTENT}}", insights_html)

# Chart.js JS code string
line_chart_js = get_chart_js_template(
    "lineChart",
    "line",
    json.dumps(monthly_ticket_trends['labels']),
    json.dumps(monthly_ticket_trends['data']),
    "Monthly Tickets"
)

bar_chart_request_type_js = get_chart_js_template(
    "barChartRequestType",
    "bar",
    json.dumps(request_type_distribution['labels']),
    json.dumps(request_type_distribution['data']),
    "Ticket Type Count"
)

pie_chart_sla_violation_js = get_chart_js_template(
    "pieChartSlaViolation",
    "pie",
    json.dumps(sla_violation_distribution['labels']),
    json.dumps(sla_violation_distribution['data']),
    "SLA Violation Status"
)

bar_chart_sla_name_js = get_chart_js_template(
    "barChartSlaName",
    "bar",
    json.dumps(sla_name_distribution['labels']),
    json.dumps(sla_name_distribution['data']),
    "SLA Name Count"
)

all_charts_js = line_chart_js + bar_chart_request_type_js + pie_chart_sla_violation_js + bar_chart_sla_name_js

final_html = final_html.replace("{{JAVASCRIPT_CONTENT}}", all_charts_js)

# Write to file
output_file = "output/comprehensive_ticket_dashboard.html"
with open(output_file, "w") as f:
    f.write(final_html)

output_file