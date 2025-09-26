import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()
num_records = 200000

# Date range
date_start = pd.Timestamp("2025-01-01 00:00:00")
date_end = pd.Timestamp("2025-08-31 23:59:59")

# Logical IT subcategories and their typical resolution texts
subcategories = [
    "Password reset", "Account locked", "Software installation error",
    "Email not syncing", "Hardware failure", "VPN connectivity",
    "Device onboarding", "Data retrieval", "Software crash", "Performance issue"
]
resolutions = {
    "Password reset": "User password reset successfully.",
    "Account locked": "Account unlocked and user notified.",
    "Software installation error": "Software reinstalled, error resolved.",
    "Email not syncing": "Mail server reconfigured; sync restored.",
    "Hardware failure": "Faulty device replaced.",
    "VPN connectivity": "VPN settings updated; user able to connect.",
    "Device onboarding": "Device configured and added to company inventory.",
    "Data retrieval": "Data restored from backup.",
    "Software crash": "Bug report logged and patch applied.",
    "Performance issue": "Performance optimized after settings adjustment."
}

categories = [
    "Account Management", "Communication", "Hardware", "Network & Security", "Software", "Access"
]
groups = [
    "Desktop Support", "Network Support", "Application Support", "Infrastructure", "Security"
]
impacts = ["Low", "Medium", "High"]
urgencies = ["Low", "Medium", "High"]
priorities = ["P1", "P2", "P3"]
technicians = ["Surendren M", "Samaira K", "Imran S", "Not Assigned"]
statuses = ["Open", "In Progress", "Resolved", "Closed"]
accounts = ["NON-MSDT", "MSDT"]
sla_names = ["Medium SLA", "High SLA", "Low SLA"]

columns = [
    "Request ID","Requester","Request Type","Account","Created Time","Subject","Group","Impact","Urgency","Priority",
    "Category","Subcategory","Technician","Request Status","Resolution","DueBy Time","First Response Overdue Status",
    "Item","Overdue Status","Resolved Time","Responded Date","Response DueBy Time","Site","Out Of Scope",
    "Request age after SLA response violation","Request age after SLA violation","SLA resolution time","SLA Name",
    "SLA response time","SLA violated technician"
]

data = []
for i in range(num_records):
    # Logical time assignment
    created_time = fake.date_time_between(start_date=date_start, end_date=date_end)
    responded_delta = np.random.randint(1*60, 2*60*60)          # 1 min to 2 hours
    responded_time = created_time + pd.Timedelta(seconds=responded_delta)
    resolved_delta = responded_delta + np.random.randint(10*60, 72*60*60) # 10 min to 3 days
    resolved_time = created_time + pd.Timedelta(seconds=resolved_delta)
    dueby_delta = np.random.choice([24*60*60, 48*60*60, 72*60*60]) # 1, 2, or 3 days
    dueby_time = created_time + pd.Timedelta(seconds=dueby_delta)
    response_dueby_time = created_time + pd.Timedelta(seconds=60*60) # 1 hour after created
    
    subcategory = np.random.choice(subcategories)
    resolution = resolutions[subcategory]
    category = np.random.choice(categories)
    group = np.random.choice(groups)
    impact = np.random.choice(impacts)
    urgency = np.random.choice(urgencies)
    # Priority logic: If high impact/urgency, likelihood of P1 increases
    if impact == "High" or urgency == "High":
        pr = [0.6, 0.2, 0.2]  # Sums to 1
    else:
        pr = [0.2, 0.2, 0.6]  # Sums to 1
    priority = np.random.choice(priorities, p=pr)
    technician = np.random.choice(technicians)
    request_status = np.random.choice(statuses, p=[0.05,0.10,0.50,0.35])
    item = subcategory.split()[0] if " " in subcategory else subcategory
    overdue_status = resolved_time > dueby_time
    first_resp_overdue = responded_time > response_dueby_time
    account = np.random.choice(accounts)
    site = np.random.choice(accounts)
    out_of_scope = np.random.choice(["No","Yes"], p=[0.97,0.03])
    sla_name = np.random.choice(sla_names)
    # Calculate SLA times, request age, resolution times (simple format)
    sla_response_time = str(response_dueby_time - created_time)
    sla_resolution_time = str(dueby_time - created_time)
    age_resp_violation = str(responded_time - response_dueby_time) if first_resp_overdue else "00:00:00"
    age_sla_violation = str(resolved_time - dueby_time) if overdue_status else "00:00:00"
    sla_violated_tech = technician if overdue_status else "Not Assigned"

    row = [
        f"REQ-{100000 + i}",
        fake.email(),
        np.random.choice(["Incident", "Request", "Change"]),
        account,
        created_time.strftime('%Y-%m-%d %H:%M:%S'),
        f"{subcategory} Ticket #{10000+i} raised",
        group,
        impact,
        urgency,
        priority,
        category,
        subcategory,
        technician,
        request_status,
        resolution,
        dueby_time.strftime('%Y-%m-%d %H:%M:%S'),
        first_resp_overdue,
        item,
        overdue_status,
        resolved_time.strftime('%Y-%m-%d %H:%M:%S'),
        responded_time.strftime('%Y-%m-%d %H:%M:%S'),
        response_dueby_time.strftime('%Y-%m-%d %H:%M:%S'),
        site,
        out_of_scope,
        age_resp_violation,
        age_sla_violation,
        sla_resolution_time,
        sla_name,
        sla_response_time,
        sla_violated_tech
    ]
    data.append(row)

df = pd.DataFrame(data, columns=columns)

df.to_excel("realistic_ticket_data.xlsx", index=False)
