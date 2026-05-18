# Each scenario is a tuple: (endpoint, description, expected_behavior)
SCENARIOS = [
    ("/payments", "normal payment", "should succeed most of the time"),
    ("/payments?delay=3000", "slow payment", "should timeout or spike latency"),
    ("/payments?fail=true", "forced payment failure", "should always fail"),
    ("/orders", "normal order", "should succeed most of the time"),
    ("/orders?delay=2000", "slow order", "should spike latency"),
    ("/orders?fail=true", "forced order failure", "should always fail"),
    ("/portfolio", "normal portfolio", "should succeed most of the time"),
    ("/login", "normal login", "should succeed most of the time"),
    ("/login?fail=true", "forced login failure", "should always return 401"),
]

# Targeted fault injection test suites
FAULT_INJECTION_SUITE = [
    ("/payments?fail=true", "forced payment failure", "should always fail"),
    ("/payments?fail=true", "forced payment failure", "should always fail"),
    ("/payments?fail=true", "forced payment failure", "should always fail"),
    ("/orders?fail=true", "forced order failure", "should always fail"),
    ("/login?fail=true", "forced login failure", "should always return 401"),
]

LATENCY_SUITE = [
    ("/payments?delay=3000", "slow payment", "latency spike"),
    ("/payments?delay=3000", "slow payment", "latency spike"),
    ("/orders?delay=2000", "slow order", "latency spike"),
    ("/orders?delay=2000", "slow order", "latency spike"),
    ("/portfolio?delay=1000", "slow portfolio", "latency spike"),
]

NORMAL_SUITE = [
    ("/payments", "normal payment", "baseline"),
    ("/orders", "normal order", "baseline"),
    ("/portfolio", "normal portfolio", "baseline"),
    ("/login", "normal login", "baseline"),
    ("/health", "health check", "should always succeed"),
]