"""Build setjamaica.com (Phase A: catalog skeleton, guides, reserve shop).
Pages live in _build/pages/*.html as body fragments with a header comment:
  <!-- title: ... | description: ... | path: shop/index.html | nav: shop -->
Run: python _build/build.py   (writes the .html files at the repo root)
Jekyll ignores _build/, so the sources are never published.
"""
import re, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "_build" / "pages"
SITE = "https://setjamaica.com"
WA_NUMBER = "18763561541"   # S.E.T. JA WhatsApp (from the current site; Wayne to confirm)
EMAIL = "info@setjamaica.com"
YEAR = datetime.date.today().year

NAV = [("shop", "Shop", "shop/"), ("guides", "Guides", "guides/"), ("diaspora", "Family Back Home", "diaspora.html"),
       ("order", "How to Order", "how-to-order.html"), ("contact", "Contact", "contact.html")]


def wa(text):
    from urllib.parse import quote
    return f"https://wa.me/{WA_NUMBER}?text={quote(text)}"


def layout(meta, body):
    depth = meta["path"].count("/")
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{href}"{" aria-current=\"page\"" if meta.get("nav") == key else ""}>{label}</a>'
        for key, label, href in NAV)
    canonical = SITE + "/" + meta["path"].replace("index.html", "")
    body = body.replace("{{up}}", up).replace("{{email}}", EMAIL)
    body = re.sub(r"\{\{wa:(.*?)\}\}", lambda m: wa(m.group(1)), body)
    return f"""<!doctype html>
<html lang="en-JM">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta['title']}</title>
<meta name="description" content="{meta['description']}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{meta['title']}">
<meta property="og:description" content="{meta['description']}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/logo.png">
<meta property="og:type" content="website">
<link rel="icon" type="image/png" sizes="32x32" href="{up}favicon-32.png">
<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{up}index.html"><img src="{up}images/logo-mark.png" alt="" width="44" height="44"><span>S.E.T. <small>Jamaica</small></span></a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="primary-nav">Menu</button>
    <nav id="primary-nav" class="nav" aria-label="Primary">{nav}</nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <p class="footer-brand">S.E.T. Sustainable Energy Technology in Jamaica</p>
      <p>Solar batteries, power stations and solar gear, stocked in Kingston. Every AC product is checked for Jamaica's 110V / 50Hz grid.</p>
    </div>
    <div>
      <p class="footer-head">Shop</p>
      <a href="{up}shop/">All products</a><a href="{up}how-to-order.html">How to order</a><a href="{up}diaspora.html">Family back home</a><a href="{up}warranty.html">Warranty &amp; returns</a>
    </div>
    <div>
      <p class="footer-head">Learn</p>
      <a href="{up}guides/50hz-power-stations-jamaica.html">Will it work on 50Hz?</a><a href="{up}guides/sizing.html">What size do I need?</a><a href="{up}guides/hurricane-prep.html">Hurricane power checklist</a><a href="{up}blog/">Blog</a>
    </div>
    <div>
      <p class="footer-head">Contact</p>
      <a href="{wa('Hi S.E.T. Jamaica, I have a question.')}">WhatsApp</a><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{up}about.html">About</a><a href="{up}privacy-policy.html">Privacy</a><a href="{up}terms.html">Terms</a>
    </div>
  </div>
  <p class="wrap copyright">&copy; {YEAR} S.E.T. Sustainable Energy Technology in Jamaica. Prices in Jamaican dollars (J$).</p>
</footer>
<script>
document.querySelector('.menu-toggle').addEventListener('click', function () {{
  var nav = document.getElementById('primary-nav');
  var open = nav.classList.toggle('open');
  this.setAttribute('aria-expanded', open);
}});
</script>
</body>
</html>
"""


def main():
    built = []
    for src in sorted(PAGES.glob("*.html")):
        raw = src.read_text(encoding="utf-8")
        head = re.match(r"<!--(.*?)-->\s*", raw, re.S)
        keys = "title|description|path|nav"
        meta = dict(re.findall(rf"({keys}):\s*(.*?)\s*(?=\|\s*(?:{keys}):|$)", head.group(1).strip(), re.S))
        out = ROOT / meta["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout(meta, raw[head.end():]), encoding="utf-8")
        built.append(meta["path"])
    urls = "".join(f"  <url><loc>{SITE}/{p.replace('index.html', '')}</loc></url>\n" for p in built if p != "404.html")
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n',
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("\n".join(built))


if __name__ == "__main__":
    main()
