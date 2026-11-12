"""TapBaitx - entry point + self-checks.
Consent-first phone / cell / FaceTime-style / location / media tracker lab.
Synthetic fixtures only. Every live capability is HOLD-gated.
Run: python3 main.py          (demo + CHECKS)
     python3 -m pytest -q     (test suite)"""
import sys
from tapbaitx import phone, taplab, facetime_lab, geoearth, media_tracker, council, gates

def run_checks():
    checks = []
    def check(name, ok):
        checks.append((name, bool(ok)))
    # phone
    check("phone format", phone.format_number("2025550147") == "(202) 555-0147")
    check("phone synthetic flag", phone.is_synthetic("2025550147") is True)
    log = phone.synthetic_call_log()
    check("call log all synthetic", all(c["synthetic"] for c in log))
    check("call totals", phone.call_totals(log)["calls"] == len(log))
    # tap chamber
    line = taplab.FixtureLine("FIX-1", "(202) 555-0147", True,
        [("A", "meet at noon noon"), ("B", "noon works")])
    try:
        taplab.open_tap(line, "")
        denied = False
    except taplab.HoldError:
        denied = True
    check("tap denied without authorization", denied)
    sess = taplab.open_tap(line, "own-device-consent-001")
    check("tap synthetic session, no live audio", sess["authorized"] and sess["live_audio"] is False)
    check("transcript analysis", taplab.analyse_transcript(line)["top_words"][0] == ("noon", 3))
    # facetime-style lab
    check("tile layout 9 = 3 cols", facetime_lab.tile_layout(9)["cols"] == 3)
    p = facetime_lab.Participant("Friend")
    check("not visible before join+camera", p.visible() is False)
    p.joined = True; p.camera_on = True
    check("visible after join+camera on", p.visible() is True)
    md = facetime_lab.metadata_summary([(1200, 20), (900, 40)])
    check("facetime metadata only", md["payload_inspected"] is False and md["total_bytes"] == 2100)
    # geoearth
    check("consent off = no KML", geoearth.make_kml("t", [("A", 34.0522, -118.2437)], geoearth.Consent(False)) is None)
    kml = geoearth.make_kml("t", [("A", 34.0522, -118.2437)], geoearth.Consent(True, "city"))
    check("KML city-fuzzed (exact absent)", "34.0522" not in kml and "34.1" in kml)
    check("haversine LA->SF sane", 500 < geoearth.haversine_km((34.05, -118.24), (37.77, -122.42)) < 600)
    # media tracker
    gif = b"GIF89a" + b"\x21\xf9" * 3 + b"\x00" * 8
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
    check("detect gif", media_tracker.detect_format(gif) == "image/gif")
    check("detect png", media_tracker.detect_format(png) == "image/png")
    check("gif frames counted", media_tracker.gif_frames(gif) == 3)
    item = media_tracker.MediaItem("a.gif", gif, "gif", frames=3,
        exif_gps=(34.0522, -118.2437), owner_consent=True, taken_at="2026-11-11T09:00:00")
    rec = item.record(public=True)
    check("media location city-fuzzed only", rec["location"] == (34.1, -118.2))
    item2 = media_tracker.MediaItem("copy.gif", gif, "gif", frames=3, taken_at="2026-11-11T10:00:00")
    tr = media_tracker.track_media([item, item2])
    check("media dedupe by fingerprint", tr["unique"] == 1 and tr["duplicates"] == ["copy.gif"])
    check("video motion model", media_tracker.video_motion([0.1, 0.12, 0.9])["scene_changes"] == 1)
    check("strip plan does not apply itself", media_tracker.strip_metadata_plan(item)["applied"] is False)
    # council + gates
    c = council.council("Is this tap authorized?", risk="hold")
    check("council HOLD wins", c["final"] == "HOLD" and c["decider"]["live_call"] is False)
    check("muse advisor authority none", c["advisor"]["authority"] == "none" and len(c["advisor"]["advice"]) == 4)
    check("14 HOLD gates", len(gates.all_gates()) == 14)
    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    print(f"CHECKS {passed}/{len(checks)}")
    return passed == len(checks)

def demo():
    print("TapBaitx v1.0.0 - synthetic demo")
    print("Phone:", phone.format_number("2025550147"), "| synthetic:", phone.is_synthetic("2025550147"))
    print("Gates held:", len(gates.all_gates()))
    return run_checks()

if __name__ == "__main__":
    sys.exit(0 if demo() else 1)
