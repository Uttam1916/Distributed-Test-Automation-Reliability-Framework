import asyncio
import httpx
import time
import random

from logger_config import logger
from scenarios import SCENARIOS, FAULT_INJECTION_SUITE, LATENCY_SUITE, NORMAL_SUITE
from metrics import init_db, save_metric
from anomalies import detect_anomalies

BASE_URL = "http://127.0.0.1:8000"
MAX_RETRIES = 3


async def make_request(client, endpoint, description=""):
    retries = 0

    while retries <= MAX_RETRIES:
        try:
            start = time.perf_counter()
            response = await client.get(BASE_URL + endpoint, timeout=6.0)
            end = time.perf_counter()

            latency = (end - start) * 1000

            if response.status_code >= 500:
                raise Exception(f"Server Error {response.status_code}")

            save_metric(endpoint, latency, "success", retries)
            logger.info(f"SUCCESS | {endpoint} | {latency:.2f}ms | retries={retries} | {description}")
            return latency, "success", retries, endpoint

        except Exception as e:
            retries += 1
            logger.error(f"FAILURE | {endpoint} | retry={retries} | {str(e)} | {description}")

            if retries > MAX_RETRIES:
                save_metric(endpoint, 0, "failure", retries)
                return 0, "failure", retries, endpoint

            await asyncio.sleep(1)


async def run_suite(suite_name, suite, multiplier=10):
    """
    Run a specific fault injection suite.
    multiplier = how many times to repeat the suite concurrently.
    """
    print(f"\n{'='*50}")
    print(f"Running suite: {suite_name}")
    print(f"{'='*50}")

    async with httpx.AsyncClient() as client:
        # Repeat the suite multiple times for load
        tasks = []
        for _ in range(multiplier):
            for endpoint, description, _ in suite:
                tasks.append(make_request(client, endpoint, description))

        results = await asyncio.gather(*tasks)

    successes = [r for r in results if r[1] == "success"]
    failures = [r for r in results if r[1] == "failure"]

    print(f"Total requests: {len(results)}")
    print(f"Successes: {len(successes)}")
    print(f"Failures: {len(failures)}")

    if successes:
        avg_latency = sum(r[0] for r in successes) / len(successes)
        print(f"Avg latency: {avg_latency:.2f}ms")

    return results


async def main():
    init_db()

    # Run all three suites in sequence
    await run_suite("NORMAL BASELINE", NORMAL_SUITE, multiplier=10)
    await run_suite("FAULT INJECTION", FAULT_INJECTION_SUITE, multiplier=10)
    await run_suite("LATENCY STRESS", LATENCY_SUITE, multiplier=5)

    # Detect anomalies across all collected data
    print(f"\n{'='*50}")
    print("Running anomaly detection across all suites...")
    print(f"{'='*50}")

    anomalies = detect_anomalies()
    print(f"\nTotal anomalies found: {len(anomalies)}")
    for a in anomalies:
        print(a)


if __name__ == "__main__":
    asyncio.run(main())