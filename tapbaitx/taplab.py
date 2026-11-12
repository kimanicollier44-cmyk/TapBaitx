"""Simulated wiretap chamber - synthetic fixture lines ONLY.
A tap session needs (a) a fixture line and (b) an authorization reference
(own-device consent or a case reference recorded by the operator).
Anything real is HOLD - see gates.py. No audio is captured; the lab
analyses synthetic transcripts the operator supplies for the fixture."""
from dataclasses import dataclass, field

class HoldError(RuntimeError):
    pass

@dataclass
class FixtureLine:
    line_id: str
    number: str
    synthetic: bool = True
    transcript: list = field(default_factory=list)  # [(speaker, text), ...]

def open_tap(line, authorization_ref):
    if not line.synthetic:
        raise HoldError("HOLD: only synthetic fixture lines can be tapped in this lab")
    if not authorization_ref:
        raise HoldError("HOLD: an authorization reference is required (own-device consent or case ref)")
    return {"line_id": line.line_id, "authorized": True, "live_audio": False,
            "mode": "synthetic-transcript-analysis"}

def analyse_transcript(line):
    words = {}
    speakers = {}
    for speaker, text in line.transcript:
        speakers[speaker] = speakers.get(speaker, 0) + 1
        for w in text.lower().split():
            words[w] = words.get(w, 0) + 1
    top = sorted(words.items(), key=lambda kv: -kv[1])[:5]
    return {"turns": len(line.transcript), "speakers": speakers, "top_words": top}
