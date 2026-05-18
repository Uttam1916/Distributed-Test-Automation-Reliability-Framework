# Distributed Test Automation Reliability Framework

A test automation framework that runs concurrent load tests against a REST API, detects anomalies, and generates reports. Built to simulate real-world failure scenarios including latency spikes, random failures, and forced error states.

## What it does

- Fires concurrent HTTP requests using asyncio and measures latency per endpoint
- Simulates production failure modes — random failures, forced errors, artificial delays
- Persists every request result to SQLite with endpoint, latency, status, and retry count
- Detects anomalies using 2-sigma latency thresholds and failure rate analysis per endpoint
- Generates a markdown report summarizing failures and anomalies across test runs
- Visualizes results in a Streamlit dashboard

## Stack

Python · FastAPI · asyncio · httpx · SQLite · pytest · Streamlit

## Structure

```
├── service/          # FastAPI app — the system under test
├── tester/           # Test runner, metrics, anomaly detection, reports
├── dashboard/        # Streamlit visualization
├── tests/            # pytest suite
└── data/             # SQLite database (auto-created on first run)
```

## Running it

```bash
# 1. Start the API
cd service && uvicorn app:app --reload

# 2. Run load tests
cd tester && python runner.py

# 3. Generate report
cd tester && python report_generator.py

# 4. View dashboard
cd dashboard && streamlit run app.py

# 5. Run unit tests
pytest tests/
```

## How the test suites work

Three suites run in sequence:

1. **Baseline** — normal requests to establish healthy latency and failure rate reference data
2. **Fault injection** — forced failures to test retry logic and failure detection
3. **Latency stress** — artificial delays to test latency anomaly detection

Anomaly detection runs after all three suites using the full dataset.

## Anomaly detection logic

Each endpoint is analyzed independently. A request is flagged as a latency anomaly if its value exceeds the mean plus two standard deviations for that endpoint. An endpoint is flagged for high failure rate if more than 30% of its requests failed.
