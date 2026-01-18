// Minimal front-end logic to manage N, dynamic (x,y) rows, validation, and API calls

const nInput = document.getElementById('nInput');
const setNBtn = document.getElementById('setNBtn');
const xyContainer = document.getElementById('xyContainer');
const xyRows = document.getElementById('xyRows');
const actions = document.getElementById('actions');
const resultsEl = document.getElementById('results');
const solveAllBtn = document.getElementById('solveAll');

// Generate N rows for x,y inputs  `
setNBtn.addEventListener('click', () => {
  const n = parseInt(nInput.value, 10);
  if (!Number.isInteger(n) || n <= 0) {
    alert('Please enter a valid integer N > 0.');
    return;
  }
  xyRows.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const row = document.createElement('div');
    row.className = 'xy-row fade-in';
    row.innerHTML = `
      <div>${i + 1}</div>
      <div><input type="number" step="any" placeholder="x${i + 1}" /></div>
      <div><input type="number" step="any" placeholder="y${i + 1}" /></div>
    `;
    xyRows.appendChild(row);
  }
  xyContainer.classList.remove('hidden');
  actions.classList.remove('hidden');
  resultsEl.classList.add('hidden');
  resultsEl.innerHTML = '';

  // Wire Enter-to-next navigation for x/y inputs
  wireXYKeyNav();
});

// Pressing Enter in N triggers Set N
nInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    setNBtn.click();
  }
});

// Helper to read x,y arrays and validate length
function readXY() {
  const rows = Array.from(xyRows.querySelectorAll('.xy-row'));
  const x = [];
  const y = [];
  for (const row of rows) {
    const inputs = row.querySelectorAll('input');
    const xv = parseFloat(inputs[0].value);
    const yv = parseFloat(inputs[1].value);
    if (!Number.isFinite(xv) || !Number.isFinite(yv)) {
      return { error: 'Please fill all x and y values with valid numbers.' };
    }
    x.push(xv);
    y.push(yv);
  }
  return { x, y };
}

// Attach single-fit buttons
actions.addEventListener('click', async (e) => {
  const btn = e.target.closest('button[data-fit]');
  if (!btn) return;
  await submitFits([btn.dataset.fit]);
});

// Solve All
solveAllBtn.addEventListener('click', async () => {
  await submitFits(['all']);
});

// Call backend and render results
async function submitFits(types) {
  const data = readXY();
  if (data.error) {
    alert(data.error);
    return;
  }
  try {
    const res = await fetch('/fit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: data.x, y: data.y, types })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Request failed');
    }
    const payload = await res.json();
    renderResults(data.x, data.y, payload.results, payload.bestType);
  } catch (err) {
    alert(err.message || 'Something went wrong.');
  }
}

function renderResults(x, y, results, bestType) {
  resultsEl.innerHTML = '';
  resultsEl.classList.remove('hidden');

  // Show the data table first
  const dataCard = document.createElement('div');
  dataCard.className = 'result fade-in';
  dataCard.innerHTML = `
    <h3>Input Data</h3>
    <div class="meta">N = ${x.length}
    </div>
    <div style="overflow:auto;margin-top:8px">
      <table style="border-collapse:collapse;width:100%">
        <thead>
          <tr>
            <th style="text-align:left;padding:6px;border-bottom:1px solid #97C5E2">#</th>
            <th style="text-align:left;padding:6px;border-bottom:1px solid #97C5E2">x</th>
            <th style="text-align:left;padding:6px;border-bottom:1px solid #97C5E2">y</th>
          </tr>
        </thead>
        <tbody>
          ${x.map((xi, i) => `
            <tr>
              <td style="padding:6px;border-bottom:1px solid #97C5E2">${i + 1}</td>
              <td style="padding:6px;border-bottom:1px solid #97C5E2">${xi}</td>
              <td style="padding:6px;border-bottom:1px solid #97C5E2">${y[i]}</td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  `;
  resultsEl.appendChild(dataCard);

  // (Per-type summaries will be shown inline; no global summary)

  // Each result card
  for (const r of results) {
    const card = document.createElement('div');
    card.className = 'result fade-in' + (r.type === bestType ? ' best' : '');
    const title = r.type ? r.type.charAt(0).toUpperCase() + r.type.slice(1) : 'Result';
    const coeffs = r.coefficients ? Object.entries(r.coefficients).map(([k, v]) => `${k} = ${formatNum(v)}`).join(', ') : '';
    // Extra steps section removed per request
    const eq = r.equation || '';
    const r2 = typeof r.r2 === 'number' ? r.r2 : null;
    const error = r.error || null;
    const warn = r.warnings || null;

    const question = r.question ? `<div class="solution-section"><strong>Question:</strong> ${escapeHtml(r.question)}</div>` : '';
    const cols = Array.isArray(r.columns) ? r.columns : null;
    const table = Array.isArray(r.table) ? r.table : null;
    const sums = r.sums || null;
    const equations = Array.isArray(r.equations) ? r.equations : null;
    const working = Array.isArray(r.working) ? r.working : null;

    // Build table HTML if provided
    let tableHtml = '';
    if (cols && table) {
      tableHtml = `
        <div class="solution-table-wrap">
          <table class="solution-table">
            <thead><tr>${cols.map(c => `<th>${escapeHtml(c)}</th>`).join('')}</tr></thead>
            <tbody>
              ${table.map(row => `<tr>${cols.map(c => `<td>${escapeHtml(rowKey(row, c))}</td>`).join('')}</tr>`).join('')}
            </tbody>
          </table>
        </div>`;
    }

    // Build sums
    let sumsHtml = '';
    if (sums) {
      const pairs = Object.entries(sums).map(([k, v]) => `${escapeHtml(k)} = ${escapeHtml(formatNum(v))}`);
      sumsHtml = `<div class="solution-pre"><pre>${pairs.join('\n')}</pre></div>`;
    }

    // Build equations/working
    const eqsHtml = equations ? `<div class="solution-pre"><pre>${equations.map(e => escapeHtml(e)).join('\n')}</pre></div>` : '';
    const workHtml = working ? `<div class="solution-pre"><pre>${working.map(e => escapeHtml(e)).join('\n')}</pre></div>` : '';

    card.innerHTML = `
      <h3>${title} Fit ${r.type === bestType ? '— Best Fit' : ''}</h3>
      ${question}
      ${tableHtml}
      ${sumsHtml}
      ${eqsHtml}
      ${workHtml}
      <div class="meta"><strong>Formula used:</strong> ${escapeHtml(r.formula || '')}</div>
      ${error ? `<div class="meta" style="color:#dc2626;margin-top:6px">Error: ${escapeHtml(error)}</div>` : ''}
      ${warn ? `<div class="meta" style="color:#a16207;margin-top:6px">${escapeHtml(String(warn))}</div>` : ''}
      ${coeffs ? `<div style="margin-top:8px"><strong>Values:</strong> ${coeffs}</div>` : ''}
      ${eq ? `<div class="final-equation"><strong>${escapeHtml(eq)}</strong></div>` : ''}
      ${typeof r2 === 'number' ? `<div style="margin-top:8px"><strong>R²:</strong> ${formatNum(r2)}</div>` : ''}
    `;
    resultsEl.appendChild(card);

    // After each solution, show a concise best-fit summary for THIS type
    const mini = document.createElement('div');
    mini.className = 'result fade-in mini' + (r.type === bestType ? ' best' : '');
    mini.innerHTML = `
      <h3 class="mini-title">The Best Fitted Curve</h3>
      <div class="meta">Type: ${escapeHtml(r.type || '')}</div>
      ${r.equation ? `<div class="final-equation"><strong>${escapeHtml(r.equation)}</strong></div>` : ''}
      ${typeof r.r2 === 'number' ? `<div style=\"margin-top:8px\"><strong>R²:</strong> ${formatNum(r.r2)}</div>` : ''}
    `;
    resultsEl.appendChild(mini);
  }

  // When solving all (multiple results), show overall best at the end
  if (Array.isArray(results) && results.length > 1 && bestType) {
    const best = results.find(rr => rr.type === bestType);
    if (best) {
      const overall = document.createElement('div');
      overall.className = 'result fade-in overall';
      overall.innerHTML = `
        <h3>The Best Fitted Curve (Overall)</h3>
        <div class="meta">Type: ${escapeHtml(best.type || '')}</div>
        ${best.equation ? `<div class="final-equation"><strong>${escapeHtml(best.equation)}</strong></div>` : ''}
        ${typeof best.r2 === 'number' ? `<div style="margin-top:8px"><strong>R²:</strong> ${formatNum(best.r2)}</div>` : ''}
      `;
      resultsEl.appendChild(overall);
    }
  }

}

function escapeHtml(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}

function formatNum(v) {
  if (!Number.isFinite(v)) return String(v);
  // Keep it readable
  return Math.abs(v) >= 1e6 || (Math.abs(v) > 0 && Math.abs(v) < 1e-4)
    ? v.toExponential(6)
    : Number(v.toFixed(6));
}

function rowKey(row, colName) {
  // Map pretty headers like x², (ln x)², etc., back to keys we stored
  const mapping = {
    'x': 'x', 'y': 'y', 'xy': 'xy', 'x²': 'x2', 'x2': 'x2',
    'ln(y)': 'lny', 'x·ln(y)': 'xlny', 'x²': 'x2',
    'ln(x)': 'lnx', 'ln(x)·y': 'u*y', '(ln x)²': 'u2', 'ln(x)·ln(y)': 'lnx·lny'
  };
  const key = mapping[colName] || colName;
  const val = row[key];
  return typeof val === 'number' ? formatNum(val) : (val ?? '');
}

// Helpers for keyboard navigation across x/y inputs
function wireXYKeyNav() {
  const rows = Array.from(xyRows.querySelectorAll('.xy-row'));
  const xInputs = [];
  const yInputs = [];
  for (const row of rows) {
    const [x, y] = row.querySelectorAll('input');
    if (x) xInputs.push(x);
    if (y) yInputs.push(y);
  }
  const ordered = [...xInputs, ...yInputs];

  ordered.forEach((inp, idx) => {
    inp.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const next = ordered[idx + 1];
        if (next) {
          next.focus();
          next.select?.();
        } else {
          // If on last cell, keep focus or move to actions
          document.getElementById('solveAll')?.focus();
        }
      }
    });
  });
}



