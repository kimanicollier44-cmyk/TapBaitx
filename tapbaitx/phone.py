"""Phone + cell phone hub: own-device model, synthetic call log, cell profiles.
No carrier access, no real-number lookup. 555 numbers are flagged synthetic."""
import re, random

def normalize_number(raw):
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError("need a 10-digit US number")
    return digits

def format_number(raw):
    d = normalize_number(raw)
    return f"({d[0:3]}) {d[3:6]}-{d[6:10]}"

def is_synthetic(raw):
    d = normalize_number(raw)
    return d[3:6] == "555"  # 555 exchange = fictional / lab-safe

CELL_PROFILES = {
    "lte":   {"peak_mbps": 100.0,   "latency_ms": 30.0},
    "5g":    {"peak_mbps": 1000.0,  "latency_ms": 10.0},
    "6g-sim": {"peak_mbps": 10000.0, "latency_ms": 1.0},
}

def synthetic_call_log(seed=7, count=6):
    """Deterministic synthetic log - every number is a 555 fixture."""
    rng = random.Random(seed)
    log = []
    for i in range(count):
        log.append({
            "id": i + 1,
            "number": f"(202) 555-01{rng.randint(10,99)}",
            "synthetic": True,
            "direction": rng.choice(["in", "out"]),
            "seconds": rng.randint(12, 640),
        })
    return log

def call_totals(log):
    return {"calls": len(log), "seconds": sum(c["seconds"] for c in log)}
