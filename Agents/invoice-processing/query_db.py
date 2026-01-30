"""
Query and display invoice data from DuckDB database
"""
import duckdb
import pandas as pd

# Connect to database
conn = duckdb.connect('invoices.db')

print("="*100)
print("INVOICE DATABASE QUERY RESULTS")
print("="*100)

# 1. Invoice Summary
print("\n" + "="*100)
print("INVOICE SUMMARY")
print("="*100)
result = conn.execute("""
    SELECT
        i.id,
        i.invoice_no,
        i.date_of_issue,
        i.seller_name,
        i.client_name,
        i.net_worth_total,
        i.vat_total,
        i.gross_worth_total,
        i.confidence_score,
        COUNT(l.id) as item_count
    FROM invoices i
    LEFT JOIN line_items l ON i.id = l.invoice_id
    GROUP BY i.id, i.invoice_no, i.date_of_issue, i.seller_name, i.client_name,
             i.net_worth_total, i.vat_total, i.gross_worth_total, i.confidence_score
    ORDER BY i.id;
""").fetchdf()

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

print(result.to_string(index=False))

# 2. Detailed Invoice Information
print("\n" + "="*100)
print("DETAILED INVOICE INFORMATION")
print("="*100)

for invoice_id in range(1, 6):
    invoice = conn.execute(f"""
        SELECT * FROM invoices WHERE id = {invoice_id};
    """).fetchone()

    if invoice:
        print(f"\n{'='*100}")
        print(f"INVOICE #{invoice_id} - {invoice[1]}")
        print(f"{'='*100}")
        print(f"Date of Issue: {invoice[2]}")
        print(f"Confidence Score: {float(invoice[14]):.2%}")
        print(f"\nSeller:")
        print(f"  Name: {invoice[3]}")
        print(f"  Address: {invoice[4]}")
        print(f"  Tax ID: {invoice[5]}")
        print(f"  IBAN: {invoice[6]}")
        print(f"\nClient:")
        print(f"  Name: {invoice[7]}")
        print(f"  Address: {invoice[8]}")
        print(f"  Tax ID: {invoice[9]}")
        print(f"\nFinancial Summary:")
        print(f"  VAT Rate: {float(invoice[10])}%")
        print(f"  Net Worth Total: $" + f"{float(invoice[11]):,.2f}")
        print(f"  VAT Total: $" + f"{float(invoice[12]):,.2f}")
        print(f"  Gross Worth Total: $" + f"{float(invoice[13]):,.2f}")

        # Get line items
        line_items = conn.execute(f"""
            SELECT * FROM line_items WHERE invoice_id = {invoice_id} ORDER BY item_no;
        """).fetchall()

        print(f"\nLine Items ({len(line_items)}):")
        for item in line_items:
            print(f"\n  {item[2]}. {item[3][:70]}")
            print(f"     Qty: {float(item[4])} {item[5]}")
            print(f"     Net Price: $" + f"{float(item[6]):,.2f} | Net Worth: $" + f"{float(item[7]):,.2f}")
            print(f"     VAT: {float(item[8])}% | Gross Worth: $" + f"{float(item[9]):,.2f}")

# 3. Overall Statistics
print("\n" + "="*100)
print("OVERALL STATISTICS")
print("="*100)

stats = conn.execute("""
    SELECT
        COUNT(DISTINCT i.id) as total_invoices,
        COUNT(l.id) as total_line_items,
        SUM(i.net_worth_total) as total_net_worth,
        SUM(i.vat_total) as total_vat,
        SUM(i.gross_worth_total) as total_gross_worth,
        AVG(i.confidence_score) as avg_confidence
    FROM invoices i
    LEFT JOIN line_items l ON i.id = l.invoice_id;
""").fetchone()

print(f"Total Invoices: {stats[0]}")
print(f"Total Line Items: {stats[1]}")
print(f"Total Net Worth: $" + f"{float(stats[2]):,.2f}")
print(f"Total VAT: $" + f"{float(stats[3]):,.2f}")
print(f"Total Gross Worth: $" + f"{float(stats[4]):,.2f}")
print(f"Average Confidence: {float(stats[5]):.2%}")

# 4. Line Items Count per Invoice
print("\n" + "="*100)
print("LINE ITEMS COUNT PER INVOICE")
print("="*100)

line_count = conn.execute("""
    SELECT
        i.invoice_no,
        COUNT(l.id) as item_count
    FROM invoices i
    LEFT JOIN line_items l ON i.id = l.invoice_id
    GROUP BY i.invoice_no
    ORDER BY i.id;
""").fetchdf()

print(line_count.to_string(index=False))

# 5. Export to CSV
print("\n" + "="*100)
print("EXPORTING DATA TO CSV")
print("="*100)

conn.execute("COPY invoices TO 'invoices_export.csv' (HEADER, DELIMITER ',');")
print("[+] Exported invoices to: invoices_export.csv")

conn.execute("COPY line_items TO 'line_items_export.csv' (HEADER, DELIMITER ',');")
print("[+] Exported line items to: line_items_export.csv")

# Close connection
conn.close()

print("\n" + "="*100)
print("QUERY COMPLETE")
print("="*100)
