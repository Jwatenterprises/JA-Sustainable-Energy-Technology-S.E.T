"""Build setjamaica.com (design system v2, 2026-10-05).
Pages live in _build/pages/*.html as body fragments with a header comment:
  <!-- title: ... | description: ... | path: shop/index.html | nav: shop -->
Placeholders inside pages:
  {{up}}  {{email}}  {{wa:prefilled text}}  {{reserve_form}}  {{products:<line>}}  {{address}}
Catalog data: _build/products.json (prices/status/payment links). A product page
(shop/<slug>.html) is generated only for products that have real photos.
Run: python _build/build.py   (writes the .html files at the repo root)
Jekyll ignores _build/, so the sources are never published.
"""
import re, json, html, pathlib, datetime
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "_build" / "pages"
PRODUCTS = json.loads((ROOT / "_build" / "products.json").read_text(encoding="utf-8"))["products"]
SITE = "https://setjamaica.com"
WA_NUMBER = "18574459407"   # Wayne's WhatsApp, temporary (2026-10-05); swap for the JA business line later
EMAIL = "info@setjamaica.com"
ADDRESS = "11 Hill View Avenue, Kingston 10, Jamaica"
FORM_ENDPOINT = "https://formsubmit.co/ajax/1aa6a339d1afc580d4f6abe8fc176a5c"   # FormSubmit alias for info@setjamaica.com (activated 2026-10-05)
YEAR = datetime.date.today().year
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800"
         "&family=Plus+Jakarta+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap")

NAV = [("shop", "Shop", "shop/"), ("sizing", "What size do I need?", "guides/sizing.html"),
       ("hurricane", "Hurricane ready", "guides/hurricane-prep.html"), ("diaspora", "Send power home", "diaspora.html"),
       ("order", "How to order", "how-to-order.html"), ("guides", "Guides", "guides/")]
LINES = {"power-stations": "Power station", "batteries": "Home battery", "everyday-solar": "Everyday solar"}


def wa(text):
    return f"https://wa.me/{WA_NUMBER}?text={quote(text)}"


def esc(s):
    return html.escape(str(s), quote=True)


def jmd(n):
    return f"J${n:,.0f}"


def product_card(p, up):
    has_page = bool(p.get("photos"))
    href = f'{up}shop/{p["slug"]}.html' if has_page else None
    pic = (f'<div class="pic"><img src="{up}{esc(p["photos"][0])}" alt="{esc(p["name"])}" loading="lazy"></div>'
           if has_page else "")
    tag = '<span class="badge-50">50Hz-verified</span>' if p["line"] == "power-stations" else ""
    specs = "".join(f'<span class="spec">{esc(s)}</span>' for s in p.get("specs", []))
    if p["status"] == "selling" and p.get("price_jmd"):
        price = f'<span class="price num">{jmd(p["price_jmd"])}</span>'
        cta = (f'<a class="btn btn-primary" href="{href}">Buy</a>' if href else
               f'<a class="btn btn-wa" href="{wa("Hi S.E.T. Jamaica, I would like to order the " + p["name"] + ". My parish is: ")}">Order on WhatsApp</a>')
    elif p["status"] == "sold_out":
        price = '<span class="price-tba">Sold out, more coming</span>'
        cta = f'<a class="btn btn-ghost" href="{wa("Hi S.E.T. Jamaica, please tell me when the " + p["name"] + " is back.")}">Notify me</a>'
    else:
        price = f'<span class="price-tba">Lands {esc(p.get("eta", "soon"))}</span>'
        cta = f'<a class="btn btn-ghost" href="#reserve" data-item="{esc(p["name"])}">Reserve</a>'
    title = f'<a href="{href}">{esc(p["name"])}</a>' if href else esc(p["name"])
    return f"""<article class="card pcard">{pic}
  <div class="body"><span class="line">{esc(p.get("kicker", LINES[p["line"]]))}</span>{tag and f'<div>{tag}</div>'}
    <h3>{title}</h3><div class="specs">{specs}</div><p class="runs">{esc(p.get("runs", ""))}</p>
    <div class="foot">{price}{cta}</div></div></article>"""


def products_grid(line, up):
    items = [p for p in PRODUCTS if p["line"] == line and p["status"] != "hidden"]
    return '<div class="grid-4">' + "".join(product_card(p, up) for p in items) + "</div>"


def reserve_form():
    opts = "".join(f"<option>{esc(p['name'])}</option>" for p in PRODUCTS if p["status"] == "reserve")
    parishes = ["Kingston", "St Andrew", "St Catherine", "Clarendon", "Manchester", "St Elizabeth", "Westmoreland",
                "Hanover", "St James", "Trelawny", "St Ann", "St Mary", "Portland", "St Thomas"]
    popts = "".join(f"<option>{x}</option>" for x in parishes) + "<option>I live abroad (it's for family)</option>"
    return f"""<form class="form" id="reserve-form" data-endpoint="{FORM_ENDPOINT}" novalidate>
  <label for="r-name">Your name<input id="r-name" name="name" autocomplete="name" required></label>
  <div class="row2">
    <label for="r-phone">WhatsApp number<input id="r-phone" name="whatsapp" inputmode="tel" autocomplete="tel" placeholder="876-555-0123" required></label>
    <label for="r-parish">Parish<select id="r-parish" name="parish">{popts}</select></label>
  </div>
  <label for="r-item">What are you interested in?<select id="r-item" name="item">{opts}<option>Not sure yet, please advise</option></select></label>
  <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
  <button class="btn btn-primary" type="submit">Reserve my spot</button>
  <p class="fine" style="margin:0">No payment now. We'll message you on WhatsApp when it lands in Kingston.</p>
  <div class="form-msg" id="reserve-msg" role="status" hidden></div>
</form>"""


FORM_JS = """
(function () {
  var f = document.getElementById('reserve-form'); if (!f) return;
  var msg = document.getElementById('reserve-msg');
  var params = new URLSearchParams(location.search); var want = params.get('item');
  document.querySelectorAll('[data-item]').forEach(function (a) { a.addEventListener('click', function () {
    var s = document.getElementById('r-item'); for (var i = 0; i < s.options.length; i++) if (s.options[i].text === a.dataset.item) s.selectedIndex = i; }); });
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!f.name.value.trim() || !f.whatsapp.value.trim()) { msg.hidden = false; msg.className = 'form-msg err'; msg.textContent = 'Please add your name and WhatsApp number.'; return; }
    var data = { name: f.name.value, whatsapp: f.whatsapp.value, parish: f.parish.value, item: f.item.value,
      _subject: 'New reservation: ' + f.item.value, _template: 'table', _captcha: 'false', _honey: f._honey.value };
    f.querySelector('button').disabled = true;
    fetch(f.dataset.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json(); })
      .then(function (j) { if (String(j.success) !== 'true') throw 0;
        msg.hidden = false; msg.className = 'form-msg ok'; msg.textContent = 'You\\u2019re on the list. We\\u2019ll message you on WhatsApp when it lands.'; f.reset(); })
      .catch(function () { msg.hidden = false; msg.className = 'form-msg err';
        msg.innerHTML = 'That didn\\u2019t go through. Please <a href="WA_LINK">reserve on WhatsApp</a> instead.'; })
      .finally(function () { f.querySelector('button').disabled = false; });
  });
})();
"""


def layout(meta, body):
    depth = meta["path"].count("/")
    up = "../" * depth
    nav = "".join(
        f'<a href="{up}{href}"{" aria-current=\"page\"" if meta.get("nav") == key else ""}>{label}</a>'
        for key, label, href in NAV)
    canonical = SITE + "/" + meta["path"].replace("index.html", "")
    body = body.replace("{{reserve_form}}", reserve_form())
    body = re.sub(r"\{\{products:([a-z-]+)\}\}", lambda m: products_grid(m.group(1), up), body)
    body = body.replace("{{up}}", up).replace("{{email}}", EMAIL).replace("{{address}}", ADDRESS)
    body = re.sub(r"\{\{wa:(.*?)\}\}", lambda m: wa(m.group(1)), body)
    extra_head = meta.get("head", "")
    js = FORM_JS.replace("WA_LINK", wa("Hi S.E.T. Jamaica, please reserve for me: ")) if "reserve-form" in body else ""
    return f"""<!doctype html>
<html lang="en-JM">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{meta['title']}</title>
<meta name="description" content="{meta['description']}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{meta['title']}">
<meta property="og:description" content="{meta['description']}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/logo.png">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0F3D2E">
<link rel="icon" type="image/png" sizes="32x32" href="{up}favicon-32.png">
<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{up}assets/site.css">
{extra_head}
</head>
<body>
<div class="util"><div class="wrap"><span>Island-wide delivery</span><span>Pay by card, Lynk, bank transfer or PayPal</span><span>{ADDRESS.replace(", Jamaica", "")}</span></div></div>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{up}index.html" aria-label="S.E.T. Sustainable Energy Technology in Jamaica, home"><picture><source srcset="{up}images/logo-lockup.webp" type="image/webp"><img src="{up}images/logo-lockup.png" alt="Sustainable Energy Technology S.E.T. logo" width="554" height="180"></picture></a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="primary-nav">Menu</button>
    <nav id="primary-nav" class="nav" aria-label="Primary">{nav}</nav>
    <div class="header-cta"><a class="btn btn-wa" href="{wa('Hi S.E.T. Jamaica, ')}">WhatsApp us</a></div>
  </div>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <picture><source srcset="{up}images/logo-full.webp" type="image/webp"><img class="footer-logo" src="{up}images/logo-full.png" alt="Sustainable Energy Technology S.E.T. logo" width="300" height="421" loading="lazy"></picture>
      <p class="footer-brand">S.E.T. Sustainable Energy Technology in Jamaica</p>
      <p>Solar batteries, power stations and solar gear, stocked in Kingston. Every AC product is checked for Jamaica's 110V / 50Hz grid.</p>
      <p>{ADDRESS}<br>Pickup by appointment</p>
    </div>
    <div>
      <p class="footer-head">Shop</p>
      <a href="{up}shop/#power-stations">Power stations</a><a href="{up}shop/#batteries">Home batteries</a><a href="{up}shop/#everyday-solar">Everyday solar</a><a href="{up}diaspora.html">Send power home</a>
    </div>
    <div>
      <p class="footer-head">Help</p>
      <a href="{up}how-to-order.html">How to order &amp; pay</a><a href="{up}warranty.html">Warranty &amp; returns</a><a href="{up}guides/50hz-power-stations-jamaica.html">Will it work on 50Hz?</a><a href="{up}guides/sizing.html">What size do I need?</a><a href="{up}blog/">Blog</a>
    </div>
    <div>
      <p class="footer-head">Contact</p>
      <a href="{wa('Hi S.E.T. Jamaica, I have a question.')}">WhatsApp 857-445-9407</a><a href="mailto:{EMAIL}">{EMAIL}</a><a href="{up}about.html">About</a><a href="{up}contact.html">Contact</a><a href="{up}privacy-policy.html">Privacy</a><a href="{up}terms.html">Terms</a>
    </div>
  </div>
  <p class="wrap copyright">&copy; {YEAR} S.E.T. Sustainable Energy Technology in Jamaica. Prices in Jamaican dollars (J$), GCT included.</p>
</footer>
<div class="mbar"><a class="btn btn-wa" href="{wa('Hi S.E.T. Jamaica, ')}">WhatsApp</a><a class="btn btn-primary" href="{up}index.html#reserve">Reserve now</a></div>
<script>
document.querySelector('.menu-toggle').addEventListener('click', function () {{
  var nav = document.getElementById('primary-nav');
  var open = nav.classList.toggle('open');
  this.setAttribute('aria-expanded', open);
}});
{js}
</script>
</body>
</html>
"""


def product_page(p):
    """Timeline 3/4: generated only when real photos exist. Payment buttons appear when status == selling."""
    specs = "".join(f'<span class="spec">{esc(s)}</span>' for s in p.get("specs", []))
    gallery = "".join(f'<img src="../{esc(x)}" alt="{esc(p["name"])} photo {i + 1}" loading="lazy">' for i, x in enumerate(p["photos"]))
    order_text = f"Hi S.E.T. Jamaica, I'd like to order the {p['name']}. Qty: 1. My parish is: "
    if p["status"] == "selling" and p.get("price_jmd"):
        price = f'<p class="price num" style="font-size:2rem">{jmd(p["price_jmd"])}</p>'
        pay = p.get("pay", {})
        btns = [f'<a class="btn btn-wa" href="{wa(order_text)}">Order on WhatsApp (Lynk / bank transfer)</a>']
        if pay.get("card_link"):
            btns.append(f'<a class="btn btn-primary" href="{esc(pay["card_link"])}" rel="noopener">Pay by card</a>')
        if pay.get("paypal_link"):
            btns.append(f'<a class="btn btn-ghost" href="{esc(pay["paypal_link"])}" rel="noopener">Pay with PayPal (US$)</a>')
        offer = {"@type": "Offer", "price": p["price_jmd"], "priceCurrency": "JMD", "availability": "https://schema.org/InStock"}
    else:
        price = f'<p class="price-tba">Lands {esc(p.get("eta", "soon"))}. Reserve now, pay nothing until it arrives.</p>'
        btns = ['<a class="btn btn-primary" href="../index.html#reserve">Reserve</a>',
                f'<a class="btn btn-wa" href="{wa("Hi S.E.T. Jamaica, please reserve the " + p["name"] + " for me.")}">Reserve on WhatsApp</a>']
        offer = {"@type": "Offer", "priceCurrency": "JMD", "availability": "https://schema.org/PreOrder"}
    ld = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": p["name"], "sku": p["sku"],
                     "image": [f"{SITE}/{x}" for x in p["photos"]], "brand": {"@type": "Brand", "name": "S.E.T. Jamaica"},
                     "offers": {**offer, "url": f"{SITE}/shop/{p['slug']}.html"}})
    body = f"""<section class="section"><div class="wrap grid-2" style="align-items:start">
  <div class="card" style="padding:12px">{gallery}</div>
  <div><p class="eyebrow">{esc(p.get("kicker", ""))}</p><h1>{esc(p["name"])}</h1>
    {'<p><span class="badge-50">50Hz-verified for Jamaica</span></p>' if p["line"] == "power-stations" else ""}
    <div class="specs">{specs}</div><p class="lead" style="margin-top:1rem">{esc(p.get("runs", ""))}</p>{price}
    <div class="btn-row">{''.join(btns)}</div>
    <p class="small muted" style="margin-top:1rem">Delivery island-wide, priced by parish. Pickup at {ADDRESS} by appointment. <a href="../how-to-order.html">How ordering works</a>.</p>
  </div></div></section>"""
    meta = {"title": f"{p['name']} | S.E.T. Jamaica", "description": f"{p['name']}: {p.get('runs', '')} Stocked in Kingston.",
            "path": f"shop/{p['slug']}.html", "nav": "shop", "head": f'<script type="application/ld+json">{ld}</script>'}
    return meta, body


def main():
    built = []
    for src in sorted(PAGES.glob("*.html")):
        raw = src.read_text(encoding="utf-8")
        head = re.match(r"<!--(.*?)-->\s*", raw, re.S)
        keys = "title|description|path|nav"
        meta = dict(re.findall(rf"({keys}):\s*(.*?)\s*(?=\|\s*(?:{keys}):|$)", head.group(1).strip(), re.S))
        if meta["path"] == "index.html":
            meta["head"] = '<script type="application/ld+json">' + json.dumps({
                "@context": "https://schema.org", "@type": "Store", "name": "S.E.T. Sustainable Energy Technology in Jamaica",
                "url": SITE, "email": EMAIL, "telephone": "+1-857-445-9407", "image": f"{SITE}/logo.png",
                "address": {"@type": "PostalAddress", "streetAddress": "11 Hill View Avenue", "addressLocality": "Kingston 10",
                            "addressRegion": "Kingston", "addressCountry": "JM"}}) + "</script>"
        out = ROOT / meta["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(layout(meta, raw[head.end():]), encoding="utf-8")
        built.append(meta["path"])
    for p in PRODUCTS:
        if p.get("photos") and p["status"] != "hidden":
            meta, body = product_page(p)
            (ROOT / meta["path"]).write_text(layout(meta, body), encoding="utf-8")
            built.append(meta["path"])
    urls = "".join(f"  <url><loc>{SITE}/{p.replace('index.html', '')}</loc></url>\n" for p in built if p != "404.html")
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n',
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("\n".join(built))


if __name__ == "__main__":
    main()
