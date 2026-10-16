(function () {
  // Parish sun hours: NASA POWER ALLSKY_SFC_SW_DWN climatology (kWh/m2/day), annual mean + lowest month. Fetched 2026-10-16.
  var P = [['kingston','Kingston',5.6,4.3],['standrew','St Andrew',5.2,4.0],['stcatherine','St Catherine',5.6,4.3],['clarendon','Clarendon',5.7,4.5],
    ['manchester','Manchester',5.2,4.0],['stelizabeth','St Elizabeth',5.2,4.0],['westmoreland','Westmoreland',5.6,4.4],['hanover','Hanover',5.6,4.4],
    ['stjames','St James',5.2,4.0],['trelawny','Trelawny',5.2,4.0],['stann','St Ann',5.2,4.0],['stmary','St Mary',5.2,4.0],['portland','Portland',5.2,4.0],['stthomas','St Thomas',5.6,4.3]];
  var APPS = [{n:'Fridge',w:110,h:24,on:true},{n:'Standing fan',w:45,q:2,h:8,on:true},{n:'TV 43"',w:80,h:5,on:true},{n:'Wi-Fi router',w:12,h:24,on:true},
    {n:'LED lights ×4',w:36,h:6,on:true},{n:'Phone charging',w:15,h:3},{n:'Laptop',w:55,h:6},{n:'CPAP',w:40,h:8},{n:'Chest freezer',w:90,h:24},
    {n:'Ceiling fan',w:60,h:8},{n:'Water pump',w:750,h:1},{n:'Washing machine',w:500,h:1},{n:'Inverter AC 12k BTU',w:900,h:8}];
  var ST = [{n:'EcoFlow DELTA 2',wh:1024,max:1800},{n:'BLUETTI AC180',wh:1152,max:1800},{n:'EcoFlow DELTA 2 Max',wh:2048,max:2400}];
  var GOALS = [{id:'backup',n:'Backup when JPS goes',d:'Keep things running through outages'},{id:'bill',n:'Cut my JPS bill',d:'Make your own power every day'},
    {id:'offgrid',n:'Off-grid',d:'Cabin, farm, shop or yard with no JPS'}];
  var RATE = 45.8, EFF = .75, USE = .85;
  var state = {parish:'kingston', goal:'backup', outage:8};
  function $(id) { return document.getElementById(id); }
  function btn(cls, html, pressed, fn) { var b = document.createElement('button'); b.type = 'button'; b.className = cls; b.innerHTML = html; b.setAttribute('aria-pressed', pressed); b.addEventListener('click', fn); return b; }
  function kwh(wh) { return (wh / 1000).toFixed(wh < 10000 ? 1 : 0) + ' kWh'; }
  function num(n) { return Math.round(n).toLocaleString('en-US'); }
  function each(list, fn) { Array.prototype.forEach.call(list, fn); }

  APPS.forEach(function (a) {
    var b = btn('app', '<span>' + a.n + '<small>' + (a.q ? a.q + ' × ' : '') + a.w + ' W · ' + a.h + ' h/day</small></span><span>' + (a.on ? '✓' : '+') + '</span>', !!a.on,
      function () { a.on = !a.on; b.setAttribute('aria-pressed', a.on); b.lastChild.textContent = a.on ? '✓' : '+'; calc(); });
    $('apps').appendChild(b);
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
  [4, 8, 12, 24].forEach(function (h) {
    var b = btn('oh', h + ' hrs', h === state.outage, function () {
      state.outage = h; each($('outageRow').querySelectorAll('.oh'), function (c) { c.setAttribute('aria-pressed', c === b); }); calc(); });
    $('outageRow').appendChild(b);
  });

  function calc() {
    var load = 0, daily = 0;
    APPS.forEach(function (a) { if (a.on) { var w = a.w * (a.q || 1); load += w; daily += w * a.h; } });
    var p = P.filter(function (x) { return x[0] === state.parish; })[0], g = state.goal;
    $('outageRow').hidden = g !== 'backup';
    if (!load) { $('result').innerHTML = '<p class="muted" style="margin:0">Pick at least one appliance to see your solar size.</p>'; return; }
    var store, panel;
    if (g === 'backup') { store = daily * state.outage / 24 / USE; panel = store * USE / (p[2] * EFF); }   // recharge the outage energy in one average day
    else if (g === 'bill') { store = daily * 13 / 24 / USE; panel = daily / (p[2] * EFF); }               // cover a full day; battery carries ~13 dark hours
    else { store = daily / USE; panel = daily / (p[3] * EFF); }                                             // off-grid: size for the lowest month
    panel = Math.max(100, Math.ceil(panel / 100) * 100);
    var fit = ST.filter(function (s) { return s.wh >= store && s.max >= load; })[0];
    var html = '<p class="r-parish">' + p[1] + ' · <b>' + p[2].toFixed(1) + '</b> peak sun hrs/day <span>(lowest month ' + p[3].toFixed(1) + ')</span></p>' +
      '<div class="r-grid"><div><span class="k">Daily use</span><span class="v">' + kwh(daily) + '</span></div><div><span class="k">Running load</span><span class="v">' + num(load) + ' W</span></div>' +
      '<div><span class="k">Solar panels</span><span class="v">' + num(panel) + ' W</span><span class="s">≈ ' + Math.ceil(panel / 400) + ' × 400 W rooftop or ' + Math.ceil(panel / 200) + ' × 200 W portable</span></div>' +
      '<div><span class="k">Battery</span><span class="v">' + kwh(store) + '</span><span class="s">' + (g === 'backup' ? 'for a ' + state.outage + '-hour outage' : g === 'bill' ? 'to carry the evening and night' : 'one full day of storage') + '</span></div></div>';
    if (g === 'bill') html += '<p class="r-save">Could save about <b>J$' + num(Math.min(daily, panel * p[2] * EFF) / 1000 * 30 * RATE) + '</b> a month on your JPS bill.</p>';
    if (fit && g !== 'bill') {
      html += '<div class="station best"><span class="nm">' + fit.n + ' · best fit</span><span class="hrs">' + kwh(fit.wh) + '</span><span class="note">Handles ' + num(load) + ' W of its ' + num(fit.max) + ' W max. Pair it with ' + Math.ceil(panel / 200) + ' × 200 W solar panel' + (panel > 200 ? 's' : '') + '.</span></div>' +
        '<a class="btn btn-primary" href="{{up}}shop/">See the ' + fit.n + ' and our 50Hz picks</a>';
    } else {
      html += '<div class="station"><span class="nm">' + (g === 'bill' ? 'Rooftop solar system' : 'Bigger than a portable power station') + '</span><span class="note">' +
        (g === 'bill' ? 'Cutting your bill takes a rooftop grid-tie or hybrid system, installed by a licensed local installer.' : 'At ' + num(load) + ' W and ' + kwh(store) + ' of storage you need a home battery or rooftop hybrid system.') +
        ' We can point you to a trusted installer in ' + p[1] + '.</span></div>' +
        '<a class="btn btn-wa" href="https://wa.me/{{wa_number}}?text=' + encodeURIComponent('Hi S.E.T. Jamaica, I used the solar calculator. Parish: ' + p[1] + '. Daily use: ' + kwh(daily) + ', load ' + num(load) + ' W, solar ' + num(panel) + ' W, battery ' + kwh(store) + '. Can you help?') + '">Ask about an installer on WhatsApp</a>';
    }
    $('result').innerHTML = html + '<p class="fine" style="margin:0">Estimates only. <a href="{{up}}guides/sizing.html">Detailed sizing guide</a>.</p>';
  }
  pick(state.parish);
})();
