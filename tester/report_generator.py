import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "metrics.db")
ANOMALY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "anomalies.json")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "report.md")


def generate_report():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM metrics")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM metrics WHERE status='failure'")
    failures = cursor.fetchone()[0]

    cursor.execute("""
        SELECT endpoint, AVG(latency), COUNT(*),
               SUM(CASE WHEN status='failure' THEN 1 ELSE 0 END)
        FROM metrics
        GROUP BY endpoint
        ORDER BY AVG(latency) DESC
    """)
    endpoint_stats = cursor.fetchall()
    conn.close()

    failure_rate = (failures / total * 100) if total > 0 else 0

    try:
        with open(ANOMALY_FILE, "r") as f:
            anomalies = json.load(f)
    except:
        anomalies = []

    # Build markdown report
    report = f"""# Reliability Test Report
Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC

## Summary
| Metric | Value |
|--------|-------|
| Total Requests | {total} |
| Total Failures | {failures} |
| Overall Failure Rate | {failure_rate:.2f}% |
| Anomalies Detected | {len(anomalies)} |

## Per-Endpoint Breakdown
| Endpoint | Avg Latency (ms) | Total Requests | Failures |
|----------|-----------------|----------------|----------|
"""

    for endpoint, avg_latency, count, fail_count in endpoint_stats:
        report += f"| {endpoint} | {avg_latency:.2f} | {count} | {fail_count} |\n"

    report += f"""
## Anomalies
"""
    if anomalies:
        for a in anomalies:
            report += f"- `{a['endpoint']}` — **{a['issue']}**"
            if a['issue'] == 'high_latency':
                report += f" — {a['value_ms']}ms (threshold: {a['threshold_ms']}ms)\n"
            else:
                report += f" — {a['failure_rate_pct']}% failure rate ({a['failures']}/{a['total_requests']} requests)\n"
    else:
        report += "No anomalies detected.\n"

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write(report)

    print(f"Report saved to {REPORT_PATH}")
    return REPORT_PATH


if __name__ == "__main__":
    generate_report()