import json

# Data for charts
request_type_distribution = {"Incident": 2245, "Service Request": 2180, "Preventive Maintenance": 20, "Security Incident": 16, "Request For Information": 5, "Change Requests": 3}

request_status_distribution = {"Closed": 4345, "Waiting for Customer": 50, "Cancelled": 30, "Waiting for Vendor": 17, "Assigned": 10, "Waiting for parts - NOC": 9, "Onhold": 5, "In Progress": 2, "Open": 1}

monthly_ticket_volume = [{"year_month": "2025-01", "count": 1071}, {"year_month": "2025-02", "count": 1033}, {"year_month": "2025-03", "count": 1127}, {"year_month": "2025-04", "count": 1238}]

avg_resolution_time_by_category = {
    "Preventive Maintenance": 388.33,
    "Procurement": 208.18,
    "Network & Security": 121.97,
    "Cloud Services": 105.85,
    "Systems": 78.50,
    "Telecom": 77.10,
    "Microsoft Dynamics 365 - Barton": 74.02,
    "End User Support": 59.04,
    "Information Security": 53.42,
    "License Changes": 50.65,
    "Patch Management": 32.28,
    "Microsoft": 28.72,
    "Application": 27.13,
    "Infra Monitoring": 10.87,
    "Reports": 7.30
}

# Prepare JSON strings for embedding
request_type_labels = json.dumps(list(request_type_distribution.keys()))
request_type_values = json.dumps(list(request_type_distribution.values()))

request_status_labels = json.dumps(list(request_status_distribution.keys()))
request_status_values = json.dumps(list(request_status_distribution.values()))

monthly_labels = json.dumps([d['year_month'] for d in monthly_ticket_volume])
monthly_values = json.dumps([d['count'] for d in monthly_ticket_volume])

resolution_labels = json.dumps(list(avg_resolution_time_by_category.keys()))
resolution_values = json.dumps(list(avg_resolution_time_by_category.values()))

# Create dashboard HTML
html_content = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Ticket Metrics Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f4f7f9; color: #333; }}
        h1 {{ text-align: center; margin-bottom: 40px; color: #2c3e50; }}
        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: flex; flex-direction: column; }}
        canvas {{ width: 100% !important; height: 280px !important; }}
        .insight {{ margin-top: 10px; font-size: 0.9rem; color: #555; }}
    </style>
</head>
<body>
    <h1>Ticket Metrics Dashboard</h1>
    <div class=\"dashboard\">
        <!-- Ticket Type Distribution -->
        <div class=\"card\">
            <h2>Ticket Type Distribution</h2>
            <canvas id=\"typeChart\"></canvas>
            <p class=\"insight\">Most tickets are \"Incident\" and \"Service Request\", reflecting common IT workload categories.</p>
        </div>

        <!-- Ticket Status Distribution -->
        <div class=\"card\">
            <h2>Ticket Status Distribution</h2>
            <canvas id=\"statusChart\"></canvas>
            <p class=\"insight\">Majority of tickets are Closed indicating good resolution rates.</p>
        </div>

        <!-- Monthly Ticket Volume -->
        <div class=\"card\">
            <h2>Monthly Ticket Volume</h2>
            <canvas id=\"monthlyChart\"></canvas>
            <p class=\"insight\">Ticket volume is steadily increasing month over month.</p>
        </div>

        <!-- Average Resolution Time by Category -->
        <div class=\"card\">
            <h2>Average Resolution Time by Category (hours)</h2>
            <canvas id=\"resolutionChart\"></canvas>
            <p class=\"insight\">Preventive Maintenance tickets have the highest average resolution time, suggesting complex or long-duration tasks.</p>
        </div>
    </div>

    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
    <script>
        const typeData = {{
            labels: {request_type_labels},
            datasets: [{{
                label: 'Ticket Count',
                data: {request_type_values},
                backgroundColor: ['#3498db', '#2ecc71', '#e67e22', '#9b59b6', '#e74c3c', '#34495e']
            }}]
        }};

        const statusData = {{
            labels: {request_status_labels},
            datasets: [{{
                label: 'Ticket Count',
                data: {request_status_values},
                backgroundColor: ['#1abc9c', '#f39c12', '#e74c3c', '#95a5a6', '#2980b9', '#d35400', '#7f8c8d', '#8e44ad', '#c0392b']
            }}]
        }};

        const monthlyData = {{
            labels: {monthly_labels},
            datasets: [{{
                label: 'Tickets',
                data: {monthly_values},
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                fill: true,
                tension: 0.3
            }}]
        }};

        const resolutionData = {{
            labels: {resolution_labels},
            datasets: [{{
                label: 'Average Resolution Time (hrs)',
                data: {resolution_values},
                backgroundColor: '#e67e22'
            }}]
        }};

        const configType = {{
            type: 'pie',
            data: typeData,
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
        }};

        const configStatus = {{
            type: 'doughnut',
            data: statusData,
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
        }};

        const configMonthly = {{
            type: 'line',
            data: monthlyData,
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Number of Tickets' }} }},
                    x: {{ title: {{ display: true, text: 'Month' }} }}
                }}
            }}
        }};

        const configResolution = {{
            type: 'bar',
            data: resolutionData,
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: 'Hours' }} }},
                    x: {{ title: {{ display: true, text: 'Category' }} }}
                }}
            }}
        }};

        window.onload = function() {{
            const ctxType = document.getElementById('typeChart').getContext('2d');
            const ctxStatus = document.getElementById('statusChart').getContext('2d');
            const ctxMonthly = document.getElementById('monthlyChart').getContext('2d');
            const ctxResolution = document.getElementById('resolutionChart').getContext('2d');

            new Chart(ctxType, configType);
            new Chart(ctxStatus, configStatus);
            new Chart(ctxMonthly, configMonthly);
            new Chart(ctxResolution, configResolution);
        }};
    </script>
</body>
</html>
"""

output_file = "output/ticket_metrics_dashboard.html"

with open(output_file, 'w') as f:
    f.write(html_content)

output_file