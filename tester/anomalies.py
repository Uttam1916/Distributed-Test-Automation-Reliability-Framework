import sqlite3
import statistics
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "metrics.db")
ANOMALY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "anomalies.json")


def detect_anomalies():
    # Pull all data from the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT endpoint, latency, status FROM metrics")
    rows = cursor.fetchall()
    conn.close()

    #  Group by endpoint
    endpoint_data = {}
    for endpoint, latency, status in rows:
        if endpoint not in endpoint_data:
            endpoint_data[endpoint] = []
        endpoint_data[endpoint].append((latency, status))

    anomalies = []

    # Analyze each endpoint separately
    for endpoint, values in endpoint_data.items():

        latencies = [v[0] for v in values if v[1] == "success"]  # only successful latencies
        failures = [v for v in values if v[1] == "failure"]

        # Need at least 2 data points for std deviation
        if len(latencies) < 2:
            continue

        avg = statistics.mean(latencies)
        std = statistics.stdev(latencies)

        # Latency anomaly — 2 sigma rule
        for latency in latencies:
            if latency > avg + 2 * std:
                anomalies.append({
                    "endpoint": endpoint,
                    "issue": "high_latency",
                    "value_ms": round(latency, 2),
                    "threshold_ms": round(avg + 2 * std, 2),
                    "mean_ms": round(avg, 2)
                })

        # Failure rate anomaly
        failure_rate = len(failures) / len(values)
        if failure_rate > 0.3:
            anomalies.append({
                "endpoint": endpoint,
                "issue": "high_failure_rate",
                "failure_rate_pct": round(failure_rate * 100, 2),
                "total_requests": len(values),
                "failures": len(failures)
            })

    #  Save to file
    with open(ANOMALY_FILE, "w") as f:
        json.dump(anomalies, f, indent=4)

    return anomalies


if __name__ == "__main__":
    anomalies = detect_anomalies()
    print(f"\nAnomalies detected: {len(anomalies)}\n")
    for a in anomalies:
        print(a)