"""
HTML Dashboard Templates for Data Analysis
Safe templates that avoid f-string conflicts
"""

def get_html_template():
    """Returns a safe HTML template without f-string conflicts"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Support Ticket Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f6fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
        }
        
        .insights-section {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .insights-title {
            font-size: 1.5rem;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .insight-item {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 5px 5px 0;
        }
        
        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Support Ticket Analysis Dashboard</h1>
            <p>Comprehensive analysis of support ticket data and trends</p>
        </div>
        
        <!-- KPI Cards Section -->
        <div class="stats-grid">
            <!-- Stats will be inserted here -->
            {{STATS_CONTENT}}
        </div>
        
        <!-- Charts Section -->
        <div class="charts-grid">
            <!-- Charts will be inserted here -->
            {{CHARTS_CONTENT}}
        </div>
        
        <!-- Insights Section -->
        <div class="insights-section">
            <h2 class="insights-title">Key Insights</h2>
            {{INSIGHTS_CONTENT}}
        </div>
    </div>
    
    <script>
        // Chart data and initialization
        {{JAVASCRIPT_CONTENT}}
    </script>
</body>
</html>"""

def get_stat_card_template():
    """Returns template for stat cards"""
    return """
    <div class="stat-card">
        <div class="stat-number">{{NUMBER}}</div>
        <div class="stat-label">{{LABEL}}</div>
    </div>
    """

def get_chart_card_template():
    """Returns template for chart cards"""  
    return """
    <div class="chart-card">
        <h3 class="chart-title">{{CHART_TITLE}}</h3>
        <div class="chart-container">
            <canvas id="{{CHART_ID}}"></canvas>
        </div>
    </div>
    """

def get_insight_template():
    """Returns template for insights"""
    return """
    <div class="insight-item">
        <strong>{{INSIGHT_TITLE}}:</strong> {{INSIGHT_TEXT}}
    </div>
    """

def get_chart_js_template(chart_id, chart_type, data_labels, data_values, title=""):
    """Returns Chart.js initialization code"""
    return f"""
    // Initialize {title} Chart
    const {chart_id}Ctx = document.getElementById('{chart_id}').getContext('2d');
    const {chart_id}Chart = new Chart({chart_id}Ctx, {{
        type: '{chart_type}',
        data: {{
            labels: {data_labels},
            datasets: [{{
                label: '{title}',
                data: {data_values},
                backgroundColor: [
                    '#3498db', '#e74c3c', '#2ecc71', '#f39c12', 
                    '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'bottom'
                }}
            }}
        }}
    }});
    """