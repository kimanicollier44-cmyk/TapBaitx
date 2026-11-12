"""HOLD gates - every live / non-consensual capability is held by default."""
GATES = {
    "live_wiretap_real_line": "Interception of a real phone line is HOLD - lab uses synthetic fixture lines only.",
    "covert_interception": "Covert interception of another person is HOLD, permanently.",
    "facetime_interception_decryption": "Decrypting or tapping real FaceTime traffic is HOLD - lab models metadata only, on synthetic captures.",
    "tracking_another_person": "Tracking another person's location is HOLD - location is own-device, opt-in only.",
    "carrier_network_access": "Accessing carrier / SS7 / Diameter networks is HOLD, names only.",
    "imsi_catcher": "IMSI catcher / stingray operation is HOLD, names only.",
    "call_recording_without_consent": "Recording a real call without all-party consent notice is HOLD.",
    "live_location_api_call": "Live Google Earth / Maps calls are HOLD until a key is supplied (name only) AND consent is on.",
    "live_gemini_api_call": "Live Gemini Carbon 4 calls are HOLD - council seat is offline, names only.",
    "live_muse_api_call": "Live Muse calls are HOLD - advisor seat is offline, names only.",
    "media_upload_external": "Uploading tracked media to an external service is HOLD.",
    "exact_location_public_share": "Sharing exact coordinates publicly is HOLD - public output is city-fuzzed.",
    "child_location_sharing": "Sharing a child's location is HOLD.",
    "exif_location_of_others_media": "Reading location from another person's media without their consent is HOLD.",
}
def all_gates():
    return dict(GATES)
def is_held(name):
    return name in GATES
