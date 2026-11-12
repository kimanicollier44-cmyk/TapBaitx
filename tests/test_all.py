import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tapbaitx import phone, taplab, facetime_lab, geoearth, media_tracker, council, gates
import pytest

def test_phone():
    assert phone.format_number("1-202-555-0147") == "(202) 555-0147"
    assert phone.is_synthetic("2025550147")
    with pytest.raises(ValueError):
        phone.normalize_number("123")

def test_tap_requires_fixture_and_auth():
    real = taplab.FixtureLine("R1", "(202) 867-5309", synthetic=False)
    with pytest.raises(taplab.HoldError):
        taplab.open_tap(real, "case-1")
    fix = taplab.FixtureLine("F1", "(202) 555-0147", True, [("A", "hi hi"), ("B", "hi")])
    with pytest.raises(taplab.HoldError):
        taplab.open_tap(fix, "")
    assert taplab.analyse_transcript(fix)["turns"] == 2

def test_facetime_visibility_and_metadata():
    p = facetime_lab.Participant("X"); p.joined = True
    assert p.visible() is False
    p.camera_on = True
    assert p.visible() is True
    assert facetime_lab.metadata_summary([])["packets"] == 0
    assert facetime_lab.tile_layout(16)["cols"] == 4

def test_geo_consent_and_fuzz():
    assert geoearth.fuzz(34.0522, -118.2437, "city") == (34.1, -118.2)
    assert geoearth.make_kml("x", [("A", 1.0, 2.0)], geoearth.Consent(False)) is None
    assert geoearth.track_distance_km([(0, 0), (0, 1)]) > 100

def test_media_tracker():
    gif = b"GIF89a" + b"\x21\xf9" * 4
    assert media_tracker.detect_format(gif) == "image/gif"
    assert media_tracker.gif_frames(gif) == 4
    mp4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 4
    assert media_tracker.detect_format(mp4) == "video/mp4"
    no_consent = media_tracker.MediaItem("x.gif", gif, "gif", exif_gps=(34.05, -118.24), owner_consent=False)
    assert no_consent.record()["location"] is None

def test_council_and_gates():
    assert council.carbon_decide("q", tier=32768)["live_call"] is False
    with pytest.raises(ValueError):
        council.carbon_decide("q", tier=123)
    assert gates.is_held("live_wiretap_real_line")
    assert len(gates.all_gates()) == 14
