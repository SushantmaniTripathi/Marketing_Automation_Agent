/* ═══════════════════════════════════════════════
   DIGITAL MARKETING AUTOMATION — APP.JS
   ═══════════════════════════════════════════════ */

// ── STATE ────────────────────────────────────────
const state = {
  post: {
    topic: '',
    hashtags: [],
    caption: '',
    imagePath: '',
    imageUrl: '',
  },
  seo: {
    topic: '',
    research: null,
    autopostDraft: null,
  }
};

// ── INIT ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initLogin();
  initTabs();
  checkHealth();
  setInterval(checkHealth, 60000);
});

function initLogin() {
  const loginForm = document.getElementById('loginForm');
  const loginOverlay = document.getElementById('loginOverlay');
  const loginUsername = document.getElementById('login-username');
  const loginPassword = document.getElementById('login-password');

  if (sessionStorage.getItem('dma_web_authenticated') === 'true') {
    unlockApp();
    return;
  }

  loginForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = (loginUsername?.value || '').trim();
    const password = (loginPassword?.value || '').trim();
    const errorEl = document.getElementById('loginError');
    const submitBtn = loginForm.querySelector('.login-btn');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';
    }

    try {
        const res = await api('/api/login', { username, password });
        if (res.success) {
            sessionStorage.setItem('dma_web_authenticated', 'true');
            unlockApp();
            toast('Login successful', 'success');
        } else {
            if (errorEl) errorEl.textContent = res.error || 'Invalid credentials.';
        }
    } catch (e) {
        if (errorEl) errorEl.textContent = 'Error connecting to server.';
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    }
  });

  loginPassword?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      loginForm?.requestSubmit();
    }
  });
}

function unlockApp() {
  document.body.classList.remove('app-locked');
  const overlay = document.getElementById('loginOverlay');
  if (overlay) overlay.style.display = 'none';
}

function logout() {
  sessionStorage.removeItem('dma_web_authenticated');
  document.body.classList.add('app-locked');
  const overlay = document.getElementById('loginOverlay');
  if (overlay) overlay.style.display = 'flex';
  
  // Clear any inputs like username/password
  const loginUsername = document.getElementById('login-username');
  const loginPassword = document.getElementById('login-password');
  const errorEl = document.getElementById('loginError');
  if (loginUsername) loginUsername.value = '';
  if (loginPassword) loginPassword.value = '';
  if (errorEl) errorEl.textContent = '';
  
  toast('Logged out successfully', 'info');
}

// ── TABS ─────────────────────────────────────────
function initTabs() {
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${tab}`).classList.add('active');
    });
  });
}

// ── HEALTH CHECK ─────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    const s = data.services || {};
    setDot('hd-openai', s.openai);
    setDot('hd-instagram', s.instagram);
    setDot('hd-gsc', s.gsc);
  } catch (e) { /* silently fail */ }
}
function setDot(id, ok) {
  const el = document.getElementById(id);
  if (el) { el.className = 'health-dot ' + (ok ? 'ok' : 'err'); }
}

// ── TOAST ─────────────────────────────────────────
function toast(msg, type = 'info', duration = 4000) {
  const c = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.remove(), duration);
}

// ── LOADING ───────────────────────────────────────
function showLoading(text = 'Processing...') {
  document.getElementById('loadingText').textContent = text;
  document.getElementById('loadingOverlay').classList.remove('hidden');
}
function hideLoading() {
  document.getElementById('loadingOverlay').classList.add('hidden');
}

// ── API CALL ──────────────────────────────────────
async function api(path, body = null, method = 'POST') {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  return res.json();
}

// ═══════════════════════════════════════════════════
//  POST AUTOMATION
// ═══════════════════════════════════════════════════

function fillTopic(t) {
  const input = document.getElementById('post-topic');
  if (!input) return;
  input.value = t;
  state.post.topic = t;
  input.focus();
}

async function loadTodaysTrends() {
  const trendsEl = document.getElementById('trends-result');
  const btn = document.getElementById('btn-post-trends');
  if (!trendsEl) return;

  trendsEl.style.display = 'block';
  trendsEl.innerHTML = '<div class="result-block loading"><div class="spinner-ring"></div> Loading today\'s trend topics...</div>';
  if (btn) btn.disabled = true;

  try {
    const res = await fetch('/api/post/trends');
    const data = await res.json();

    if (!data.success) {
      trendsEl.innerHTML = `<div class="result-error">❌ ${escHtml(data.error || 'Failed to load trends')}</div>`;
      return;
    }

    const topics = (data.topics || []).slice(0, 20);
    if (!topics.length) {
      trendsEl.innerHTML = '<div class="result-info">No trends available right now. Try again in a few minutes.</div>';
      return;
    }

    trendsEl.innerHTML = `
      <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;">Today's Trends (click to use as topic)</div>
      <div id="trends-topic-list" style="display:flex;flex-direction:column;gap:8px;margin-bottom:10px;">
        ${topics.map((t, i) => `
          <button class="chip trend-topic-btn" data-topic="${escAttr(t.topic || t.title || '')}" title="${escAttr((t.source || 'source') + ' • ' + (t.niche || 'trend'))}" style="text-align:left;">
            ${(i + 1)}. ${escHtml((t.title || '').slice(0, 120))}
            <span style="display:block;margin-top:4px;font-size:10px;color:var(--text-muted);">${escHtml((t.niche || 'trend').toUpperCase())} • ${escHtml(t.source || 'source')}</span>
          </button>
        `).join('')}
      </div>
      <div style="font-size:11px;color:var(--text-muted);">${escHtml(data.note || '')}</div>
    `;

    trendsEl.querySelectorAll('.trend-topic-btn').forEach(btnEl => {
      btnEl.addEventListener('click', () => {
        const topic = btnEl.getAttribute('data-topic') || '';
        if (!topic) return;
        fillTopic(topic);
        toast('Topic selected. Click Generate Hashtags to continue.', 'info');
      });
    });

    toast('Today\'s trends loaded', 'success');
  } catch (e) {
    trendsEl.innerHTML = `<div class="result-error">❌ ${escHtml(e.message)}</div>`;
  } finally {
    if (btn) btn.disabled = false;
  }
}

function syncPostDraftFromEditors() {
  const hashtagsEditor = document.getElementById('post-hashtags-editor');
  const captionEditor = document.getElementById('post-caption-editor');

  if (hashtagsEditor) {
    state.post.hashtags = hashtagsEditor.value
      .split(/\s+/)
      .map(t => t.trim())
      .filter(Boolean);
  }

  if (captionEditor) {
    state.post.caption = captionEditor.value;
  }
}

function renderPostEditors() {
  const hashEl = document.getElementById('hashtags-result');
  const capEl = document.getElementById('caption-result');
  const hashtagsText = (state.post.hashtags || []).join(' ');

  hashEl.innerHTML = `
    <div class="result-block">
      <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">🏷️ Hashtags (editable)</div>
      <textarea id="post-hashtags-editor" class="input-field" rows="4" style="font-family:var(--font-mono);font-size:12px;line-height:1.7">${escHtml(hashtagsText)}</textarea>
    </div>`;

  capEl.innerHTML = `
    <div class="result-block">
      <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;">✍️ Caption (editable)</div>
      <textarea id="post-caption-editor" class="input-field" rows="8" style="line-height:1.7">${escHtml(state.post.caption || '')}</textarea>
    </div>`;

  document.getElementById('post-hashtags-editor')?.addEventListener('input', syncPostDraftFromEditors);
  document.getElementById('post-caption-editor')?.addEventListener('input', syncPostDraftFromEditors);
}

async function postStep1() {
  const topic = document.getElementById('post-topic').value.trim();
  if (!topic) { toast('Please enter a topic first', 'error'); return; }
  state.post.topic = topic;

  showLoading('Fetching hashtags from Instagram API...');
  advancePostStep(2);

  const hashEl = document.getElementById('hashtags-result');
  const capEl  = document.getElementById('caption-result');
  hashEl.innerHTML = '<div class="result-block loading"><div class="spinner-ring"></div> Fetching hashtags...</div>';
  capEl.innerHTML  = '<div class="result-block loading"><div class="spinner-ring"></div> Generating caption...</div>';

  hideLoading();

  try {
    // Parallel: hashtags + caption
    const [hRes, cRes] = await Promise.all([
      api('/api/post/hashtags', { topic }),
      api('/api/post/caption',  { topic }),
    ]);

    if (hRes.success) {
      state.post.hashtags = hRes.hashtags;
      toast('Hashtags generated!', 'success');
    } else {
      hashEl.innerHTML = `<div class="result-error">❌ ${hRes.error}</div>`;
    }

    if (cRes.success) {
      state.post.caption = cRes.caption;
      toast('Caption generated!', 'success');
    } else {
      capEl.innerHTML = `<div class="result-error">❌ ${cRes.error}</div>`;
    }

    if (hRes.success || cRes.success) {
      renderPostEditors();
      syncPostDraftFromEditors();
    }
  } catch (e) {
    toast('Request failed: ' + e.message, 'error');
  }
}

async function regenerateCaption() {
  if (!state.post.topic) { toast('No topic set', 'error'); return; }
  const capEl = document.getElementById('caption-result');
  capEl.innerHTML = '<div class="result-block loading"><div class="spinner-ring"></div> Regenerating...</div>';
  try {
    const res = await api('/api/post/caption', { topic: state.post.topic });
    if (res.success) {
      state.post.caption = res.caption;
      renderPostEditors();
      syncPostDraftFromEditors();
      toast('Caption regenerated!', 'success');
    } else {
      capEl.innerHTML = `<div class="result-error">❌ ${res.error}</div>`;
    }
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

async function postStep2() {
  syncPostDraftFromEditors();
  if (!state.post.caption) { toast('Wait for caption to generate first', 'error'); return; }
  advancePostStep(3);
  const preview = document.getElementById('image-preview');
  preview.innerHTML = '<div class="image-loader"><div class="spinner-ring"></div><span>Generating image with Ideogram AI...</span></div>';
  toast('Generating AI image — this may take ~30s', 'info');
  try {
    const res = await api('/api/post/image', { topic: state.post.topic });
    if (res.success) {
      state.post.imagePath = res.image_path;
      // Build a served URL from the filename only
      const fname = res.image_path.split(/[\\/]/).pop();
      const src = `/api/post/generated-image/${encodeURIComponent(fname)}`;
      preview.innerHTML = `<img src="${src}" alt="Generated" onerror="this.src='https://images.unsplash.com/photo-1534854638093-bada1813ca19?w=600&q=80'">`;
      toast('Image generated!', 'success');
    } else {
      preview.innerHTML = `<div class="result-error" style="margin:20px">❌ ${res.error}</div>`;
      toast('Image generation failed: ' + res.error, 'error');
    }
  } catch (e) {
    preview.innerHTML = `<div class="result-error" style="margin:20px">❌ ${e.message}</div>`;
    toast('Error: ' + e.message, 'error');
  }
}

async function regenerateImage() {
  if (!state.post.topic) { toast('No topic', 'error'); return; }
  const preview = document.getElementById('image-preview');
  preview.innerHTML = '<div class="image-loader"><div class="spinner-ring"></div><span>Regenerating...</span></div>';
  try {
    // Pass the old path so backend deletes it before generating a new one
    const res = await api('/api/post/image', {
      topic: state.post.topic,
      old_image_path: state.post.imagePath || null
    });
    if (res.success) {
      state.post.imagePath = res.image_path;
      const fname = res.image_path.split(/[\\/]/).pop();
      const src = `/api/post/generated-image/${encodeURIComponent(fname)}`;
      preview.innerHTML = `<img src="${src}" alt="Generated" onerror="this.src='https://images.unsplash.com/photo-1534854638093-bada1813ca19?w=600&q=80'">`;
      toast('Image regenerated!', 'success');
    } else {
      preview.innerHTML = `<div class="result-error" style="margin:20px">❌ ${res.error}</div>`;
    }
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

function postStep3() {
  syncPostDraftFromEditors();
  if (!state.post.imagePath) { toast('Image not ready yet', 'error'); return; }
  advancePostStep(4);

  const preview = document.getElementById('publish-preview');
  preview.innerHTML = `
    <div class="preview-topic">📌 ${escHtml(state.post.topic)}</div>
    <div class="preview-caption">${escHtml(state.post.caption.substring(0, 200))}${state.post.caption.length > 200 ? '...' : ''}</div>
    <div class="preview-hashtags">${state.post.hashtags.join(' ')}</div>
  `;
}

function toggleSchedule() {
  const checked = document.getElementById('schedule-toggle').checked;
  document.getElementById('schedule-time-input').classList.toggle('hidden', !checked);
}

async function publishPost() {
  syncPostDraftFromEditors();
  if (!state.post.caption || !state.post.imagePath) {
    toast('Complete all steps before publishing', 'error');
    return;
  }
  const resultEl = document.getElementById('publish-result');
  const scheduled = document.getElementById('schedule-toggle').checked;
  const scheduleTime = scheduled ? document.getElementById('schedule-dt').value : null;

  showLoading(scheduled ? 'Scheduling post...' : 'Publishing to Instagram...');

  try {
    const res = await api('/api/post/publish', {
      image_path:  state.post.imagePath,
      caption:     state.post.caption,
      hashtags:    state.post.hashtags,
      schedule_time: scheduleTime
    });
    hideLoading();

    if (res.success) {
      resultEl.innerHTML = `
        <div class="result-success" style="margin-top:16px">
          ✅ ${escHtml(res.message || 'Published successfully!')}
          ${res.post_id ? `<br><span class="mono">Post ID: ${res.post_id}</span>` : ''}
        </div>`;
      toast('Post published!', 'success');
      markStepDone(4);
    } else {
      resultEl.innerHTML = `<div class="result-error" style="margin-top:16px">❌ ${escHtml(res.error)}</div>`;
      toast('Publish failed: ' + res.error, 'error');
    }
  } catch (e) {
    hideLoading();
    toast('Error: ' + e.message, 'error');
  }
}

function resetPost() {
  state.post = { topic:'', hashtags:[], caption:'', imagePath:'', imageUrl:'' };
  advancePostStep(1);
  document.getElementById('post-topic').value = '';
  document.getElementById('hashtags-result').innerHTML = '';
  document.getElementById('caption-result').innerHTML = '';
  document.getElementById('publish-result').innerHTML = '';
  document.getElementById('publish-preview').innerHTML = '';
  document.getElementById('schedule-toggle').checked = false;
  document.getElementById('schedule-time-input').classList.add('hidden');
  document.getElementById('schedule-dt').value = '';
  document.getElementById('image-preview').innerHTML = `
    <div class="image-loader">
      <div class="spinner-ring"></div>
      <span>Generating with Ideogram AI...</span>
    </div>
  `;
  document.querySelectorAll('#tab-post .step-dot').forEach((d,i) => {
    d.classList.remove('active','done');
    if (i === 0) d.classList.add('active');
  });
}

function postGoBack(step) {
  const target = Number(step);
  if (![1, 2, 3, 4].includes(target)) return;
  advancePostStep(target);
}

function stopPostFlow() {
  resetPost();
  toast('Post automation stopped. You can start again anytime.', 'info');
}

function advancePostStep(n) {
  document.querySelectorAll('.step-panel').forEach((p,i) => {
    p.classList.toggle('active', i + 1 === n);
  });
  document.querySelectorAll('#tab-post .step-dot').forEach((d,i) => {
    d.classList.remove('active','done');
    if (i + 1 < n)  d.classList.add('done');
    if (i + 1 === n) d.classList.add('active');
  });
}

function markStepDone(n) {
  document.querySelectorAll('#tab-post .step-dot').forEach((d,i) => {
    if (i + 1 <= n) { d.classList.remove('active'); d.classList.add('done'); }
  });
}

// ═══════════════════════════════════════════════════
//  SEO AUTOMATION
// ═══════════════════════════════════════════════════

function setSEOTopic() {
  const topic = document.getElementById('seo-topic').value.trim();
  if (!topic) { toast('Enter an SEO topic first', 'error'); return; }
  state.seo.topic = topic;
  toast(`Topic set: "${topic}"`, 'success');
  document.getElementById('seo-topic-card').style.borderColor = 'var(--accent-2)';
}

async function runSEOStep(step) {
  if (!state.seo.topic) {
    const t = document.getElementById('seo-topic').value.trim();
    if (!t) { toast('Set your SEO topic first!', 'error'); return; }
    state.seo.topic = t;
  }

  const statusEl = document.getElementById(`seo-status-${step}`);
  const resultEl = document.getElementById(`seo-result-${step}`);
  const btnEl    = document.getElementById(`btn-seo-${step}`);

  statusEl.textContent = '⟳ Running';
  statusEl.className   = 'seo-status running';
  btnEl.disabled = true;
  resultEl.innerHTML = '<div style="display:flex;align-items:center;gap:8px"><div class="spinner-ring"></div> Working...</div>';

  const endpoints = {
    research:    '/api/seo/research',
    technical:   '/api/seo/technical',
    backlinks:   '/api/seo/backlinks',
    performance: '/api/seo/performance',
  };

  try {
    const payload = { topic: state.seo.topic };
    if (step === 'performance') {
      payload.period = document.getElementById('seo-performance-period')?.value || 'month';
    }
    const res = await api(endpoints[step], payload);

    statusEl.textContent = res.success ? '✓ Done' : '✕ Error';
    statusEl.className   = 'seo-status ' + (res.success ? 'done' : 'error');
    btnEl.disabled = false;

    if (res.success) {
      resultEl.innerHTML = renderSEOResult(step, res);
      toast(`${step} analysis complete!`, 'success');
    } else {
      resultEl.innerHTML = `<div class="result-error" style="margin-top:8px">❌ ${escHtml(res.error)}</div>`;
      toast(`${step} failed`, 'error');
    }
  } catch (e) {
    statusEl.textContent = '✕ Error';
    statusEl.className   = 'seo-status error';
    btnEl.disabled = false;
    resultEl.innerHTML = `<div class="result-error" style="margin-top:8px">❌ ${e.message}</div>`;
    toast('Request failed', 'error');
  }
}

function renderSEOResult(step, data) {
  if (step === 'research') {
    const kws = (data.keywords || []);
    if (!kws.length) return `<p style="color:var(--text-muted);font-size:12px">${data.summary || 'No keywords found'}</p>`;
    return `
      <p style="font-size:11px;color:var(--text-secondary);margin-bottom:6px">
        ${data.summary || `${kws.length} keywords found`} • Showing all ${kws.length}
      </p>
      <div class="kw-table-scroll">
        <table class="kw-table">
          <thead><tr>
            <th>Keyword</th><th>Vol.</th><th>Diff.</th><th>Intent</th>
          </tr></thead>
          <tbody>${kws.map(k => `
            <tr>
              <td>${escHtml(k.keyword||'')}</td>
              <td>${k.search_volume_estimate||0}</td>
              <td>${k.difficulty||0}</td>
              <td><span class="intent-badge intent-${(k.intent||'informational').toLowerCase()}">${k.intent||''}</span></td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>`;
  }

  if (step === 'technical') {
    const recs = (data.recommendations || []).slice(0, 3);
    return `
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-val">${data.health_score || 0}%</div>
          <div class="kpi-label">Health Score</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val">${data.passed || 0}</div>
          <div class="kpi-label">Passed</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-val">${data.failed || 0}</div>
          <div class="kpi-label">Failed</div>
        </div>
      </div>
      ${recs.length ? `
      <ul class="insight-list">${recs.map(r => `<li><strong>${r.priority||''}</strong> — ${escHtml(r.fix||r.issue||'')}</li>`).join('')}</ul>` : ''}`;
  }

  if (step === 'backlinks') {
    const anchors = (data.anchor_texts || []).slice(0, 4);
    const plats   = (data.configured_platforms || []);
    return `
      ${anchors.length ? `
      <p style="font-size:11px;color:var(--text-muted);margin-bottom:4px">TOP ANCHOR TEXTS</p>
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">
        ${anchors.map(a => `<span class="chip">${escHtml(a.text||a||'')}</span>`).join('')}
      </div>` : ''}
      ${plats.length ? `
      <p style="font-size:11px;color:var(--text-muted);margin-bottom:4px">PLATFORMS</p>
      <div style="display:flex;gap:8px">
        ${plats.map(p => `
          <div class="campaign-tag ${p.configured ? 'active-tag' : ''}">
            ${p.name} ${p.configured ? '✓' : '—'}
          </div>`).join('')}
      </div>` : ''}`;
  }

  if (step === 'performance') {
    const kpis = (data.kpis || []).slice(0, 4);
    const periodLabel = (data.period || 'month') === 'year' ? 'This Year' : 'This Month';
    return `
      <p style="font-size:11px;color:var(--text-muted);margin-bottom:8px">Period: ${escHtml(periodLabel)}</p>
      <div class="kpi-row">
        ${kpis.map(k => `
          <div class="kpi-card">
            <div class="kpi-val">${escHtml(String(k.value||''))}</div>
            <div class="kpi-label">${escHtml(k.metric||'')}</div>
            <div class="kpi-change ${(k.change||'').includes('-') ? 'down' : 'up'}">${escHtml(k.change||'')}</div>
          </div>`).join('')}
      </div>
      ${data.insights && data.insights.length ? `
      <ul class="insight-list">${data.insights.slice(0,3).map(i => `<li>${escHtml(i)}</li>`).join('')}</ul>` : ''}`;
  }

  return `<div class="result-info">${data.summary || 'Completed'}</div>`;
}

function getSelectedAutopostPlatforms() {
  const platforms = [];
  if (document.getElementById('plat-devto').checked) platforms.push('devto');
  if (document.getElementById('plat-hashnode').checked) platforms.push('hashnode');
  return platforms;
}

function renderSEODraftPreview(blog) {
  const previewEl = document.getElementById('seo-autopost-preview');
  if (!previewEl || !blog) return;
  previewEl.innerHTML = `
    <label class="field-label">Title</label>
    <input type="text" id="seo-autopost-title" class="input-field" value="${escAttr(blog.title || '')}">
    <label class="field-label">Meta Description</label>
    <textarea id="seo-autopost-meta" class="input-field" rows="2">${escHtml(blog.meta_description || '')}</textarea>
    <label class="field-label">Tags (comma separated)</label>
    <input type="text" id="seo-autopost-tags" class="input-field" value="${escAttr((blog.tags || []).join(', '))}">
    <label class="field-label">Introduction</label>
    <textarea id="seo-autopost-intro" class="input-field" rows="5">${escHtml(blog.intro || '')}</textarea>
    <label class="field-label">Body (Markdown)</label>
    <textarea id="seo-autopost-body" class="input-field" rows="12">${escHtml(blog.body || '')}</textarea>
    <label class="field-label">Conclusion</label>
    <textarea id="seo-autopost-conclusion" class="input-field" rows="4">${escHtml(blog.conclusion || '')}</textarea>
  `;
}

function collectSEODraftFromUI() {
  const tagsRaw = document.getElementById('seo-autopost-tags')?.value || '';
  return {
    title: document.getElementById('seo-autopost-title')?.value?.trim() || '',
    meta_description: document.getElementById('seo-autopost-meta')?.value?.trim() || '',
    intro: document.getElementById('seo-autopost-intro')?.value?.trim() || '',
    body: document.getElementById('seo-autopost-body')?.value?.trim() || '',
    conclusion: document.getElementById('seo-autopost-conclusion')?.value?.trim() || '',
    tags: tagsRaw.split(',').map(t => t.trim()).filter(Boolean).slice(0, 5)
  };
}

async function generateSEOAutopostPreview(humanize = false) {
  if (!state.seo.topic) {
    const t = document.getElementById('seo-topic').value.trim();
    if (!t) { toast('Set your SEO topic first!', 'error'); return; }
    state.seo.topic = t;
  }

  const statusEl = document.getElementById('seo-status-autopost');
  const resultEl = document.getElementById('seo-result-autopost');
  const generateBtn = document.getElementById('btn-seo-autopost-generate');
  const humanBtn = document.getElementById('btn-seo-autopost-humanize');
  const publishBtn = document.getElementById('btn-seo-autopost-publish');
  const previewEl = document.getElementById('seo-autopost-preview');

  statusEl.textContent = '⟳ Generating';
  statusEl.className   = 'seo-status running';
  generateBtn.disabled = true;
  humanBtn.disabled = true;
  publishBtn.disabled = true;
  previewEl.innerHTML = '<div style="display:flex;align-items:center;gap:8px"><div class="spinner-ring"></div> Generating blog preview...</div>';
  resultEl.innerHTML = '';

  try {
    const res = await api('/api/seo/autopost/preview', { topic: state.seo.topic, humanize });

    if (!res.success) {
      statusEl.textContent = '✕ Error';
      statusEl.className = 'seo-status error';
      previewEl.innerHTML = `<div class="result-error">❌ ${escHtml(res.error || 'Preview generation failed')}</div>`;
      return;
    }

    state.seo.autopostDraft = res.blog_content || null;
    renderSEODraftPreview(state.seo.autopostDraft);
    statusEl.textContent = '✓ Draft Ready';
    statusEl.className = 'seo-status done';
    publishBtn.disabled = false;
    toast(humanize ? 'Humanized draft regenerated!' : 'Draft generated. Review before publishing.', 'success');

  } catch (e) {
    statusEl.textContent = '✕ Error';
    statusEl.className   = 'seo-status error';
    previewEl.innerHTML = `<div class="result-error">❌ ${e.message}</div>`;
    toast('Draft generation failed', 'error');
  } finally {
    generateBtn.disabled = false;
    humanBtn.disabled = false;
  }
}

async function publishSEOAutopost() {
  const platforms = getSelectedAutopostPlatforms();
  if (!platforms.length) { toast('Select at least one platform', 'error'); return; }

  const statusEl = document.getElementById('seo-status-autopost');
  const resultEl = document.getElementById('seo-result-autopost');
  const publishBtn = document.getElementById('btn-seo-autopost-publish');

  if (!document.getElementById('seo-autopost-title')) {
    toast('Generate a draft first', 'error');
    return;
  }

  const blog = collectSEODraftFromUI();
  if (!blog.title || !blog.body) {
    toast('Title and body are required before publishing', 'error');
    return;
  }

  statusEl.textContent = '⟳ Posting';
  statusEl.className = 'seo-status running';
  publishBtn.disabled = true;
  resultEl.innerHTML = '<div style="display:flex;align-items:center;gap:8px"><div class="spinner-ring"></div> Publishing to selected platforms...</div>';

  try {
    const res = await api('/api/seo/autopost/publish', {
      topic: state.seo.topic,
      platforms,
      blog
    });

    if (!res.success) {
      statusEl.textContent = '✕ Error';
      statusEl.className = 'seo-status error';
      resultEl.innerHTML = `<div class="result-error">❌ ${escHtml(res.error || 'Publish failed')}</div>`;
      return;
    }

    statusEl.textContent = '✓ Done';
    statusEl.className = 'seo-status done';

    let html = '';
    const plts = res.platforms || {};
    for (const [plat, result] of Object.entries(plts)) {
      if (result.success) {
        html += `<div class="result-success" style="margin-bottom:6px">
          ✅ <strong>${plat}</strong> — Posted!
          ${result.url ? `<a href="${escHtml(result.url)}" target="_blank" style="color:var(--accent-2);margin-left:8px">View →</a>` : ''}
        </div>`;
      } else {
        html += `<div class="result-error" style="margin-bottom:6px">❌ <strong>${plat}</strong> — ${escHtml(result.error || 'Failed')}</div>`;
      }
    }
    resultEl.innerHTML = html || '<div class="result-info">No platforms processed</div>';
    toast('Publish completed for selected platforms', 'success');
  } catch (e) {
    statusEl.textContent = '✕ Error';
    statusEl.className = 'seo-status error';
    resultEl.innerHTML = `<div class="result-error">❌ ${e.message}</div>`;
    toast('Publish failed', 'error');
  } finally {
    publishBtn.disabled = false;
  }
}

async function downloadPDF() {
  if (!state.seo.topic) {
    const t = document.getElementById('seo-topic').value.trim();
    if (!t) { toast('Set your SEO topic first!', 'error'); return; }
    state.seo.topic = t;
  }

  const statusEl = document.getElementById('seo-status-pdf');
  const resultEl = document.getElementById('seo-result-pdf');
  const btnEl    = document.getElementById('btn-seo-pdf');

  statusEl.textContent = '⟳ Generating';
  statusEl.className   = 'seo-status running';
  btnEl.disabled = true;
  resultEl.innerHTML = '<div style="display:flex;align-items:center;gap:8px"><div class="spinner-ring"></div> Building PDF report...</div>';
  toast('Generating PDF — this may take a moment', 'info');

  try {
    const res = await fetch('/api/seo/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: state.seo.topic })
    });

    if (res.ok && res.headers.get('content-type')?.includes('pdf')) {
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href = url;
      a.download = `seo_report_${state.seo.topic.substring(0,15).replace(/\s/g,'_')}.pdf`;
      a.click();
      URL.revokeObjectURL(url);

      statusEl.textContent = '✓ Done';
      statusEl.className   = 'seo-status done';
      resultEl.innerHTML   = '<div class="result-success">✅ PDF downloaded!</div>';
      toast('PDF report downloaded!', 'success');
    } else {
      const data = await res.json();
      statusEl.textContent = '✕ Error';
      statusEl.className   = 'seo-status error';
      resultEl.innerHTML   = `<div class="result-error">❌ ${data.error || 'PDF generation failed'}</div>`;
      toast('PDF generation failed', 'error');
    }
    btnEl.disabled = false;
  } catch (e) {
    statusEl.textContent = '✕ Error';
    statusEl.className   = 'seo-status error';
    btnEl.disabled = false;
    resultEl.innerHTML = `<div class="result-error">❌ ${e.message}</div>`;
    toast('Error: ' + e.message, 'error');
  }
}

async function runFullSEO() {
  const t = document.getElementById('seo-topic').value.trim();
  if (!t) { toast('Enter an SEO topic first!', 'error'); return; }
  state.seo.topic = t;

  toast('Running full SEO pipeline...', 'info', 6000);
  showLoading('Running full SEO pipeline...');

  // Run all steps sequentially
  const steps = ['research', 'technical', 'backlinks', 'performance'];
  for (const step of steps) {
    document.getElementById('loadingText').textContent = `Running ${step}...`;
    await runSEOStep(step);
  }

  hideLoading();
  toast('✅ Full SEO pipeline complete!', 'success', 5000);
}

// ── UTILS ─────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}
function escAttr(str) {
  return String(str).replace(/'/g,"\\'").replace(/"/g,'&quot;');
}
