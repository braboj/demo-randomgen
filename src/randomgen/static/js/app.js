/* RandomGen demo UI logic — calls the REST API and renders the result. */
(function () {
  'use strict';

  var cfg = window.RANDOMGEN_CONFIG || {};
  var form = document.getElementById('controls');
  var statusEl = document.getElementById('status');
  var resultsEl = document.getElementById('results');
  var verdictEl = document.getElementById('verdict');
  var chartEl = document.getElementById('chart');
  var generateBtn = document.getElementById('generate');
  var resetBtn = document.getElementById('reset');

  function setStatus(message, kind) {
    if (!message) { statusEl.hidden = true; statusEl.textContent = ''; return; }
    statusEl.hidden = false;
    statusEl.textContent = message;
    statusEl.className = 'status' + (kind ? ' ' + kind : '');
  }

  function selectedVersion() {
    var checked = form.querySelector('input[name="apiVersion"]:checked');
    return checked ? checked.value : 'v1';
  }

  function buildUrl() {
    var version = selectedVersion();
    var quantity = document.getElementById('quantity').value;
    var dist = document.getElementById('dist').value.trim();
    var params = new URLSearchParams();
    params.set('numbers', quantity);
    if (dist) { params.set('dist', dist); }
    return '/api/' + version + '/randomgen?' + params.toString();
  }

  // Sort the union of category labels numerically (keys arrive as strings).
  function categories(expected, observed) {
    var keys = {};
    Object.keys(expected || {}).forEach(function (k) { keys[k] = true; });
    Object.keys(observed || {}).forEach(function (k) { keys[k] = true; });
    return Object.keys(keys).sort(function (a, b) { return parseFloat(a) - parseFloat(b); });
  }

  function fmtPct(p) { return (p * 100).toFixed(1) + '%'; }

  function renderVerdict(test) {
    var pass = !!test.is_null;
    verdictEl.innerHTML = '';

    var badge = document.createElement('span');
    badge.className = 'badge ' + (pass ? 'pass' : 'fail');
    badge.textContent = pass ? '✓ Fits the distribution' : '✗ Deviates from expected';
    verdictEl.appendChild(badge);

    var stats = [
      ['χ²', Number(test.chi_square).toFixed(3)],
      ['p-value', Number(test.p_value).toFixed(3)],
      ['df', String(test.df)]
    ];
    var dl = document.createElement('dl');
    stats.forEach(function (pair) {
      var dt = document.createElement('dt'); dt.textContent = pair[0];
      var dd = document.createElement('dd'); dd.textContent = pair[1];
      dl.appendChild(dt); dl.appendChild(dd);
    });
    verdictEl.appendChild(dl);
  }

  function renderChart(expected, observed) {
    chartEl.innerHTML = '';
    var cats = categories(expected, observed);

    // Scale every bar against the largest proportion so the tallest fills the track.
    var max = 0;
    cats.forEach(function (c) {
      max = Math.max(max, expected[c] || 0, observed[c] || 0);
    });
    if (max <= 0) { max = 1; }

    cats.forEach(function (c) {
      var exp = expected[c] || 0;
      var obs = observed[c] || 0;

      var row = document.createElement('div');
      row.className = 'bar-row';

      var label = document.createElement('div');
      label.className = 'value';
      label.textContent = c;
      row.appendChild(label);

      var bars = document.createElement('div');
      bars.className = 'bars';
      bars.appendChild(makeBar('expected', exp, max));
      bars.appendChild(makeBar('observed', obs, max));
      row.appendChild(bars);

      chartEl.appendChild(row);
    });
  }

  function makeBar(kind, proportion, max) {
    var track = document.createElement('div');
    track.className = 'bar-track';
    var fill = document.createElement('div');
    fill.className = 'bar-fill ' + kind;
    var pct = document.createElement('span');
    pct.className = 'pct';
    pct.textContent = fmtPct(proportion);
    fill.appendChild(pct);
    track.appendChild(fill);
    // Defer the width so the CSS transition animates from 0.
    requestAnimationFrame(function () {
      fill.style.width = Math.max(2, (proportion / max) * 100) + '%';
    });
    return track;
  }

  function onSubmit(event) {
    event.preventDefault();
    generateBtn.disabled = true;
    setStatus('Generating…', 'busy');

    fetch(buildUrl(), { headers: { Accept: 'application/json' } })
      .then(function (res) {
        return res.json().then(function (body) {
          if (!res.ok) {
            throw new Error(body && body.error ? body.error : 'Request failed (' + res.status + ')');
          }
          return body;
        });
      })
      .then(function (data) {
        var q = data.quality || {};
        renderVerdict(q.chi_square_test || {});
        renderChart(q.expected_histogram || {}, q.observed_histogram || {});
        resultsEl.hidden = false;
        setStatus(null);
      })
      .catch(function (err) {
        resultsEl.hidden = true;
        setStatus(err.message || 'Something went wrong.', 'err');
      })
      .finally(function () {
        generateBtn.disabled = false;
      });
  }

  function onReset() {
    var v1 = document.getElementById('v1');
    if (v1) { v1.checked = true; }
    document.getElementById('quantity').value = cfg.defaultQuantity || 1000;
    document.getElementById('dist').value = cfg.defaultDist || '';
    resultsEl.hidden = true;
    setStatus(null);
  }

  form.addEventListener('submit', onSubmit);
  resetBtn.addEventListener('click', onReset);
})();
