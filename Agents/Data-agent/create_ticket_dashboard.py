import pandas as pd
from datetime import datetime
import json

# Data preparation
monthly_tickets_data = {
    'Month': [datetime(2025, m, 1).strftime('%Y-%m') for m in range(1, 13)],
    'Ticket_Count': [120, 135, 150, 175, 160, 145, 155, 165, 170, 180, 190, 200]
}

request_type_data = {
    'Request_Type': ['Bug', 'Feature Request', 'Support', 'Inquiry'],
    'Ticket_Count': [300, 150, 350, 100]
}

category_data = {
    'Category': ['Software', 'Hardware', 'Network', 'Other'],
    'Ticket_Count': [400, 200, 180, 120]
}

monthly_tickets_df = pd.DataFrame(monthly_tickets_data)
request_type_df = pd.DataFrame(request_type_data)
category_df = pd.DataFrame(category_data)

total_tickets = monthly_tickets_df['Ticket_Count'].sum()
most_common_request = request_type_df.loc[request_type_df['Ticket_Count'].idxmax(), 'Request_Type']
most_common_category = category_df.loc[category_df['Ticket_Count'].idxmax(), 'Category']

# Prepare JSON strings for Chart.js data insertion
months_json = json.dumps(monthly_tickets_df['Month'].tolist())
ticket_counts_json = json.dumps(monthly_tickets_df['Ticket_Count'].tolist())
request_types_json = json.dumps(request_type_df['Request_Type'].tolist())
request_type_counts_json = json.dumps(request_type_df['Ticket_Count'].tolist())
categories_json = json.dumps(category_df['Category'].tolist())
category_counts_json = json.dumps(category_df['Ticket_Count'].tolist())

html_template = f'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comprehensive Ticket Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f7f9fc; }}
  h1 {{ text-align: center; color: #333; }}
  .dashboard {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; max-width: 1200px; margin: auto; }}
  .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 20px; }}
  .kpi {{ display: flex; justify-content: space-around; margin-bottom: 40px; max-width: 1200px; margin-left: auto; margin-right: auto; }}
  .kpi-card {{ background: #007bff; color: white; border-radius: 8px; padding: 20px; width: 30%; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.15);}}
  .kpi-card h2 {{ margin: 0 0 10px; font-size: 2.5em; }}
  .kpi-card p {{ margin: 0; font-weight: bold; font-size: 1.1em; }}
  .insights {{ max-width: 1200px; margin: 30px auto; background: #e9ecef; padding: 20px; border-radius: 8px; }}
  canvas {{ background: #fff; border-radius: 8px; }}
</style>
</head>
<body>
<h1>Comprehensive Ticket Dashboard - 2025</h1>

<div class="kpi">
  <div class="kpi-card">
    <h2>{total_tickets}</h2>
    <p>Total Tickets in 2025</p>
  </div>
  <div class="kpi-card">
    <h2>{most_common_request}</h2>
    <p>Most Common Request Type</p>
  </div>
  <div class="kpi-card">
    <h2>{most_common_category}</h2>
    <p>Most Common Category</p>
  </div>
</div>

<div class="dashboard">
  <div class="card">
    <h3>Monthly Ticket Trend (Line + Bar Chart)</h3>
    <canvas id="monthlyTrendChart"></canvas>
  </div>
  <div class="card">
    <h3>Ticket Distribution by Request Type</h3>
    <canvas id="requestTypeChart"></canvas>
  </div>
  <div class="card">
    <h3>Ticket Counts by Category</h3>
    <canvas id="categoryChart"></canvas>
  </div>
</div>

<div class="insights">
  <h3>Insights</h3>
  <ul>
    <li>Total tickets handled in 2025 amount to {total_tickets}.</li>
    <li>The most frequent request type was <strong>{most_common_request}</strong>, indicating a high volume of {most_common_request.lower()} related queries.</li>
    <li>The category with the highest tickets was <strong>{most_common_category}</strong>, showing focus area in this domain.</li>
  </ul>
</div>

<script>
const ctxMonthly = document.getElementById('monthlyTrendChart').getContext('2d');
const monthlyTrendChart = new Chart(ctxMonthly, {{
    type: 'bar',
    data: {{
        labels: {months_json},
        datasets: [
            {{
                type: 'line',
                label: 'Ticket Count (Line)',
                data: {ticket_counts_json},
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                yAxisID: 'y',
                tension: 0.3
            }},
            {{
                type: 'bar',
                label: 'Ticket Count (Bar)',
                data: {ticket_counts_json},
                backgroundColor: 'rgba(75, 192, 192, 0.7)',
                yAxisID: 'y'
            }}
        ]
    }},
    options: {{
        scales: {{
            y: {{
                beginAtZero: true,
                title: {{
                    display: true,
                    text: 'Tickets'
                }}
            }}
        }},
        plugins: {{
            legend: {{ position: 'top' }},
            tooltip: {{ enabled: true }}
        }}
    }}
}});

const ctxRequest = document.getElementById('requestTypeChart').getContext('2d');
const requestTypeChart = new Chart(ctxRequest, {{
    type: 'pie',
    data: {{
        labels: {request_types_json},
        datasets: [{{
            data: {request_type_counts_json},
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#8A2BE2'
            ]
        }}]
    }},
    options: {{
        plugins: {{
            legend: {{ position: 'right' }},
            tooltip: {{ enabled: true }}
        }}
    }}
}});

const ctxCategory = document.getElementById('categoryChart').getContext('2d');
const categoryChart = new Chart(ctxCategory, {{
    type: 'bar',
    data: {{
        labels: {categories_json},
        datasets: [{{
            label: 'Ticket Counts',
            data: {category_counts_json},
            backgroundColor: 'rgba(255, 159, 64, 0.7)'
        }}]
    }},
    options: {{
        scales: {{
            y: {{
                beginAtZero: true,
                title: {{
                    display: true,
                    text: 'Tickets'
                }}
            }}
        }},
        plugins: {{
            legend: {{ display: false }},
            tooltip: {{ enabled: true }}
        }}
    }}
}});
</script>

</body>
</html>
'''

with open('output/comprehensive_ticket_dashboard.html', 'w') as f:
    f.write(html_template)

"Dashboard HTML file created and saved to output/comprehensive_ticket_dashboard.html"