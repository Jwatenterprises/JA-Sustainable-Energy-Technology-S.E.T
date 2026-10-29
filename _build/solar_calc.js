(function () {
  // Parish sun hours: NASA POWER ALLSKY_SFC_SW_DWN climatology (kWh/m2/day), annual mean + lowest month. Fetched 2026-10-16.
  var P = [['kingston','Kingston',5.6,4.3],['standrew','St Andrew',5.2,4.0],['stcatherine','St Catherine',5.6,4.3],['clarendon','Clarendon',5.7,4.5],
    ['manchester','Manchester',5.2,4.0],['stelizabeth','St Elizabeth',5.2,4.0],['westmoreland','Westmoreland',5.6,4.4],['hanover','Hanover',5.6,4.4],
    ['stjames','St James',5.2,4.0],['trelawny','Trelawny',5.2,4.0],['stann','St Ann',5.2,4.0],['stmary','St Mary',5.2,4.0],['portland','Portland',5.2,4.0],['stthomas','St Thomas',5.6,4.3]];
  var APPS = [{n:'Fridge',w:110,h:24,q:1,on:true},{n:'Standing fan',w:45,h:8,q:2,on:true},{n:'TV 43"',w:80,h:5,q:1,on:true},{n:'Wi-Fi router',w:12,h:24,q:1,on:true},
    {n:'LED bulb',w:9,h:6,q:4,on:true},{n:'Phone charging',w:15,h:3,q:1},{n:'Laptop',w:55,h:6,q:1},{n:'CPAP',w:40,h:8,q:1},{n:'Chest freezer',w:90,h:24,q:1},
    {n:'Ceiling fan',w:60,h:8,q:1},{n:'Microwave',w:1100,h:.3,q:1},{n:'Water pump',w:750,h:1,q:1},{n:'Washing machine',w:500,h:1,q:1},{n:'Inverter AC 12k BTU',w:900,h:8,q:1}];
  // Brand US-store prices checked Oct 29, 2026 (2 Extra Batteries: Oct 21; Vatrer: Oct 28). solar = max solar input in W.
  var UNITS = [{n:'BLUETTI AC180',wh:1152,w:1800,usd:499,solar:500},{n:'BLUETTI Elite 200 V2',wh:2073,w:2600,usd:899,solar:1200},
    {n:'EcoFlow DELTA 2 Max',wh:2048,w:2400,usd:1049,solar:1000}];
  var EXPAND = [{n:'EcoFlow DELTA 2 Max + 1 Extra Battery',wh:4096,w:2400,usd:1899,solar:1000,note:'EcoFlow bundle'},
    {n:'EcoFlow DELTA 2 Max + 2 Extra Batteries',wh:6144,w:2400,usd:2847,solar:1000,note:'1 unit + 2 batteries, Oct 21 prices'}];
  var PANEL = {w:200, usd:349}, HOME_BATT = {n:'Vatrer 48V 100Ah wall battery', wh:5120, usd:899.99};
  var GOALS = [{id:'backup',n:'Backup when JPS goes',d:'Keep things running through outages'},{id:'bill',n:'Cut my JPS bill',d:'Make your own power every day'},
    {id:'offgrid',n:'Off-grid',d:'Cabin, farm, shop or yard with no JPS'}];
  // Installed home system (JMD), from published Jamaican installer prices in 2026: solar + inverter + install J$350K-500K per kW
  // (solarsizecalculator.com/jm), lithium storage about J$50K-110K per kWh installed (Saddle Energy, howjamaica.com, Solar Specialist JA).
  // Check: 5 kW + 10 kWh -> J$2.3M-3.6M vs published J$1.8M-3.4M.
  var PV_JMD = [350000, 500000], BATT_JMD = [50000, 110000];
  var RATE = 45.8, FX = 160, EFF = .75, USE = .85, HOME_USE = .9;
  var state = {parish:'kingston', goal:'backup', outage:8};
  function $(id) { return document.getElementById(id); }
  function btn(cls, html, pressed, fn) { var b = document.createElement('button'); b.type = 'button'; b.className = cls; b.innerHTML = html; if (pressed !== null) b.setAttribute('aria-pressed', pressed); b.addEventListener('click', fn); return b; }
  function kwh(wh) { return (wh / 1000).toFixed(wh < 10000 ? 1 : 0) + ' kWh'; }
  function num(n) { return Math.round(n).toLocaleString('en-US'); }
  function money(usd) { return 'US$' + num(usd) + ' <span>(≈ J$' + (usd * FX >= 1e6 ? (usd * FX / 1e6).toFixed(2) + 'M' : num(usd * FX / 1000) + 'K') + ')</span>'; }
  function jm(n) { return n >= 1e6 ? 'J$' + (Math.round(n / 1e5) / 10).toFixed(1) + 'M' : 'J$' + num(Math.round(n / 1e4) * 10) + 'K'; }
  function hrs(h) { return h >= 48 ? '48+ hrs' : h >= 10 ? Math.round(h) + ' hrs' : h.toFixed(1) + ' hrs'; }
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }
  function outageLabel(h) { return (h === 8 ? 'an ' : 'a ') + (h >= 24 ? h / 24 + '-day' : h + '-hour') + ' outage'; }

  // Step 1: appliances with a quantity stepper
  APPS.forEach(function (a) {
    var row = document.createElement('div'); row.className = 'app' + (a.on ? ' on' : '');
    var t = btn('app-t', '', a.on, function () { a.on = !a.on; paint(); calc(); });
    var minus = btn('qb', '−', null, function () { a.q = Math.max(1, a.q - 1); paint(); calc(); });
    var plus = btn('qb', '+', null, function () { a.q = Math.min(20, a.q + 1); paint(); calc(); });
    minus.setAttribute('aria-label', 'Fewer ' + a.n); plus.setAttribute('aria-label', 'More ' + a.n);
    var qn = document.createElement('span'); qn.className = 'qn';
    var qty = document.createElement('span'); qty.className = 'qty'; qty.append(minus, qn, plus);
    function paint() {
      row.classList.toggle('on', a.on); t.setAttribute('aria-pressed', a.on);
      t.innerHTML = '<span class="tick">' + (a.on ? '✓' : '+') + '</span><span>' + a.n + '<small>' + a.w + ' W · ' + a.h + ' h/day</small></span>';
      qn.textContent = a.q; qty.hidden = !a.on;
    }
    paint(); row.append(t, qty); $('apps').appendChild(row);
  });
  var paths = document.querySelectorAll('.parish-map path'), tiles = {};
  P.forEach(function (p) {
    var b = btn('ptile', p[1] + '<small>' + p[2].toFixed(1) + ' sun hrs</small>', p[0] === state.parish, function () { pick(p[0]); });
    tiles[p[0]] = b; $('parishes').appendChild(b);
  });
  each(paths, function (el) {
    var p = P.filter(function (x) { return x[0] === el.dataset.parish; })[0]; if (!p) return;
    el.setAttribute('data-sun', p[2] >= 5.6 ? 'hi' : 'mid');
    el.addEventListener('click', function () { pick(p[0]); });
  });
  function pick(id) {
    state.parish = id;
    Object.keys(tiles).forEach(function (k) { tiles[k].setAttribute('aria-pressed', k === id); });
    each(paths, function (el) { el.classList.toggle('on', el.dataset.parish === id); });
    calc();
  }
  GOALS.forEach(function (g) {
    var b = btn('goal', '<b>' + g.n + '</b><small>' + g.d + '</small>', g.id === state.goal, function () {
      state.goal = g.id; each($('goals').children, function (c) { c.setAttribute('aria-pressed', c === b); }); calc(); });
    $('goals').appendChild(b);
  });
  [[4,'4 hrs'],[8,'8 hrs'],[12,'12 hrs'],[24,'1 day'],[48,'2 days']].forEach(function (o) {
    var b = btn('oh', o[1], o[0] === state.outage, function () {
      state.outage = o[0]; each($('outageRow').querySelectorAll('.oh'), function (c) { c.setAttribute('aria-pressed', c === b); }); calc(); });
    $('outageRow').appendChild(b);
  });

  // Share the load across n units, biggest appliance first (each unit runs its own appliances; 50Hz units can't be paralleled).
  function split(items, n, cap) {
    var bins = []; for (var i = 0; i < n; i++) bins.push({w: 0, names: []});
    items.slice().sort(function (a, b) { return b.w - a.w; }).forEach(function (it) {
      if (!bins) return;
      var b = bins.filter(function (x) { return x.w + it.w <= cap; }).sort(function (x, y) { return x.w - y.w; })[0];
      if (!b) { bins = null; return; }
      b.w += it.w; b.names.push(it.n);
    });
    return bins;
  }
  function group(names) {
    var c = {}; names.forEach(function (x) { c[x] = (c[x] || 0) + 1; });
    return Object.keys(c).map(function (k) { return (c[k] > 1 ? c[k] + ' × ' : '') + k; }).join(', ');
  }

  function calc() {
    var load = 0, daily = 0, items = [], big = 0;
    APPS.forEach(function (a) { if (a.on) { load += a.w * a.q; daily += a.w * a.q * a.h; big = Math.max(big, a.w);
      for (var i = 0; i < a.q; i++) items.push({n: a.n, w: a.w}); } });
    var p = P.filter(function (x) { return x[0] === state.parish; })[0], g = state.goal;
    $('outageRow').hidden = g !== 'backup';
    if (!load) { $('result').innerHTML = '<p class="muted" style="margin:0">Pick at least one appliance to see your options.</p>'; $('options').innerHTML = ''; return; }
    var avg = daily / 24, need, panel;
    if (g === 'backup') { need = avg * state.outage; panel = need / (p[2] * EFF); }   // energy for the outage, refilled in one average day
    else if (g === 'bill') { need = avg * 13; panel = daily / (p[2] * EFF); }        // cover a full day; battery carries ~13 dark hours
    else { need = daily; panel = daily / (p[3] * EFF); }                              // off-grid: one full day, sized for the lowest month
    var store = need / USE, target = need / avg;                                       // target = hours the battery must carry
    panel = Math.max(100, Math.ceil(panel / 100) * 100);

    function portable(o, units) {
      var usable = o.wh * USE * units, cap = o.w * units, panels = Math.min(Math.ceil(panel / PANEL.w), Math.floor(o.solar * units / PANEL.w));
      return {usable: usable, cap: cap, hours: usable / avg, panels: Math.max(1, panels), capped: Math.ceil(panel / PANEL.w) > panels,
        cost: o.usd * units + Math.max(1, panels) * PANEL.usd};
    }
    var opts = [];
    // A: one power station, the smallest that runs everything at once
    var one = UNITS.filter(function (u) { return u.w >= load; }).sort(function (a, b) { return a.usd - b.usd; });
    var oneFit = one.filter(function (u) { return u.wh * USE >= need; })[0] || one.sort(function (a, b) { return b.wh - a.wh; })[0];
    if (oneFit) { var r = portable(oneFit, 1); opts.push({id:'one', tag:'Plug-and-play', name: oneFit.n, r: r, power: load <= oneFit.w,
      what: 'One portable power station. Plug your appliances straight in, no electrician.',
      pros: ['Ready the day it arrives', 'Moves with you, room to room'], cons: [r.hours < target ? 'Runs out before your target' : 'Fixed size: can\'t add more later'],
      cta: ['See it in our 50Hz picks', '{{up}}shop/#power-stations']}); }
    // B: same unit, more batteries (more hours, same power)
    if (load <= 2400) {
      var ex = EXPAND.filter(function (e) { return e.wh * USE >= need; })[0] || EXPAND[EXPAND.length - 1], rb = portable(ex, 1);
      opts.push({id:'expand', tag:'More hours', name: ex.n, r: rb, power: true, date: ex.wh > 4096 ? 'Oct 21–29, 2026' : null,
        what: 'One DELTA 2 Max with clip-on Extra Batteries. More hours, same 2,400 W at once.',
        pros: ['Most storage for the money', 'Start with one, add a battery later'], cons: ['Still 2,400 W at once', 'Check Extra Battery stock first'],
        cta: ['Extra batteries or more units?', '{{up}}guides/stack-power-stations.html']});
    }
    // C: several units, each on its own appliances (more power and more hours)
    if (load > 1500 || need > 2073 * USE) {
      var best = null;
      UNITS.forEach(function (u) {
        if (big > u.w) return;
        for (var n = 2; n <= 4; n++) {
          var bins = split(items, n, u.w * .9);
          if (bins && u.wh * USE * n >= need) { var rc = portable(u, n); if (!best || rc.cost < best.r.cost) best = {u: u, n: n, r: rc, bins: bins}; break; }
        }
      });
      if (best) opts.push({id:'multi', tag:'More power', name: best.n + ' × ' + best.u.n, r: best.r, power: true,
        what: 'Several power stations, each running its own appliances.',
        plan: best.bins.filter(function (b) { return b.names.length; }).map(function (b, i) { return 'Unit ' + (i + 1) + ': ' + group(b.names); }),
        pros: ['Up to ' + num(best.u.w * best.n) + ' W across the house', 'If one unit is busy, the others keep going'],
        cons: ['Don\'t link them into one outlet'], cta: ['How to stack power stations', '{{up}}guides/stack-power-stations.html']});
    }
    // D: home battery + hybrid inverter, installed by a licensed electrician
    var hb = Math.max(1, Math.ceil(store * USE / (HOME_BATT.wh * HOME_USE))), kwp = Math.max(3, Math.ceil(panel / 1000)), roof = Math.ceil(kwp * 1000 / 400), bkwh = hb * HOME_BATT.wh / 1000;
    var lo = kwp * PV_JMD[0] + bkwh * BATT_JMD[0], hi = kwp * PV_JMD[1] + bkwh * BATT_JMD[1];
    var inv = load <= 4800 ? '6 kW 48V inverter (EG4 6000XP or Growatt SPF 6000T)' : load <= 9600 ? '12 kW 48V hybrid inverter (EG4 12000XP)' : 'two 48V inverters, designed by your installer';
    opts.push({id:'home', tag:'Whole home', name: 'Home hybrid battery system', home: true, power: true,
      r: {usable: hb * HOME_BATT.wh * HOME_USE, cap: load <= 4800 ? 6000 : 12000, hours: hb * HOME_BATT.wh * HOME_USE / avg, cost: Infinity}, lo: lo, hi: hi,
      what: 'A ' + kwp + ' kW rooftop solar system with ' + kwh(hb * HOME_BATT.wh) + ' of home battery storage, installed and wired into your panel board by a licensed electrician.',
      kit: [kwp + ' kW of rooftop panels (about ' + roof + ' × 400 W)', 'A ' + inv, hb + ' × 5 kWh lithium wall battery (for example ' + HOME_BATT.n + ')', 'Mounting, wiring, breakers and surge protection', 'Licensed installation, set to 50Hz'],
      needs: ['About ' + Math.ceil(roof * 2.1) + ' m² of sunny, unshaded roof', 'Wall or floor space for the batteries (about 50 kg each)', g === 'bill' ? 'JPS approval to connect to the grid (your installer handles it)' : 'If it connects to the grid, JPS approval (your installer handles it)'],
      pros: ['Switches over by itself when JPS goes', g === 'bill' ? 'The only option that really cuts your bill' : 'Runs AC, pumps and the whole house', 'Lasts 10+ years; add batteries later'],
      cons: ['Bigger upfront cost', 'Price depends on your roof and wiring: get 2–3 quotes'],
      cta: ['Ask about an installer on WhatsApp', 'https://wa.me/{{wa_number}}?text=' + encodeURIComponent('Hi S.E.T. Jamaica, I used the solar calculator. Parish: ' + p[1] + '. Daily use ' + kwh(daily) + ', load ' + num(load) + ' W, battery ' + kwh(store) + ', solar ' + num(panel) + ' W. I\'d like to get quotes for a ' + kwp + ' kW home solar and battery system.')]});

    // Best match: the lowest-cost portable option that covers both the power and the hours; otherwise the home system
    var fits = opts.filter(function (o) { return !o.home && o.power && load <= o.r.cap && o.r.hours >= target * .98; }).sort(function (a, b) { return a.r.cost - b.r.cost; });
    var bestId = g === 'bill' || !fits.length ? 'home' : fits[0].id;
    var bestOpt = opts.filter(function (o) { return o.id === bestId; })[0];

    var html = '<p class="r-parish">' + p[1] + ' · <b>' + p[2].toFixed(1) + '</b> peak sun hrs/day <span>(lowest month ' + p[3].toFixed(1) + ')</span></p>' +
      '<div class="r-grid"><div><span class="k">Daily use</span><span class="v">' + kwh(daily) + '</span></div><div><span class="k">All on at once</span><span class="v">' + num(load) + ' W</span></div>' +
      '<div><span class="k">Solar panels</span><span class="v">' + num(panel) + ' W</span><span class="s">≈ ' + Math.ceil(panel / 200) + ' × 200 W portable or ' + Math.ceil(panel / 400) + ' × 400 W rooftop</span></div>' +
      '<div><span class="k">Battery</span><span class="v">' + kwh(store) + '</span><span class="s">' + (g === 'backup' ? 'for ' + outageLabel(state.outage) : g === 'bill' ? 'to carry the evening and night' : 'one full day of storage') + '</span></div></div>';
    if (g === 'bill') html += '<p class="r-save">Could save about <b>J$' + num(Math.min(daily, panel * p[2] * EFF) / 1000 * 30 * RATE) + '</b> a month on your JPS bill.</p>';
    html += '<div class="station best"><span class="nm">Best match · ' + bestOpt.tag + '</span><span class="hrs">' + (bestOpt.home ? jm(bestOpt.lo) + '+' : hrs(bestOpt.r.hours)) + '</span>' +
      '<span class="note"><b>' + bestOpt.name + '.</b> ' + (opts.length > 1 ? 'Compare all ' + opts.length + ' ways to power your home below.' : '') + '</span></div>' +
      '<a class="btn btn-primary" href="#options">Compare your options ↓</a>' +
      '<a class="btn btn-wa" href="https://wa.me/{{wa_number}}?text=' + encodeURIComponent('Hi S.E.T. Jamaica, here are my solar calculator results. Parish: ' + p[1] + '. Daily use ' + kwh(daily) + ', load ' + num(load) + ' W, battery ' + kwh(store) + ', solar ' + num(panel) + ' W. Best match: ' + bestOpt.name + '. Can you help me choose?') + '">Send my results on WhatsApp</a>' +
      '<p class="fine" style="margin:0">Estimates only. <a href="{{up}}guides/sizing.html">Detailed sizing guide</a>.</p>';
    $('result').innerHTML = html;

    $('options').innerHTML = '<div class="opts-head"><p class="eyebrow">Your options</p><h2>' + ['', 'One way', 'Two ways', 'Three ways', 'Four ways'][opts.length] + ' to power the same appliances.</h2>' +
      '<p class="muted">Sized for ' + kwh(daily) + ' a day, ' + num(load) + ' W at once' + (g === 'backup' ? ', through ' + outageLabel(state.outage) : '') + ', in ' + p[1] + '.</p></div>' +
      '<div class="opts">' + opts.map(function (o) {
        var hPct = Math.min(100, o.r.hours / target * 100), wPct = Math.min(100, load / o.r.cap * 100), okH = o.r.hours >= target * .98, okW = o.power && load <= o.r.cap;
        return '<article class="opt' + (o.id === bestId ? ' best' : '') + '">' +
          '<p class="opt-tag">' + o.tag + (o.id === bestId ? '<span class="badge-best">Best match</span>' : '') + '</p><h3>' + o.name + '</h3><p class="opt-what">' + o.what + '</p>' +
          '<div class="meter"><div class="m-top"><span>Backup time</span><b class="' + (okH ? 'ok' : 'short') + '">' + hrs(o.r.hours) + (okH ? ' ✓' : '') + '</b></div><div class="bar"><i class="' + (okH ? 'ok' : 'short') + '" style="width:' + hPct.toFixed(0) + '%"></i></div>' +
          '<p class="m-sub">' + (g === 'backup' ? 'Goal: ' + target + ' hrs' : g === 'bill' ? 'Goal: carry the evening and night' : 'Goal: one full day') + ' · ' + kwh(o.r.usable) + ' usable</p></div>' +
          '<div class="meter"><div class="m-top"><span>Power at once</span><b class="' + (okW ? 'ok' : 'short') + '">' + num(o.r.cap) + ' W' + (okW ? ' ✓' : '') + '</b></div><div class="bar"><i class="' + (okW ? 'ok' : 'short') + '" style="width:' + wPct.toFixed(0) + '%"></i></div>' +
          '<p class="m-sub">Your appliances: ' + num(load) + ' W</p></div>' +
          (o.plan ? '<ul class="plan">' + o.plan.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>' : '') +
          (o.home ? '<details class="kit" open><summary>What is included</summary><ul>' + o.kit.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul></details>' +
            '<details class="kit"><summary>What you will need</summary><ul>' + o.needs.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul></details>' : '<p class="opt-solar">☀ ' + o.r.panels + ' × 200 W solar panel' + (o.r.panels > 1 ? 's' : '') + (o.r.capped ? ' (its solar input tops out here, so a full refill takes more than a day)' : '') + '</p>') +
          '<ul class="pc">' + o.pros.map(function (x) { return '<li class="pro">' + x + '</li>'; }).join('') + o.cons.map(function (x) { return '<li class="con">' + x + '</li>'; }).join('') + '</ul>' +
          (o.home ? '<p class="opt-price">' + jm(o.lo) + '–' + jm(o.hi).slice(2) + ' <span>installed, all in (≈ US$' + num(o.lo / FX / 1000) + 'K–' + num(o.hi / FX / 1000) + 'K)</span></p>' +
            '<p class="fine">Typical range from published Jamaican installer prices, 2026. Your quote depends on your roof, wiring and brands.</p>'
          : '<p class="opt-price">About ' + money(o.r.cost) + '</p>' +
            '<p class="fine">Brand US stores incl. panels, ' + (o.date || 'Oct 29, 2026') + '. Before shipping and customs. Prices change.</p>') +
          '<a class="btn ' + (o.home ? 'btn-wa' : 'btn-ghost') + '" href="' + o.cta[1] + '">' + o.cta[0] + '</a></article>';
      }).join('') + '</div>';
  }
  pick(state.parish);
})();
