"""Google Earth location - consent-first, OFF by default (pattern from LiveShareX v1.3.0).
Own location only, fuzzed BEFORE export, REAL KML. Live API calls HOLD-gated."""
import math
from xml.etree import ElementTree as ET

PRECISION = {"off": None, "city": 1, "neighborhood": 3, "exact": 5}
# city = ~1 decimal (~11 km), neighborhood = 3 decimals (~110 m), exact = private only

class Consent:
    def __init__(self, sharing=False, level="city"):
        self.sharing = sharing
        self.level = level

def fuzz(lat, lon, level):
    places = PRECISION[level]
    if places is None:
        return None
    return (round(lat, places), round(lon, places))

def haversine_km(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = math.radians(b[0]-a[0]); dl = math.radians(b[1]-a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(h))

def track_distance_km(points):
    return sum(haversine_km(points[i], points[i+1]) for i in range(len(points)-1))

def make_kml(name, points, consent):
    """points: [(label, lat, lon), ...] - returns KML string or None if consent off."""
    if not consent.sharing:
        return None
    kml = ET.Element("kml", {"xmlns": "http://www.opengis.net/kml/2.2"})
    doc = ET.SubElement(kml, "Document")
    ET.SubElement(doc, "name").text = name
    for label, lat, lon in points:
        f = fuzz(lat, lon, consent.level)
        if f is None:
            continue
        pm = ET.SubElement(doc, "Placemark")
        ET.SubElement(pm, "name").text = label
        pt = ET.SubElement(ET.SubElement(pm, "Point"), "coordinates")
        pt.text = f"{f[1]},{f[0]},0"
    text = ET.tostring(kml, encoding="unicode")
    ET.fromstring(text)  # validate XML before return
    return text
