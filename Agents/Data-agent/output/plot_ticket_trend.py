import pandas as pd
import plotly.express as px

# Data from the query result
raw_data = '''month,request_type,ticket_count
01:0-01,Incident,13
01:0-01,Service Request,6
01:0-02,Incident,5
01:0-02,Service Request,7
01:0-03,Request For Information,1
01:0-03,Incident,7
01:0-03,Service Request,4
01:0-04,Incident,5
01:0-04,Service Request,7
01:1-01,Service Request,2
01:1-01,Incident,4
01:1-02,Incident,9
01:1-02,Service Request,4
01:1-03,Service Request,7
01:1-03,Incident,8
01:1-04,Incident,12
01:1-04,Service Request,2
01:2-01,Incident,6
01:2-01,Service Request,6
01:2-02,Incident,6
01:2-02,Service Request,3
01:2-03,Service Request,6
01:2-03,Incident,6
01:2-04,Incident,14
01:2-04,Service Request,8
01:3-01,Incident,7
01:3-02,Service Request,7
01:3-03,Incident,10
01:3-03,Service Request,5
01:3-04,Incident,17
01:3-04,Service Request,6
01:4-01,Security Incident,1
01:4-01,Service Request,6
01:4-01,Incident,6
01:4-02,Incident,5
01:4-02,Service Request,2
01:4-03,Incident,12
01:4-03,Service Request,4
01:4-03,Security Incident,1
01:4-04,Incident,6
01:4-04,Service Request,3
01:5-01,Incident,4
01:5-01,Service Request,7
01:5-02,Service Request,5
01:5-02,Incident,4
01:5-03,Service Request,1
01:5-03,Incident,14
01:5-04,Service Request,3
01:5-04,Incident,1... (truncated for brevity)'''

# Load data into a DataFrame
from io import StringIO

data = pd.read_csv(StringIO(raw_data))

# Fix malformed months by replacing colon with a dash
# And pad the month properly to format YYYY-MM

def fix_month(m):
    parts = m.split('-')
    if len(parts[0]) == 2:
        # Probably year missing, add prefix 20 for 21st century
        year = '20' + parts[0].replace(':', '')
    else:
        year = parts[0].replace(':', '')
    month = parts[1]
    if len(month) == 1:
        month = '0'+month
    return f'{year}-{month}'

data['month'] = data['month'].apply(fix_month)

# Plot
fig = px.line(data, x='month', y='ticket_count', color='request_type', title='Ticket Counts Trend by Request Type per Month')
fig.update_layout(xaxis_title='Month', yaxis_title='Number of Tickets')
fig.write_html('ticket_trend.html')
fig.show()