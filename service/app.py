from fastapi import FastAPI, HTTPException
import asyncio
import random
from datetime import datetime

app = FastAPI()

#simulate random failure
def maybe_fail(probability=0.2):
    if random.random() < probability:
        raise HTTPException(status_code=500, detail="Random server failure")
    
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


##simulated delay and failure for each end point
@app.get("/login")
async def login(delay: int = 0, fail: bool = False):
    if delay:
        await asyncio.sleep(delay / 1000)
    if fail:
        raise HTTPException(status_code=401, detail="Login failed")
    maybe_fail(0.1)
    return {"status": "success", "token": random.randint(10000, 99999)}


@app.get("/orders")
async def orders(delay: int = 0, fail: bool = False):
    if delay:
        await asyncio.sleep(delay / 1000)
    if fail:
        raise HTTPException(status_code=500, detail="Order service failed")
    maybe_fail(0.15)
    return {"status": "success", "orders": [{"id": random.randint(1, 100), "price": random.randint(100, 1000)}]}


@app.get("/payments")
async def payments(delay: int = 0, fail: bool = False):
    if delay:
        await asyncio.sleep(delay / 1000)
    if fail:
        raise HTTPException(status_code=500, detail="Payment failed")
    maybe_fail(0.2)
    return {"status": "success", "transaction_id": random.randint(1000, 9999)}


@app.get("/portfolio")
async def portfolio(delay: int = 0, fail: bool = False):
    if delay:
        await asyncio.sleep(delay / 1000)
    if fail:
        raise HTTPException(status_code=500, detail="Portfolio unavailable")
    maybe_fail(0.1)
    return {"status": "success", "portfolio_value": random.randint(100000, 500000)}