import asyncio
import httpx
import time
import random

from logger_config import logger
from scenarios import SCENARIOS
from metrics import init_db, save_metric         

BASE_URL = "http://127.0.0.1:8000"
MAX_RETRIES = 3


async def make_request(client, endpoint):
    retries = 0

    while retries <= MAX_RETRIES:
        try:
            start = time.perf_counter()
            response = await client.get(BASE_URL + endpoint, timeout=5.0)
            end = time.perf_counter()

            latency = (end - start) * 1000

            if response.status_code >= 500:
                raise Exception("Server Error")

            save_metric(endpoint, latency, "success", retries)    
            logger.info(f"SUCCESS | {endpoint} | {latency:.2f}ms | retries={retries}")
            return latency, "success", retries, endpoint

        except Exception as e:
            retries += 1
            logger.error(f"FAILURE | {endpoint} | retry={retries} | error={str(e)}")

            if retries > MAX_RETRIES:
                save_metric(endpoint, 0, "failure", retries)        
                return 0, "failure", retries, endpoint

            await asyncio.sleep(1)


async def run_load_test(total_requests=100):
    async with httpx.AsyncClient() as client:
        tasks = [
            make_request(client, random.choice(SCENARIOS))
            for _ in range(total_requests)
        ]
        results = await asyncio.gather(*tasks)
        return results


async def main():
    init_db()                                                       
    print("Starting load test...")
    results = await run_load_test(100)

    successes = [r for r in results if r[1] == "success"]
    failures = [r for r in results if r[1] == "failure"]

    print(f"\nTotal: {len(results)}")
    print(f"Successes: {len(successes)}")
    print(f"Failures: {len(failures)}")

    if successes:
        avg_latency = sum(r[0] for r in successes) / len(successes)
        print(f"Avg latency: {avg_latency:.2f}ms")


if __name__ == "__main__":
    asyncio.run(main())