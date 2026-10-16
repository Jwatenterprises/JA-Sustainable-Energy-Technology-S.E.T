"""Build _build/parish_map.svg from geoBoundaries JAM ADM1 (simplified).
Source: geoBoundaries gbOpen JAM ADM1 (OpenStreetMap / Wambacher), CC BY-SA 2.0. The derived map is shared under the same licence.
Run: python _build/make_parish_map.py
"""
import json, math, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
geo = json.loads((HERE / "data" / "geoBoundaries-JAM-ADM1_simplified.geojson").read_text(encoding="utf-8"))
W, PAD, K = 1000, 12, math.cos(math.radians(18.1))


def rings(g):
    return [r for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]) for r in poly]


pts = [p for f in geo["features"] for r in rings(f["geometry"]) for p in r]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
s = (W - 2 * PAD) / ((x1 - x0) * K)
H = round((y1 - y0) * s + 2 * PAD)


def xy(p):
    return (p[0] - x0) * K * s + PAD, (y1 - p[1]) * s + PAD


out = []
for f in sorted(geo["features"], key=lambda f: f["properties"]["shapeName"]):
    name = f["properties"]["shapeName"].replace("Saint ", "St ")
    pid = re.sub(r"[^a-z]", "", name.lower())
    d = "".join("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in map(xy, r)) + "Z" for r in rings(f["geometry"]))
    out.append(f'<path data-parish="{pid}" d="{d}"><title>{name}</title></path>')
svg = (f'<svg class="parish-map" viewBox="0 0 {W} {H}" role="img" aria-label="Map of Jamaica\'s 14 parishes, shaded by average peak sun hours">'
       + "".join(out) + "</svg>")
(HERE / "parish_map.svg").write_text(svg, encoding="utf-8")
print(W, H, len(svg))
