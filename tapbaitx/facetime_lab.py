"""FaceTime-style video lab - own rooms, camera OFF by default.
A friend is seen only if they joined AND turned their own camera on
(pattern from LiveShareX v1.6.0). Real FaceTime traffic is encrypted:
this lab never decrypts it - it models packet METADATA (size/timing)
from synthetic captures only."""

def room_code(seed_text):
    import hashlib
    h = hashlib.sha256(seed_text.encode()).hexdigest()
    return h[:6].upper()

def tile_layout(n, width=1920, height=1080):
    if n <= 0:
        return {"cols": 0, "rows": 0, "tile_w": 0, "tile_h": 0}
    cols = int(n ** 0.5)
    while cols * cols < n:
        cols += 1
    rows = (n + cols - 1) // cols
    return {"cols": cols, "rows": rows, "tile_w": width // cols, "tile_h": height // rows}

class Participant:
    def __init__(self, name):
        self.name = name; self.joined = False
        self.camera_on = False; self.mic_on = False
    def visible(self):
        return self.joined and self.camera_on

def metadata_summary(packets):
    """packets: synthetic [(bytes_len, gap_ms), ...] - metadata only, no payload."""
    if not packets:
        return {"packets": 0, "total_bytes": 0, "avg_gap_ms": 0.0}
    total = sum(p[0] for p in packets)
    avg_gap = sum(p[1] for p in packets) / len(packets)
    return {"packets": len(packets), "total_bytes": total, "avg_gap_ms": round(avg_gap, 2),
            "payload_inspected": False}
