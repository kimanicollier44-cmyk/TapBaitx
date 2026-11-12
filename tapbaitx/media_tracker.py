"""Image / GIF / video tracker - for media the owner supplies.
Real format detection by magic bytes, real SHA-256 fingerprints,
GIF/video frame + timeline models, and owner-consent EXIF location:
exact GPS is never exported publicly (city-fuzzed, like geoearth.py),
and a strip-metadata plan is produced so the owner can remove it."""
import hashlib
from .geoearth import fuzz

MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"), (b"GIF89a", "image/gif"),
    (b"RIFF", "image/webp"),
]

def detect_format(data: bytes):
    for magic, mime in MAGIC:
        if data.startswith(magic):
            return mime
    if len(data) >= 8 and data[4:8] == b"ftyp":
        return "video/mp4"
    return "application/octet-stream"

def fingerprint(data: bytes):
    return hashlib.sha256(data).hexdigest()

def gif_frames(data: bytes):
    """Real GIF frame count: count Graphic Control / Image Descriptor markers
    in a GIF byte stream (0x2C image separator at block level is approximated
    by counting 0x21 0xF9 graphic-control extensions, one per frame)."""
    if not (data.startswith(b"GIF87a") or data.startswith(b"GIF89a")):
        return 0
    return max(1, data.count(b"\x21\xf9"))

class MediaItem:
    def __init__(self, name, data, kind, frames=1, duration_s=0.0,
                 exif_gps=None, owner_consent=False, taken_at=""):
        self.name = name; self.data = data; self.kind = kind  # image|gif|video
        self.frames = frames; self.duration_s = duration_s
        self.exif_gps = exif_gps; self.owner_consent = owner_consent
        self.taken_at = taken_at
    def record(self, public=True):
        rec = {"name": self.name, "kind": self.kind,
               "format": detect_format(self.data),
               "sha256": fingerprint(self.data),
               "bytes": len(self.data), "frames": self.frames,
               "duration_s": self.duration_s, "taken_at": self.taken_at,
               "location": None}
        if self.exif_gps and self.owner_consent:
            level = "city" if public else "exact"
            rec["location"] = fuzz(self.exif_gps[0], self.exif_gps[1], level)
        return rec

def track_media(items, public=True):
    """Timeline + dedupe by fingerprint. Duplicate bytes = same fingerprint."""
    records = [it.record(public=public) for it in items]
    records.sort(key=lambda r: r["taken_at"] or r["name"])
    seen, dupes = set(), []
    for r in records:
        if r["sha256"] in seen:
            dupes.append(r["name"])
        seen.add(r["sha256"])
    return {"items": records, "count": len(records),
            "unique": len(seen), "duplicates": dupes}

def video_motion(frames_luminance):
    """Scene/motion model from per-frame average luminance supplied by caller."""
    if len(frames_luminance) < 2:
        return {"frames": len(frames_luminance), "scene_changes": 0, "motion": 0.0}
    diffs = [abs(frames_luminance[i+1]-frames_luminance[i]) for i in range(len(frames_luminance)-1)]
    return {"frames": len(frames_luminance),
            "scene_changes": sum(1 for d in diffs if d >= 0.25),
            "motion": round(sum(diffs)/len(diffs), 4)}

def strip_metadata_plan(item):
    return {"name": item.name, "removes": ["exif_gps", "device_make_model",
            "taken_at_original"], "keeps": ["pixel_data", "sha256_fingerprint"],
            "applied": False}
