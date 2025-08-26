import json

# Data for the dashboard
labels = ["Incident", "Service Request", "Preventive Maintenance", "Security Incident", "Request For Information", "Change Requests"]
counts = [2245, 2180, 20, 16, 5, 3]
percentages = [50.23, 48.78, 0.45, 0.36, 0.11, 0.07]

# Create the HTML content with Chart.js pie chart and a bar chart
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Ticket Type Distribution Dashboard</title>
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f7fa; color: #333; }}
  h1 {{ text-align: center; color: #2c3e50; margin-bottom: 1rem; }}
  .container {{ max-width: 900px; margin: 0 auto; display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
  .card {{ background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; }}
  canvas {{ max-width: 100%; height: auto; }}
  .insights {{ grid-column: span 2; background: #ecf0f1; padding: 1rem; border-radius: 10px; color: #34495e; }}
</style>
</head>
<body>
  <h1>Ticket Type Distribution Dashboard</h1>
  <div class="container">
    <div class="card">
      <canvas id="pieChart"></canvas>
    </div>
    <div class="card">
      <canvas id="barChart"></canvas>
    </div>
    <div class="insights">
      <h2>Data Insights</h2>
      <p>The majority of tickets are "Incident" and "Service Request" types, accounting for over 99% of all tickets combined.</p>
      <p>Smaller proportions of tickets belong to categories like "Preventive Maintenance," "Security Incident," "Request For Information," and "Change Requests."</p>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const labels = {json.dumps(labels)};
    const counts = {json.dumps(counts)};
    const percentages = {json.dumps(percentages)};

    const pieCtx = document.getElementById('pieChart').getContext('2d');
    const pieChart = new Chart(pieCtx, {{
      type: 'pie',
      data: {{
        labels: labels,
        datasets: [{{
          data: counts,
          backgroundColor: [
            '#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f1c40f', '#34495e'
          ],
          borderColor: '#ecf0f1',
          borderWidth: 2
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ position: 'top' }},
          tooltip: {{
            callbacks: {{
              label: function(context) {{
                let label = context.label || '';
                let value = context.parsed || 0;
                let percent = percentages[context.dataIndex] || 0;
                return `${{label}}: ${{value}} tickets (${{percent}}%)`;
              }}
            }}
          }}
        }}
      }}
    }});

    const barCtx = document.getElementById('barChart').getContext('2d');
    const barChart = new Chart(barCtx, {{
      type: 'bar',
      data: {{
        labels: labels,
        datasets: [{{
          label: 'Ticket Counts',
          data: counts,
          backgroundColor: '#2980b9'
        }}]
      }},
      options: {{
        responsive: true,
        scales: {{
          y: {{
            beginAtZero: true,
            ticks: {{ color: '#34495e' }},
            grid: {{ color: '#ecf0f1' }}
          }},
          x: {{ ticks: {{ color: '#34495e' }}, grid: {{ color: '#ecf0f1' }} }}
        }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: function(context) {{
                return `Count: ${{context.parsed.y}}`;
              }}
            }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""

# Save the HTML file
with open('output/ticket_type_distribution_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

result = 'Dashboard HTML saved to output/ticket_type_distribution_dashboard.html'