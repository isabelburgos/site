/* Vacuum Sequence — interactive step-through for vacuum procedures.
 *
 * Each .vs-container holds:
 *   .vs-mermaid-panel      — Mermaid flowchart (rendered by mermaid.js)
 *   .vs-diagram-panel      — vacuum diagram SVG (always visible, updated in-place)
 *   .vs-step-bar           — current step controls (populated here)
 *   template.vs-svg-template — base vacuum diagram SVG
 *   pre.vs-sequence-data   — JSON sequence definition
 */

// ── SVG class helpers ─────────────────────────────────────────────────────────
// Cumulative diagram state: accumState = { state: Set<id> }
// Per-step spec tokens:
//   "V31, V36"  — absolute: resets that state category, sets to these IDs
//   "+V9"       — delta: adds V9 to accumulated set
//   "-V9"       — delta: removes V9 from accumulated set

function applyDiagramSpec(svgEl, wrapperEl, spec, accumState) {
  // Phase 1: update persistent accumState with +/- tokens only
  const MUTEX = { closed: 'open', open: 'closed' };
  if (spec) {
    for (const [state, val] of Object.entries(spec)) {
      const tokens = String(val).split(',').map(s => s.trim()).filter(Boolean);
      for (const t of tokens) {
        if (t[0] === '+') {
          if (!accumState[state]) accumState[state] = new Set();
          const id = t.slice(1);
          accumState[state].add(id);
          const opp = MUTEX[state];
          if (opp && accumState[opp]) accumState[opp].delete(id);
        } else if (t[0] === '-') {
          if (accumState[state]) accumState[state].delete(t.slice(1));
        }
      }
    }
  }

  // Phase 2: build displayState = copy of accumState + ephemeral absolutes
  const displayState = {};
  for (const [s, ids] of Object.entries(accumState)) displayState[s] = new Set(ids);
  if (spec) {
    for (const [state, val] of Object.entries(spec)) {
      const tokens = String(val).split(',').map(s => s.trim()).filter(Boolean);
      const absolutes = tokens.filter(t => t[0] !== '+' && t[0] !== '-');
      if (absolutes.length) displayState[state] = new Set(absolutes);
    }
  }

  // Phase 3: render SVG from displayState
  svgEl.querySelectorAll('[class]').forEach(el => {
    [...el.classList].filter(c => c.startsWith('vd-')).forEach(c => el.classList.remove(c));
  });
  wrapperEl.classList.remove('has-highlight');

  const tagAll = (baseId, cls) => {
    svgEl.querySelectorAll(`[id="${baseId}"], [id^="${baseId}_"]`)
         .forEach(el => el.classList.add(cls));
  };

  for (const [state, ids] of Object.entries(displayState)) {
    if (!ids.size) continue;
    const cls = state === 'highlight' ? 'vd-highlighted' : `vd-${state}`;
    ids.forEach(id => tagAll(id, cls));
  }
  if (displayState.highlight?.size) wrapperEl.classList.add('has-highlight');
}

// ── Mermaid reserved word sanitizer (must match hooks.py + main.js) ──────────

const MERMAID_RESERVED = new Set(['end', 'subgraph', 'style', 'classDef', 'class',
  'click', 'graph', 'flowchart', 'direction', 'linkStyle', 'default']);

function mid(id) { return MERMAID_RESERVED.has(id) ? `_${id}` : id; }

// ── Mermaid helpers ───────────────────────────────────────────────────────────

function highlightMermaidNode(svg, stepId) {
  svg.querySelectorAll('.vs-current').forEach(el => el.classList.remove('vs-current'));
  const g = svg.querySelector(`[id^="flowchart-${mid(stepId)}-"]`);
  if (g) {
    g.classList.add('vs-current');
    g.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function addConditionOverlays(svg, steps) {
  for (const [id, step] of Object.entries(steps)) {
    if (step.type !== 'condition') continue;
    const g = svg.querySelector(`[id^="flowchart-${mid(id)}-"]`);
    if (!g) continue;
    g.classList.add('vs-condition');
    const rect = g.querySelector('rect');
    if (!rect) continue;
    const x = parseFloat(rect.getAttribute('x') || '0');
    const y = parseFloat(rect.getAttribute('y') || '0');
    const w = parseFloat(rect.getAttribute('width') || '0');
    const h = parseFloat(rect.getAttribute('height') || '0');
    if (!w || !h) continue;
    const poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    poly.classList.add('vs-condition-diamond');
    poly.setAttribute('points', `${x},${y+h/2} ${x+w/2},${y} ${x+w},${y+h/2} ${x+w/2},${y+h}`);
    poly.setAttribute('fill', 'none');
    poly.setAttribute('pointer-events', 'none');
    g.appendChild(poly);
  }
}

function patchMermaidClicks(svg, onStepClick) {
  svg.querySelectorAll('[id^="flowchart-"]').forEach(g => {
    const m = g.id.match(/^flowchart-(.+)-\d+$/);
    if (!m) return;
    const mermaidId = m[1];
    const stepId = mermaidId.startsWith('_') && MERMAID_RESERVED.has(mermaidId.slice(1))
      ? mermaidId.slice(1) : mermaidId;
    g.style.cursor = 'pointer';
    g.addEventListener('click', () => onStepClick(stepId));
  });
}

// ── Step bar rendering ────────────────────────────────────────────────────────

function renderStepBar(stepBar, step, stepId, isLoop) {
  const type = step.type || 'action';

  let buttonsHtml;
  if (type === 'condition') {
    const nLabel = isLoop ? 'N \u2014 not yet' : 'N';
    const nExtra = isLoop ? ' vs-loop' : '';
    const nGoto = isLoop ? '' : (step.else || '');
    buttonsHtml = `
      <button class="vs-btn vs-btn-yes" data-goto="${step.then || ''}">Y</button>
      <button class="vs-btn vs-btn-no${nExtra}" data-goto="${nGoto}">${nLabel}</button>`;
  } else if (step.next) {
    const nextLabel = step.timer ? `Wait ${step.timer} \u2192` : `Next \u2192`;
    buttonsHtml = `<button class="vs-btn vs-btn-next" data-goto="${step.next}">${nextLabel}</button>`;
  } else {
    buttonsHtml = `<span class="vs-complete">\u2713 Sequence complete</span>
      <button class="vs-btn vs-btn-restart" data-action="restart">\u21BA Restart</button>`;
  }

  stepBar.innerHTML = `
    <div class="vs-step-info">
      <span class="vs-type-badge vs-badge-${type}">${type}</span>
      <span class="vs-step-label">${step.label || stepId}</span>
    </div>
    <div class="vs-buttons">${buttonsHtml}</div>`;
}

// ── Container initialization ──────────────────────────────────────────────────

function initContainer(container) {
  if (container.dataset.vsInit) return;
  container.dataset.vsInit = '1';

  const dataPre = container.querySelector('.vs-sequence-data');
  if (!dataPre) return;
  let sequence;
  try { sequence = JSON.parse(dataPre.textContent); }
  catch (e) { console.error('[vacuum-sequence] JSON parse error', e); return; }

  const steps = sequence.steps;
  let currentId = sequence.start;
  let accumState = {};
  let mermaidSvg = null;

  const tmpl = container.querySelector('template.vs-svg-template');
  const diagramPanel = container.querySelector('.vs-diagram-panel');
  const mermaidPanel = container.querySelector('.vs-mermaid-panel');
  const stepBar = container.querySelector('.vs-step-bar');

  let diagramSvg = null;
  let diagramWrapper = null;

  if (tmpl && diagramPanel) {
    const svgEl = tmpl.content.querySelector('svg');
    if (svgEl) {
      diagramWrapper = document.createElement('div');
      diagramWrapper.className = 'vacuum-diagram-embed';
      diagramSvg = svgEl.cloneNode(true);
      diagramWrapper.appendChild(diagramSvg);
      diagramPanel.appendChild(diagramWrapper);
    }
  }

  function goTo(stepId) {
    if (!stepId || !steps[stepId]) return;
    currentId = stepId;

    const step = steps[stepId];
    const isLoop = step.loop || step.else === stepId;

    if (stepBar) renderStepBar(stepBar, step, stepId, isLoop);
    if (diagramSvg && diagramWrapper) applyDiagramSpec(diagramSvg, diagramWrapper, step.diagram || null, accumState);
    if (mermaidSvg) highlightMermaidNode(mermaidSvg, stepId);
  }

  goTo(currentId);

  if (stepBar) {
    stepBar.addEventListener('click', e => {
      const btn = e.target.closest('.vs-btn');
      if (!btn) return;
      const action = btn.dataset.action;
      if (action === 'restart') {
        accumState = {};
        goTo(sequence.start);
        return;
      }
      if (btn.classList.contains('vs-loop')) {
        btn.classList.add('vs-waiting');
        setTimeout(() => btn.classList.remove('vs-waiting'), 600);
        return;
      }
      const target = btn.dataset.goto;
      if (target) goTo(target);
    });
  }

  // Wait for mermaid to finish rendering before wiring up clicks and overlays
  if (mermaidPanel) {
    const tryPatch = () => {
      const svg = mermaidPanel.querySelector('svg');
      if (!svg || !svg.querySelector('[id^="flowchart-"]')) return false;
      mermaidSvg = svg;
      patchMermaidClicks(svg, goTo);
      addConditionOverlays(svg, steps);
      highlightMermaidNode(svg, currentId);
      return true;
    };
    if (!tryPatch()) {
      const obs = new MutationObserver(() => { if (tryPatch()) obs.disconnect(); });
      obs.observe(mermaidPanel, { childList: true, subtree: true });
    }
  }
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────

function initAll() {
  document.querySelectorAll('.vs-container').forEach(initContainer);
}

document.addEventListener('DOMContentLoaded', initAll);

if (typeof document$ !== 'undefined') {
  document$.subscribe(initAll);
} else {
  new MutationObserver(initAll).observe(document.body, { childList: true, subtree: true });
}
