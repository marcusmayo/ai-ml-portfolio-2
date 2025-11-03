/* === Progress (SSE + fallback) === */
export function startProgressStream(update) {
  let stopped = false;
  const es = new EventSource('/api/progress');
  const close = () => { stopped = true; try { es.close(); } catch {} };

  es.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data || '{}');
      if (data.ping) return;
      update(data);
      if (data.percent >= 100) close();
    } catch {}
  };
  es.onerror = () => {
    // fallback to polling
    es.close();
    const tick = async () => {
      if (stopped) return;
      try {
        const r = await fetch('/api/progress-now');
        const j = await r.json();
        update(j);
        if (j.percent < 100) setTimeout(tick, 1500);
      } catch {
        setTimeout(tick, 3000);
      }
    };
    tick();
  };
  return close;
}

/* === Timeline + Word-level rendering === */
function colorFor(score) {
  if (score >= 75) return '#22c55e';   // green
  if (score >= 50) return '#eab308';   // yellow
  return '#ef4444';                    // red
}

export function renderResultsEnhancements(result) {
  // Create containers dynamically under #results
  const root = document.querySelector('#results') || document.body;
  let wrap = document.getElementById('timeline-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = 'timeline-wrap';
    wrap.innerHTML = `
      <h3 style="margin:16px 0 8px;font:600 16px/1.2 system-ui">Timeline</h3>
      <div id="timeline" style="width:100%;height:48px;display:flex;gap:2px;align-items:flex-end;"></div>
      <div id="bin-info" style="margin:8px 0 16px;padding:8px;border:1px solid #e5e7eb;border-radius:8px;display:none"></div>
      <h3 style="margin:0 0 8px;font:600 16px/1.2 system-ui">Word-level Analysis</h3>
      <div id="word-level" style="padding:12px;border:1px solid #e5e7eb;border-radius:8px;line-height:1.9"></div>
    `;
    root.appendChild(wrap);
  }

  const timeline = document.getElementById('timeline');
  const info = document.getElementById('bin-info');
  const wlev = document.getElementById('word-level');

  // Render words with data-start/end
  wlev.innerHTML = '';
  const frag = document.createDocumentFragment();
  (result.word_timestamps || []).forEach(w => {
    const span = document.createElement('span');
    span.textContent = w.word + ' ';
    span.dataset.start = w.start;
    span.dataset.end = w.end;
    frag.appendChild(span);
  });
  wlev.appendChild(frag);

  // Render bins (as small flex items)
  timeline.innerHTML = '';
  const bins = (result.timeline && result.timeline.bins) || [];
  if (!bins.length) {
    // Show note if backend returned none
    const note = document.createElement('div');
    note.textContent = 'No timeline bins returned.';
    note.style.color = '#6b7280';
    note.style.font = '13px system-ui';
    timeline.appendChild(note);
    return;
  }

  const duration = result.timeline.duration || 0;
  const total = bins.length;
  const wPercent = (100 / total);

  const highlightWords = (t0, t1) => {
    [...wlev.querySelectorAll('span')].forEach(s => {
      const a = parseFloat(s.dataset.start), b = parseFloat(s.dataset.end);
      if (isNaN(a) || isNaN(b)) return;
      const on = !(b <= t0 || a >= t1);
      s.style.background = on ? 'rgba(99,102,241,.18)' : '';
    });
  };

  bins.forEach((b, idx) => {
    const div = document.createElement('div');
    div.title = `t=${b.t0.toFixed(1)}–${b.t1.toFixed(1)}s · score=${Number(b.score).toFixed(0)}`;
    div.style.flex = `0 0 ${wPercent}%`;
    div.style.height = (28 + (b.score/100)*20) + 'px';
    div.style.background = colorFor(b.score);
    div.style.borderRadius = '2px';
    div.style.cursor = 'pointer';
    div.setAttribute('role','button');
    div.addEventListener('mouseenter', () => highlightWords(b.t0, b.t1));
    div.addEventListener('mouseleave', () => highlightWords(-1,-1));
    div.addEventListener('click', () => {
      info.style.display = 'block';
      info.innerHTML = `
        <div style="font:600 13px system-ui;margin-bottom:6px">
          Bin ${idx+1}/${total} • ${b.t0.toFixed(1)}–${b.t1.toFixed(1)}s • Score ${Number(b.score).toFixed(0)}
        </div>
        <div style="font:13px/1.6 system-ui;white-space:pre-wrap">${(b.text||'').trim() || '—'}</div>
      `;
      highlightWords(b.t0, b.t1);
      // scroll the word panel into view on narrow screens
      info.scrollIntoView({block:'nearest', behavior:'smooth'});
    });
    timeline.appendChild(div);
  });
}

/* === Wire up to your existing page ===
   Call:
     startProgressStream(({percent,stage,message}) => { ...update your progress bar... });
   After you receive analyze-audio JSON, call:
     renderResultsEnhancements(json);
*/
