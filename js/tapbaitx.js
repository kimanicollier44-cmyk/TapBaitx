"use strict";
/* TapBaitx - JavaScript port of the core models (Node, zero deps).
   Same rules as the Python core: synthetic fixtures only, consent-first. */
const crypto = require("crypto");

function formatNumber(raw) {
  let d = String(raw).replace(/\D/g, "");
  if (d.length === 11 && d.startsWith("1")) d = d.slice(1);
  if (d.length !== 10) throw new Error("need a 10-digit US number");
  return `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
}
function isSynthetic(raw) {
  let d = String(raw).replace(/\D/g, "");
  if (d.length === 11 && d.startsWith("1")) d = d.slice(1);
  return d.slice(3, 6) === "555";
}
function fuzz(lat, lon, level) {
  const places = { city: 1, neighborhood: 3, exact: 5 }[level];
  if (places === undefined) return null;
  const f = Math.pow(10, places);
  return [Math.round(lat * f) / f, Math.round(lon * f) / f];
}
function haversineKm(a, b) {
  const R = 6371, rad = x => x * Math.PI / 180;
  const h = Math.sin(rad(b[0] - a[0]) / 2) ** 2 +
    Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(rad(b[1] - a[1]) / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}
function detectFormat(buf) {
  if (buf.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) return "image/png";
  if (buf.subarray(0, 3).equals(Buffer.from([0xff, 0xd8, 0xff]))) return "image/jpeg";
  if (buf.toString("ascii", 0, 6).startsWith("GIF8")) return "image/gif";
  if (buf.length >= 8 && buf.toString("ascii", 4, 8) === "ftyp") return "video/mp4";
  return "application/octet-stream";
}
function fingerprint(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
function tileLayout(n, w = 1920, h = 1080) {
  if (n <= 0) return { cols: 0, rows: 0, tileW: 0, tileH: 0 };
  let cols = Math.ceil(Math.sqrt(n));
  const rows = Math.ceil(n / cols);
  return { cols, rows, tileW: Math.floor(w / cols), tileH: Math.floor(h / rows) };
}
module.exports = { formatNumber, isSynthetic, fuzz, haversineKm, detectFormat, fingerprint, tileLayout };

if (require.main === module) {
  const gif = Buffer.concat([Buffer.from("GIF89a"), Buffer.alloc(8)]);
  const checks = [
    ["phone format", formatNumber("2025550147") === "(202) 555-0147"],
    ["synthetic flag", isSynthetic("2025550147") === true],
    ["fuzz city", JSON.stringify(fuzz(34.0522, -118.2437, "city")) === "[34.1,-118.2]"],
    ["haversine LA-SF", haversineKm([34.05, -118.24], [37.77, -122.42]) > 500],
    ["detect gif", detectFormat(gif) === "image/gif"],
    ["fingerprint len", fingerprint(gif).length === 64],
    ["tiles 9", tileLayout(9).cols === 3],
  ];
  let passed = 0;
  for (const [name, ok] of checks) { console.log((ok ? "PASS " : "FAIL ") + name); if (ok) passed++; }
  console.log(`JS CHECKS ${passed}/${checks.length}`);
  process.exit(passed === checks.length ? 0 : 1);
}
