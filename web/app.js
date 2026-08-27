const state = {
  studentId: null,
  demo: null,
  overview: null,
  graph: null,
  lastAdvisorResult: null,
  activeView: 'overview'
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function formatReply(text) {
  return escapeHtml(text || '')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^### (.*)$/gm, '<strong class="reply-heading">$1</strong>')
    .replace(/\n/g, '<br>');
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {'Content-Type':'application/json', ...(options.headers || {})},
    ...options
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || `Request failed (${response.status})`);
  return payload;
}

function toast(message) {
  const node = $('#toast');
  node.textContent = message;
  node.classList.add('show');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => node.classList.remove('show'), 2600);
}

function setView(view) {
  state.activeView = view;
  $$('.nav-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.view === view));
  $$('[data-view-panel]').forEach(panel => panel.classList.toggle('active', panel.dataset.viewPanel === view));
  if (view === 'graph' && state.graph) renderGraph();
  if (view === 'faculty') loadPetitions();
  window.scrollTo({top: 0, behavior: 'smooth'});
}

async function bootstrap() {
  bindShell();
  await checkHealth();
  state.demo = await api('/api/demo');
  populateStudents();
  renderDemoPrompts();
  if (state.demo.students.length) {
    state.studentId = state.demo.students[0].id;
    $('#student-select').value = state.studentId;
    await loadStudentWorkspace();
  }
  loadGraph().catch(error => toast(error.message));
}

function bindShell() {
  $$('.nav-btn').forEach(btn => btn.addEventListener('click', () => setView(btn.dataset.view)));
  $$('[data-open-view]').forEach(btn => btn.addEventListener('click', () => setView(btn.dataset.openView)));
  $('#student-select').addEventListener('change', async event => {
    state.studentId = event.target.value;
    state.lastAdvisorResult = null;
    resetAdvisorPanels();
    await loadStudentWorkspace();
    toast('Student context changed');
  });
  $('#chat-form').addEventListener('submit', sendChat);
  $('#chat-input').addEventListener('input', event => {
    event.target.style.height = 'auto';
    event.target.style.height = Math.min(150, event.target.scrollHeight) + 'px';
  });
  $('#chat-input').addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      $('#chat-form').requestSubmit();
    }
  });
  $('#graph-search').addEventListener('input', renderGraph);
  $('#graph-reset').addEventListener('click', () => {
    $('#graph-search').value = '';
    renderGraph();
    $('#graph-inspector').innerHTML = '<div class="empty-state">Select a course node to inspect its relationships.</div>';
  });
  $('#refresh-petitions').addEventListener('click', loadPetitions);
  $('#petition-form').addEventListener('submit', submitPetition);
}

async function checkHealth() {
  try {
    const health = await api('/api/health');
    const pill = $('#system-status');
    pill.classList.add('online');
    pill.innerHTML = `<i></i> ${escapeHtml(health.database)} · ${health.gemini_configured ? 'Gemini ready' : 'Gemini fallback'}`;
  } catch (error) {
    $('#system-status').innerHTML = '<i></i> Offline';
    toast(error.message);
  }
}

function populateStudents() {
  const select = $('#student-select');
  select.innerHTML = state.demo.students.map(student =>
    `<option value="${escapeHtml(student.id)}">${escapeHtml(student.name)} · ${escapeHtml(student.id)}</option>`
  ).join('');
}

function renderDemoPrompts() {
  const root = $('#demo-prompts');
  root.innerHTML = state.demo.prompts.map((item, index) => `
    <article class="demo-card">
      <span>SCENARIO ${String(index + 1).padStart(2,'0')}</span>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.prompt)}</p>
      <button class="btn ghost small" data-demo-prompt="${index}">Run scenario →</button>
    </article>
  `).join('');
  $$('[data-demo-prompt]', root).forEach(btn => btn.addEventListener('click', () => {
    const item = state.demo.prompts[Number(btn.dataset.demoPrompt)];
    setView('advisor');
    $('#chat-input').value = item.prompt;
    $('#chat-form').requestSubmit();
  }));

  $('#quick-prompts').innerHTML = state.demo.prompts.map((item, index) =>
    `<button type="button" data-quick="${index}">${escapeHtml(item.title)}</button>`
  ).join('');
  $$('[data-quick]').forEach(btn => btn.addEventListener('click', () => {
    $('#chat-input').value = state.demo.prompts[Number(btn.dataset.quick)].prompt;
    $('#chat-input').focus();
  }));
}

async function loadStudentWorkspace() {
  if (!state.studentId) return;
  state.overview = await api(`/api/overview/${encodeURIComponent(state.studentId)}`);
  renderMetrics();
  renderProfile();
  renderPathway();
  $('#curriculum-source').textContent = state.overview.source_reference || 'Curriculum source available';
}

function renderMetrics() {
  const student = state.overview.student;
  const metrics = [
    [state.overview.completed_credits_observed, 'observed completed credits', 'Computed from completed curriculum courses'],
    [student.completed.length, 'courses completed', student.current_semester || 'Current record'],
    [state.overview.remaining_core_count, 'remaining core courses', 'Elective choice slots remain flexible'],
    [student.standing || '—', 'academic standing', student.expected_grad || 'Graduation target']
  ];
  $('#metric-grid').innerHTML = metrics.map(([value,label,note]) => `
    <article class="metric"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span><small>${escapeHtml(note)}</small></article>
  `).join('');
}

function renderProfile() {
  const s = state.overview.student;
  const initials = (s.name || 'Student').split(/\s+/).slice(0,2).map(part => part[0]).join('');
  $('#profile-card').innerHTML = `
    <div class="profile-main">
      <div class="profile-avatar">${escapeHtml(initials)}</div>
      <div><h3>${escapeHtml(s.name)}</h3><p>${escapeHtml(s.id)} · ${escapeHtml(s.major)}</p></div>
    </div>
    <div class="profile-tags">
      <span class="tag">${escapeHtml(s.current_semester || 'Semester not set')}</span>
      <span class="tag">GPA ${escapeHtml(s.gpa ?? '—')}</span>
      <span class="tag">${escapeHtml(s.reg_regulation || 'C24')}</span>
      <span class="tag">${escapeHtml(s.expected_grad || 'Target not set')}</span>
      ${s.honours_enrolled ? `<span class="tag">Optional track: ${escapeHtml(s.honours_track || 'Honours/Minor')}</span>` : ''}
    </div>
  `;
}

function renderPathway() {
  const board = $('#pathway-board');
  board.innerHTML = state.overview.semesters.map(semester => {
    const courses = semester.courses.map(course => `
      <div class="course-chip ${escapeHtml(course.state)}">
        <strong>${escapeHtml(course.id)} · ${escapeHtml(course.name)}</strong>
        <span>${escapeHtml(course.credits)} credits · ${escapeHtml(course.state)}</span>
      </div>
    `).join('');
    const slots = (semester.choice_slots || []).map(slot =>
      `<div class="choice-slot">${escapeHtml(slot.count || 1)} × ${escapeHtml(slot.type.replaceAll('_',' '))} choice${slot.credits_each ? ` · ${escapeHtml(slot.credits_each)} credits` : ''}</div>`
    ).join('');
    const optional = semester.optional_track_slot ? '<div class="choice-slot">Optional Honours / Minor slot — not a base-degree requirement</div>' : '';
    return `
      <section class="semester">
        <div class="semester-head"><h3>${escapeHtml(semester.semester)}</h3><span>Semester ${escapeHtml(semester.semester_index)}</span></div>
        ${courses}${slots}${optional}
      </section>
    `;
  }).join('');
}

function addMessage(role, html) {
  const stream = $('#chat-stream');
  if (role === 'user') {
    stream.insertAdjacentHTML('beforeend', `<div class="message user"><div><strong>You</strong><p>${escapeHtml(html)}</p></div><span class="avatar">YOU</span></div>`);
  } else {
    stream.insertAdjacentHTML('beforeend', `<div class="message assistant"><span class="avatar">AI</span><div><strong>AcadGraph AI</strong><div class="reply">${html}</div></div></div>`);
  }
  stream.scrollTop = stream.scrollHeight;
}

async function sendChat(event) {
  event?.preventDefault();
  const input = $('#chat-input');
  const question = input.value.trim();
  if (!question || !state.studentId) return;

  addMessage('user', question);
  input.value = '';
  input.style.height = 'auto';
  input.disabled = true;
  $('.send-btn').disabled = true;
  const stream = $('#chat-stream');
  stream.insertAdjacentHTML('beforeend', '<div class="message assistant" id="thinking"><span class="avatar">AI</span><div><strong>AcadGraph AI</strong><span class="loading"><i></i><i></i><i></i> Agents are reasoning and verifying</span></div></div>');
  stream.scrollTop = stream.scrollHeight;

  try {
    const result = await api('/api/chat', {
      method: 'POST',
      body: JSON.stringify({student_id: state.studentId, question})
    });
    state.lastAdvisorResult = result;
    $('#thinking')?.remove();
    addMessage('assistant', formatReply(result.reply || 'No response generated.'));
    renderVerification(result);
    renderTrace(result.agent_trace || []);
    renderCitations(result.citation_details || []);
    if (result.pathway) renderAgentPathwayHint(result.pathway);
  } catch (error) {
    $('#thinking')?.remove();
    addMessage('assistant', `<span style="color:var(--red)">${escapeHtml(error.message)}</span>`);
  } finally {
    input.disabled = false;
    $('.send-btn').disabled = false;
    input.focus();
  }
}

function renderVerification(result) {
  const verification = result.verification || {};
  const decision = verification.decision || 'ADVISORY_OK';
  const tone = decision.includes('BLOCKED') ? 'block' : decision.includes('FACULTY') || decision.includes('CANDIDATE') ? 'warn' : 'good';
  const blocks = verification.blocking_conflicts || [];
  const warnings = verification.readiness_warnings || [];
  const root = $('#verification-output');
  root.innerHTML = `
    <div class="decision ${tone}"><div><strong>${escapeHtml(decision)}</strong><small>Deterministic final gate</small></div><span>${tone === 'good' ? '✓' : tone === 'warn' ? '!' : '×'}</span></div>
    ${blocks.length ? `<div class="relation-list">${blocks.map(item => `<div class="relation-item">FORMAL BLOCK<small>${escapeHtml(item.message || JSON.stringify(item))}</small></div>`).join('')}</div>` : ''}
    ${warnings.length ? `<div class="relation-list">${warnings.map(item => `<div class="relation-item">READINESS WARNING<small>${escapeHtml(item.message || JSON.stringify(item))}</small></div>`).join('')}</div>` : ''}
    ${result.risk ? `<div class="relation-list"><div class="relation-item">Planning risk: ${escapeHtml(result.risk.level || '—')}<small>${escapeHtml((result.risk.factors || []).join(' · '))}</small></div></div>` : ''}
    ${result.needs_faculty_approval ? '<button class="btn primary small" id="send-agent-review" style="margin-top:12px">Send AI packet to faculty →</button>' : ''}
  `;
  $('#send-agent-review')?.addEventListener('click', sendLastAgentPacket);
}

function renderTrace(trace) {
  $('#agent-trace').innerHTML = trace.length ? trace.map((item, index) => `
    <div class="trace-item">
      <span class="step">${String(index + 1).padStart(2,'0')}</span>
      <div><strong>${escapeHtml(item.agent)}</strong><small>${escapeHtml(item.action)}</small></div>
      <span class="${item.status === 'degraded' ? 'status-degraded' : 'status-ok'}">${escapeHtml(item.status || 'ok')}</span>
    </div>
  `).join('') : '<div class="empty-state">No agent trace returned.</div>';
}

function renderCitations(citations) {
  $('#citation-output').innerHTML = citations.length ? citations.map(citation => `
    <div class="citation"><strong>${escapeHtml(citation.reference || 'Academic source')}</strong><small>${escapeHtml(citation.source_status || 'UNVERIFIED')}</small><small>${escapeHtml(citation.content || '')}</small></div>
  `).join('') : '<div class="empty-state">No source citations were returned for this query.</div>';
}

function resetAdvisorPanels() {
  $('#verification-output').innerHTML = '<div class="empty-state">Run an academic question to see the deterministic decision.</div>';
  $('#agent-trace').innerHTML = '<div class="empty-state">Agents will appear here in execution order.</div>';
  $('#citation-output').innerHTML = '<div class="empty-state">Source provenance will appear here.</div>';
}

function renderAgentPathwayHint(pathway) {
  if (!pathway) return;
  const summary = typeof pathway === 'string' ? pathway : JSON.stringify(pathway);
  toast(`PathwayAgent returned a candidate plan (${summary.length} chars)`);
}

async function loadGraph() {
  state.graph = await api('/api/graph');
  if (state.activeView === 'graph') renderGraph();
}

function graphVisibleData() {
  if (!state.graph) return {nodes:[], edges:[]};
  const search = $('#graph-search')?.value.trim().toLowerCase() || '';
  const connected = new Set(state.graph.edges.flatMap(edge => [edge.source, edge.target]));
  let nodes = state.graph.nodes.filter(node => connected.has(node.id) || Number(node.semester || 0) >= 3);
  if (search) {
    const matches = new Set(nodes.filter(node => `${node.id} ${node.name}`.toLowerCase().includes(search)).map(node => node.id));
    state.graph.edges.forEach(edge => {
      if (matches.has(edge.source)) matches.add(edge.target);
      if (matches.has(edge.target)) matches.add(edge.source);
    });
    nodes = nodes.filter(node => matches.has(node.id));
  }
  nodes = nodes.slice(0, 76);
  const ids = new Set(nodes.map(node => node.id));
  const edges = state.graph.edges.filter(edge => ids.has(edge.source) && ids.has(edge.target));
  return {nodes, edges};
}

function renderGraph() {
  const svg = $('#graph-canvas');
  if (!state.graph) {
    svg.innerHTML = '<text x="40" y="60" fill="#98abc0">Graph loading…</text>';
    return;
  }
  const {nodes, edges} = graphVisibleData();
  const bySemester = new Map();
  nodes.forEach(node => {
    const sem = Math.max(1, Math.min(8, Number(node.semester || 4)));
    if (!bySemester.has(sem)) bySemester.set(sem, []);
    bySemester.get(sem).push(node);
  });
  const positions = new Map();
  for (const [sem, list] of bySemester.entries()) {
    list.sort((a,b) => a.id.localeCompare(b.id));
    const x = 70 + (sem - 1) * 150;
    list.forEach((node, index) => {
      const spacing = Math.max(36, 560 / Math.max(1, list.length));
      const y = 55 + index * spacing + ((sem % 2) * 14);
      positions.set(node.id, {x, y: Math.min(625, y)});
    });
  }

  const edgeMarkup = edges.map(edge => {
    const a = positions.get(edge.source), b = positions.get(edge.target);
    if (!a || !b) return '';
    const cls = edge.type === 'FORMAL_PREREQUISITE' ? 'formal' : edge.type === 'EQUIVALENT_TO' ? 'equivalent' : 'knowledge';
    return `<line class="graph-edge ${cls}" data-edge="${escapeHtml(edge.source)}|${escapeHtml(edge.target)}" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" />`;
  }).join('');

  const nodeMarkup = nodes.map(node => {
    const pos = positions.get(node.id);
    const hue = String(node.category || '').toLowerCase().includes('elective') ? '#a99cff' : node.department === 'Mathematics' ? '#ffd37a' : '#6ee7f2';
    return `<g class="graph-node" data-node="${escapeHtml(node.id)}" transform="translate(${pos.x},${pos.y})">
      <circle r="9" fill="${hue}" fill-opacity=".9" stroke="#07111f" stroke-width="3"></circle>
      <text class="node-label" x="14" y="3">${escapeHtml(node.id)}</text>
    </g>`;
  }).join('');

  svg.innerHTML = edgeMarkup + nodeMarkup;
  $$('.graph-node', svg).forEach(nodeEl => nodeEl.addEventListener('click', () => inspectGraphNode(nodeEl.dataset.node)));
}

function inspectGraphNode(id) {
  const node = state.graph.nodes.find(item => item.id === id);
  if (!node) return;
  const relations = state.graph.edges.filter(edge => edge.source === id || edge.target === id);
  const root = $('#graph-inspector');
  root.innerHTML = `
    <span class="inspector-code">${escapeHtml(node.id)}</span>
    <h3 class="inspector-title">${escapeHtml(node.name)}</h3>
    <div class="profile-tags"><span class="tag">${escapeHtml(node.department)}</span><span class="tag">${escapeHtml(node.credits)} credits</span><span class="tag">Semester ${escapeHtml(node.semester || '—')}</span></div>
    <div class="relation-list">
      ${relations.length ? relations.map(edge => {
        const incoming = edge.target === id;
        const other = incoming ? edge.source : edge.target;
        const relation = edge.type === 'FORMAL_PREREQUISITE' ? 'FORMAL' : edge.type === 'EQUIVALENT_TO' ? 'EQUIVALENCY' : 'READINESS';
        return `<div class="relation-item">${escapeHtml(relation)} · ${incoming ? 'from' : 'to'} ${escapeHtml(other)}<small>${edge.blocking ? 'Registration-blocking only when formally sourced' : edge.type === 'REQUIRES_KNOWLEDGE_OF' ? 'Non-blocking prerequisite knowledge' : 'Faculty review may be required'}</small></div>`;
      }).join('') : '<div class="empty-state">No displayed course relationships.</div>'}
    </div>
  `;
  const related = new Set(relations.flatMap(edge => [edge.source, edge.target]));
  $$('.graph-node').forEach(el => el.classList.toggle('dimmed', !related.has(el.dataset.node)));
  $$('.graph-edge').forEach(el => {
    const [a,b] = el.dataset.edge.split('|');
    el.classList.toggle('dimmed', !related.has(a) || !related.has(b));
  });
}

async function loadPetitions() {
  try {
    const data = await api('/api/faculty/petitions');
    const root = $('#petition-list');
    const items = data.petitions || [];
    root.innerHTML = items.length ? items.map(item => `
      <article class="petition">
        <div class="petition-head"><strong>${escapeHtml(item.petition_id)} · ${escapeHtml(item.course_id || 'General review')}</strong><span class="state-pill ${String(item.status || 'pending').toLowerCase()}">${escapeHtml(item.status || 'PENDING')}</span></div>
        <p>${escapeHtml(item.reason || item.request_type || 'Academic exception review')}</p>
        <div class="petition-meta"><span class="tag">${escapeHtml(item.student_id)}</span><span class="tag">Human decision required</span></div>
        ${String(item.status || '').toUpperCase() === 'PENDING' ? `<div class="petition-actions"><button class="btn primary small" data-review="${escapeHtml(item.petition_id)}" data-decision="APPROVED">Approve</button><button class="btn ghost small" data-review="${escapeHtml(item.petition_id)}" data-decision="REJECTED">Reject</button></div>` : ''}
      </article>
    `).join('') : '<div class="empty-state">No faculty review requests yet. Create one from an agent escalation or the demo form.</div>';
    $$('[data-review]', root).forEach(btn => btn.addEventListener('click', () => reviewPetition(btn.dataset.review, btn.dataset.decision)));
  } catch (error) {
    $('#petition-list').innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

async function submitPetition(event) {
  event.preventDefault();
  const reason = $('#petition-reason').value.trim();
  const course = $('#petition-course').value.trim();
  if (!reason) return;
  await api('/api/faculty/petitions', {
    method:'POST',
    body:JSON.stringify({student_id:state.studentId, course_id:course || null, reason})
  });
  $('#petition-form').reset();
  toast('Sent to faculty review');
  await loadPetitions();
}

async function sendLastAgentPacket() {
  const result = state.lastAdvisorResult;
  if (!result) return;
  const candidate = (result.substitutions || [])[0] || {};
  await api('/api/faculty/petitions', {
    method:'POST',
    body:JSON.stringify({
      student_id:state.studentId,
      course_id:candidate.course_id || null,
      reason:'Agentic advisor identified an exception/substitution case that requires human review.',
      evidence:result.citation_details || [],
      faculty_packet:result.faculty_packet || null
    })
  });
  toast('AI review packet sent to faculty');
  setView('faculty');
}

async function reviewPetition(id, decision) {
  await api(`/api/faculty/petitions/${encodeURIComponent(id)}/review`, {
    method:'POST',
    body:JSON.stringify({decision, reviewer:'Hackathon Faculty Reviewer', comments:`Demo ${decision.toLowerCase()} decision from human governance UI.`})
  });
  toast(`Petition ${decision.toLowerCase()}`);
  await loadPetitions();
}

bootstrap().catch(error => {
  console.error(error);
  toast(error.message);
});
