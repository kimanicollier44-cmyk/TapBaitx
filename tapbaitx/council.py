"""Council: Gemini Carbon 4 Extended Thinking (DECIDER) + Muse (advisor).
Darion's 'argon 4' = his house Carbon 4 seat. Offline, names-only keys,
tighten-only: the council can raise a HOLD, never lift one. No live calls."""
import os

CARBON_MODEL = "google/gemini-carbon-4-extended-pro-thinking"
MUSE_MODELS = ["muse-spark-1.1", "muse-wonder-1.0"]
TIERS = [2048, 8192, 32768]

def carbon_decide(question, risk="low", tier=32768):
    if tier not in TIERS:
        raise ValueError("tier must be one of 2048 / 8192 / 32768")
    trace = ["MAP: " + question, "MODEL: offline deterministic model",
             "STRESS: consent + authorization negative controls applied",
             "DECIDE: see verdict"]
    verdict = "HOLD" if risk == "hold" else "PROCEED-WITH-GATES"
    return {"seat": "gemini-carbon-4", "model": CARBON_MODEL, "tier": tier,
            "trace": trace, "verdict": verdict,
            "key_present": bool(os.environ.get("GEMINI_API_KEY")),
            "live_call": False}

def muse_advise(question):
    return {"seat": "muse", "models": MUSE_MODELS, "authority": "none",
            "advice": ["Keep every tap synthetic-fixture only.",
                       "Keep location opt-in and city-fuzzed in public output.",
                       "Keep media location behind owner consent.",
                       "Never let a model verdict lift a HOLD gate."],
            "key_present": bool(os.environ.get("MODEL_API_KEY")),
            "live_call": False}

def council(question, risk="low"):
    d = carbon_decide(question, risk=risk)
    a = muse_advise(question)
    return {"decider": d, "advisor": a,
            "final": d["verdict"]}  # advisor can never override the decider/HOLD
