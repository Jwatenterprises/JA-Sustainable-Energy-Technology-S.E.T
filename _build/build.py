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
SOCIALS = [("Facebook", "https://www.facebook.com/setjamaica876"),   # Page created 2026-10-16 (id 61595609425070)
           ("YouTube", "https://www.youtube.com/@S.E.T.JAMAICA"),
           ("TikTok", "https://www.tiktok.com/@setjamaica876")]   # Business account, created 2026-10-17
FORM_ENDPOINT = "https://formsubmit.co/ajax/1aa6a339d1afc580d4f6abe8fc176a5c"   # FormSubmit alias for info@setjamaica.com (activated 2026-10-05)
YEAR = datetime.date.today().year
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800"
         "&family=Plus+Jakarta+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap")

NAV = [("shopship", "Shop & Ship", "shop-and-ship.html"), ("shop", "50Hz picks", "shop/"),
       ("sizing", "What size do I need?", "guides/sizing.html"), ("hurricane", "Hurricane ready", "guides/hurricane-prep.html"),
       ("ebikes", "E-bikes", "shop/#ebikes"), ("diaspora", "Send power home", "diaspora.html"), ("guides", "Guides", "guides/")]
# Shop & Ship model (2026-10-15): S.E.T. recommends 50Hz-verified US models and earns an affiliate commission;
# the buyer purchases from the US store and ships it home with Dennis Shipping as a personal import.
# Prices are what the brand store showed on PICKS_CHECKED; the button always opens today's price.
PICKS_CHECKED = "Oct 15, 2026"
AWIN = "https://www.awin1.com/cread.php?awinaffid=2881111&awinmid="
RENOGY = "https://renogy.sjv.io/c/6782322/1182656/14864?u=https%3A%2F%2Fwww.renogy.com%2Fproducts%2F"   # Impact, approved
VENTALLION = "https://ventallioncom.pxf.io/c/7998062/3869060/51724?partnerpropertyid=9027147&u=https%3A%2F%2Fventallion.com%2Fproducts%2F"   # Impact acct 7998062, approved 10/19
PICKS = [
    {"name": "EcoFlow DELTA 2 Max", "kicker": "Best for a whole-home outage", "img": "images/picks/ecoflow-delta-2-max.webp",
     "specs": ["2,048 Wh", "2,400 W", "LiFePO4", "50/60Hz in & out"],
     "runs": "Fridge, 2 fans, TV and Wi-Fi (about 300 W) for roughly 6 hours.", "price": "US$1,049", "store": "EcoFlow US store",
     "url": AWIN + "59181&ued=https%3A%2F%2Fus.ecoflow.com%2Fproducts%2Fdelta-2-max-portable-power-station&clickref=setja-picks"},
    {"name": "BLUETTI AC180", "kicker": "Best value", "img": "images/picks/bluetti-ac180.webp",
     "specs": ["1,152 Wh", "1,800 W", "LiFePO4", "50/60Hz switchable"],
     "runs": "Fans, LED lights and Wi-Fi (about 150 W) for roughly 6 hours. Set it to 50Hz once (2-button switch).", "price": "US$499", "store": "BLUETTI US store",
     "url": AWIN + "59271&ued=https%3A%2F%2Fwww.bluettipower.com%2Fproducts%2Fac180&clickref=setja-picks"},
    {"name": "EcoFlow DELTA 2", "kicker": "Mid-size backup", "img": "images/picks/ecoflow-delta-2.webp",
     "specs": ["1,024 Wh", "1,800 W", "LiFePO4", "50/60Hz in & out"],
     "runs": "Fridge and a fan (about 150 W) for roughly 5 hours. No longer on EcoFlow's US store, so compare sellers on Amazon.", "price": "Varies", "store": "Amazon",
     "url": "https://www.amazon.com/s?k=EcoFlow+DELTA+2+Portable+Power+Station&tag=sunenergytec2-20"},
    {"name": "BLUETTI 200W Solar Panel", "kicker": "Recharge from the sun", "img": "images/picks/bluetti-200w-solar-panel.webp",
     "specs": ["200 W", "Folding", "DC: no 50Hz issue"],
     "runs": "Recharges a power station when the grid is down for days.", "price": "US$399", "store": "BLUETTI US store",
     "url": AWIN + "59271&ued=https%3A%2F%2Fwww.bluettipower.com%2Fproducts%2Fbluetti-sp200l-solar-panel-200w&clickref=setja-picks"},
]
# Solar lifestyle picks (2026-10-16): DC/USB gear (or a universal 100-240V 50/60Hz adapter), so the 50Hz rule doesn't apply.
# Brand-store items only, official images from the brand's own store; Amazon items wait for an approved image source.
LIFESTYLE_CHECKED = "Oct 16, 2026"
LIFESTYLE = [
    {"name": "EcoFlow GLACIER Classic 35L", "kicker": "Solar fridge-freezer", "img": "images/picks/ecoflow-glacier-classic-35l.webp",
     "specs": ["35 L", "12V / solar / AC", "Fridge or freezer"],
     "runs": "Keeps food cold through outages and beach days. Its AC adapter is rated 100–240V 50/60Hz; add the plug-in battery for about 43 hours off-grid.",
     "price": "From US$699", "store": "EcoFlow US store",
     "url": AWIN + "59181&ued=https%3A%2F%2Fus.ecoflow.com%2Fproducts%2Fecoflow-glacier-classic-portable-fridge-freezer%3Fvariant%3D42093688913993&clickref=setja-lifestyle"},
    {"name": "EcoFlow TRAIL 300 DC + 45W solar panel", "kicker": "Fans, lights & phones", "img": "images/picks/ecoflow-trail-300-dc-45w-solar.webp",
     "specs": ["288 Wh", "USB-C / DC only", "45 W panel"],
     "runs": "A pure-DC kit for USB fans, LED lights, Wi-Fi and phones. No AC outlet, so no 50Hz question.",
     "price": "US$219", "store": "EcoFlow US store",
     "url": AWIN + "59181&ued=https%3A%2F%2Fus.ecoflow.com%2Fproducts%2Ftrail-series%3Fvariant%3D54590654808137&clickref=setja-lifestyle"},
    {"name": "ALLPOWERS PB100 + 21W solar charger", "kicker": "Phone charging off the sun", "img": "images/picks/allpowers-pb100-sp001.webp",
     "specs": ["24,000 mAh", "100 W USB-C", "21 W solar"],
     "runs": "Charge the power bank on the verandah by day, charge phones all night. Good for school bags and hurricane kits.",
     "price": "US$50", "store": "ALLPOWERS US store",
     "url": AWIN + "40342&ued=https%3A%2F%2Fiallpowers.com%2Fproducts%2Fallpowers-pb100-portable-power-bank-100w-24000mah%3Fvariant%3D44884576600217&clickref=setja-lifestyle"},
    {"name": "ALLPOWERS SP001 21W solar charger", "kicker": "Solar phone charger", "img": "images/picks/allpowers-sp001-21w.webp",
     "specs": ["21 W", "5 V USB", "Folds flat"],
     "runs": "Charges phones and power banks straight from the sun. Fits in a backpack.",
     "price": "US$39", "store": "ALLPOWERS US store",
     "url": AWIN + "40342&ued=https%3A%2F%2Fiallpowers.com%2Fproducts%2Fallpowers-sp001-5v-21w-portable-foldable-solar-panel%3Fvariant%3D45058752217241&clickref=setja-lifestyle"},
    {"name": "EcoFlow RAPID Power Bank 25,000mAh", "kicker": "Work through outages", "img": "images/picks/ecoflow-rapid-25000.webp",
     "specs": ["25,000 mAh", "170 W", "3 devices"],
     "runs": "Charges a laptop about twice or a phone 4–5 times. Recharges to 50% in about 20 minutes.",
     "price": "US$85.99", "store": "EcoFlow US store",
     "url": AWIN + "59181&ued=https%3A%2F%2Fus.ecoflow.com%2Fproducts%2Fecoflow-rapid-power-bank-25000mah-170w%3Fvariant%3D54593882128457&clickref=setja-lifestyle"},
    {"name": "BLUETTI X20 laptop power bank", "kicker": "Laptop & Wi-Fi backup", "img": "images/picks/bluetti-x20.webp",
     "specs": ["153.6 Wh", "288 W", "USB-C"],
     "runs": "Keeps a laptop and router going through a long outage. Fits in a backpack.",
     "price": "US$119", "store": "BLUETTI US store",
     "url": AWIN + "59271&ued=https%3A%2F%2Fwww.bluettipower.com%2Fproducts%2Fx20-portable-power-bank%3Fvariant%3D46173734699227&clickref=setja-lifestyle"},
    {"name": "EcoFlow 28W Ultra-Light Solar Panel", "kicker": "Pocket solar charger", "img": "images/picks/ecoflow-28w-solar-panel.webp",
     "specs": ["28 W", "USB direct charging", "IP68, 1.3 lb"], "checked": "Oct 17, 2026",
     "runs": "Charges phones and power banks straight from the sun, no grid needed. Tablet-sized and waterproof, for the yard, the beach or a blackout.",
     "price": "US$99", "store": "EcoFlow US store",
     "url": AWIN + "59181&ued=https%3A%2F%2Fus.ecoflow.com%2Fproducts%2Fecoflow-28w-ultra-light-solar-panel&clickref=setja-lifestyle"},
    {"name": "Dr.Prepare 700-Lumen Rechargeable LED Work Light", "kicker": "Outage light", "img": "images/picks/renogy-led-work-light.webp",
     "specs": ["700 lumens", "USB rechargeable", "Magnetic base"], "checked": "Oct 18, 2026",
     "runs": "Charges from any USB port or power bank. Folds, hangs or sticks to metal, and lasts up to 20 hours on low when JPS goes.",
     "price": "US$16.99", "store": "Renogy US store",
     "url": RENOGY + "dr-prepare-700-lumens-3200mah-foldable-rechargeable-led-work-light&subId1=setja-lifestyle"},
    {"name": "Renogy 276Wh Power Bank", "kicker": "Big power bank", "img": "images/picks/renogy-276wh-power-bank.webp",
     "specs": ["276 Wh", "USB-C fast charge", "12V car port"], "checked": "Oct 18, 2026",
     "runs": "Charges phones and laptops for days, and its 12V port can run most CPAP machines with a CPAP adapter (sold separately).",
     "price": "US$159.99", "store": "Renogy US store",
     "url": RENOGY + "2025-renogy-upgraded-76-800mah-276wh-power-bank&subId1=setja-lifestyle"},
    {"name": "Ventallion 42-Inch Solar Ceiling Fan with Light", "kicker": "Solar ceiling fan", "img": "images/picks/ventallion-42in-solar-ceiling-fan.webp",
     "specs": ["Solar + USB-C charging", "LiFePO4 battery", "3-colour LED light"], "checked": "Oct 20, 2026",
     "runs": "Runs off its own solar panel, no wiring to JPS. About 10 hours on high or up to 60 on low after a full charge. For the verandah, gazebo or shop front.",
     "price": "US$319", "store": "Ventallion US store",
     "url": VENTALLION + "42-inch-solar-ceiling-fan-with-light-and-battery&subId1=setja-lifestyle"},
    {"name": "Ventallion 52-Inch Solar Ceiling Fan with Light", "kicker": "Big solar ceiling fan", "img": "images/picks/ventallion-52in-solar-ceiling-fan.webp",
     "specs": ["Solar + USB-C charging", "12,000mAh LiFePO4", "3-colour LED light"], "checked": "Oct 20, 2026",
     "runs": "A larger panel and battery than the 42-inch. About 13 hours on high or up to 50 on low, so it keeps going through a long outage.",
     "price": "US$349", "store": "Ventallion US store",
     "url": VENTALLION + "52-inch-solar-ceiling-fan-with-light-and-battery&subId1=setja-lifestyle"},
]
# E-bikes & trikes (2026-10-17): Mooncool confirmed in writing (ticket 175302) that POP / TK2 / TK2 PRO chargers are
# rated 110-240V~ 50/60Hz. FT1 charger label (100-240V~ 50/60Hz) sent by Mooncool 2026-10-18 -> listed.
# US-only warranty, parts ship to US only, USD.
EBIKES_CHECKED = "Oct 18, 2026"
MOONCOOL = AWIN + "66494&ued=https%3A%2F%2Fwww.mooncool.com%2Fproducts%2F"
EBIKES = [
    {"name": "Mooncool POP Folding E-Bike", "kicker": "Folding e-bike", "img": "images/picks/mooncool-pop-folding-ebike.webp",
     "specs": ["1200W peak", "20 mph", "30–60 mi range"],
     "runs": "Folds down for the barrel or the car trunk. Good for town runs, school and work.",
     "price": "US$1,199.99", "store": "Mooncool US store", "url": MOONCOOL + "pop-folding-electric-bike&clickref=setja-ebikes"},
    {"name": "Mooncool FT1 Fat Tire Electric Trike", "kicker": "Fat-tire trike", "img": "images/picks/mooncool-ft1-fat-tire-trike.webp",
     "specs": ["500W motor", "35–60 mi range", "400 lb load"],
     "runs": "Wide 20 x 4 inch tires and a 7-speed Shimano for gravel, grass and rough country roads. Baskets front and back.",
     "price": "US$1,349.99", "store": "Mooncool US store", "url": MOONCOOL + "ft1-electric-trike&clickref=setja-ebikes"},
    {"name": "Mooncool TK2 Folding Electric Trike", "kicker": "Electric trike", "img": "images/picks/mooncool-tk2-trike.webp",
     "specs": ["1092W peak", "15.5 mph", "35–75 mi range"],
     "runs": "Three wheels, a backrest seat and two baskets. Steady for older riders and market runs.",
     "price": "US$1,499.99", "store": "Mooncool US store", "url": MOONCOOL + "tk2-electric-trike&clickref=setja-ebikes"},
    {"name": "Mooncool TK2 PRO Electric Trike", "kicker": "Electric trike", "img": "images/picks/mooncool-tk2-pro-trike.webp",
     "specs": ["48V 20Ah", "1310W peak", "450 lb load"],
     "runs": "More power and battery than the TK2, for hills and heavier loads. Up to 100 miles in Mooncool's testing.",
     "price": "US$1,999.99", "store": "Mooncool US store", "url": MOONCOOL + "tk2-pro-electric-trike&clickref=setja-ebikes"},
]
DISCLOSURE = ("We earn a commission when you buy through our store links, at no extra cost to you. "
              "As an Amazon Associate we earn from qualifying purchases. S.E.T. is not affiliated with Dennis Shipping.")
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


def picks_grid(up, items=None, checked=PICKS_CHECKED, badge='<span class="badge-50">50Hz-verified</span>'):
    cards = []
    for p in items or PICKS:
        specs = "".join(f'<span class="spec">{esc(x)}</span>' for x in p["specs"])
        cards.append(f"""<article class="card pcard"><div class="pic"><img src="{up}{esc(p['img'])}" alt="{esc(p['name'])}" loading="lazy"></div>
  <div class="body"><span class="line">{esc(p['kicker'])}</span><div>{badge}</div>
    <h3>{esc(p['name'])}</h3><div class="specs">{specs}</div><p class="runs">{esc(p['runs'])}</p>
    <p class="fine" style="margin:0">{esc(p['price'])} at {esc(p['store'])} ({p.get('checked', checked)}). Prices change.</p>
    <div class="foot"><a class="btn btn-primary" href="{esc(p['url'])}" target="_blank" rel="sponsored noopener">See today's price ↗</a></div></div></article>""")
    return '<div class="grid-4">' + "".join(cards) + '</div>' + f'<p class="fine" style="margin-top:10px">{esc(DISCLOSURE)}</p>'


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
    body = body.replace("{{picks}}", picks_grid(up))
    body = body.replace("{{ebikes}}", picks_grid(up, EBIKES, EBIKES_CHECKED))
    body = body.replace("{{lifestyle}}", picks_grid(up, LIFESTYLE, LIFESTYLE_CHECKED, '<span class="badge-50">No 50Hz issue</span>'))
    if "{{parish_map}}" in body:
        body = body.replace("{{parish_map}}", (ROOT / "_build" / "parish_map.svg").read_text(encoding="utf-8"))
    if "{{solar_calc_js}}" in body:
        calc_js = (ROOT / "_build" / "solar_calc.js").read_text(encoding="utf-8").replace("{{wa_number}}", WA_NUMBER)
        body = body.replace("{{solar_calc_js}}", "<script>\n" + calc_js + "</script>")
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
<div class="util"><div class="wrap"><span>US store prices</span><span>Door-to-door from Florida</span><span>Every pick checked for Jamaica's 50Hz grid</span></div></div>
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
      <p>We help Jamaica buy backup power that works on our 110V / 50Hz grid, at US store prices, and ship it home door-to-door.</p>
      <p>{ADDRESS}</p>
    </div>
    <div>
      <p class="footer-head">Shop</p>
      <a href="{up}shop-and-ship.html">Shop &amp; Ship</a><a href="{up}shop/">50Hz picks</a><a href="{up}diaspora.html">Send power home</a>
    </div>
    <div>
      <p class="footer-head">Help</p>
      <a href="{up}how-to-order.html">How to order</a><a href="{up}warranty.html">Warranty</a><a href="{up}guides/50hz-power-stations-jamaica.html">Will it work on 50Hz?</a><a href="{up}guides/sizing.html">What size do I need?</a><a href="{up}blog/">Blog</a>
    </div>
    <div>
      <p class="footer-head">Contact</p>
      <a href="{wa('Hi S.E.T. Jamaica, I have a question.')}">WhatsApp 857-445-9407</a><a href="mailto:{EMAIL}">{EMAIL}</a>{''.join(f'<a href="{u}" rel="noopener me">{n}</a>' for n, u in SOCIALS)}<a href="{up}about.html">About</a><a href="{up}contact.html">Contact</a><a href="{up}privacy-policy.html">Privacy</a><a href="{up}terms.html">Terms</a>
    </div>
  </div>
  <p class="wrap copyright">&copy; {YEAR} S.E.T. Sustainable Energy Technology in Jamaica. {esc(DISCLOSURE)}</p>
</footer>
<div class="mbar"><a class="btn btn-wa" href="{wa('Hi S.E.T. Jamaica, ')}">WhatsApp</a><a class="btn btn-primary" href="{up}shop-and-ship.html">Shop &amp; Ship</a></div>
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
                            "addressRegion": "Kingston", "addressCountry": "JM"},
                "sameAs": [u for _, u in SOCIALS],
                "description": "Solar generators, solar panels and backup power made for Jamaica's 50Hz grid, at US store prices, delivered door-to-door.",
                "areaServed": {"@type": "Country", "name": "Jamaica"}}) + "</script>"
            faq = re.findall(r"<details[^>]*><summary>(.*?)</summary><p>(.*?)</p></details>", raw, re.S)
            if faq:
                meta["head"] += '\n<script type="application/ld+json">' + json.dumps({
                    "@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                        {"@type": "Question", "name": html.unescape(q),
                         "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub(r"<[^>]+>", "", a))}} for q, a in faq]}) + "</script>"
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
