const API = '';
let signingOut = false;

async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || 'Request failed');
  return data;
}

function esc(value) {
  return String(value ?? '').replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
}

async function currentStudent() {
  const savedId = localStorage.getItem('academic_advisor_permanent_active_user_v3');
  if (!savedId && localStorage.getItem('academic_advisor_faculty_session') === 'active') {
    return { id:'', name:'Faculty reviewer', major:'Faculty governance', completed:[] };
  }
  if (!savedId) return null;
  try { return await api(`/api/student/${encodeURIComponent(savedId)}`); } catch { return null; }
}

function isFacultySession() {
  return localStorage.getItem('academic_advisor_faculty_session') === 'active';
}

function signOut() {
  if (signingOut) return;
  signingOut = true;
  try {
    fetch('/api/auth/logout', { method: 'POST' }).catch(function () {});
  } catch (e) {
    console.warn('Backend logout call skipped:', e);
  }
  try {
    localStorage.removeItem('academic_advisor_permanent_active_user_v3');
    localStorage.removeItem('academic_advisor_faculty_session');
    localStorage.clear();
    sessionStorage.clear();
  } catch (e) {
    console.error('Sign out cleanup error:', e);
  }
  window.location.replace('index.html');
}
window.signOut = signOut;

function toast(message) {
  const node = document.getElementById('toast');
  if (node) {
    node.textContent = message;
    node.style.display = 'block';
    setTimeout(() => node.style.display = 'none', 2800);
  }
}

function nav(active, faculty) {
  const items = [
    ['home.html', 'Dashboard', 'home'],
    ['advisor.html', 'Advisor', 'advisor'],
    ['pathway.html', 'Degree pathway', 'pathway'],
    ['graph.html', 'Knowledge graph', 'graph'],
    ['governance.html', 'Faculty review', 'governance']
  ];
  const visibleItems = faculty ? items.filter(([, , key]) => key === 'governance') : items;
  return visibleItems.map(([href,label,key]) => `<a class="${key === active ? 'active' : ''}" href="${href}">${label}</a>`).join('');
}

async function initShell(active) {
  const student = await currentStudent();
  if (!student) { location.href = 'index.html'; return null; }
  const faculty = isFacultySession();
  if (faculty && active !== 'governance') { location.href = 'governance.html'; return null; }
  const appbar = document.querySelector('.appbar');
  if (appbar) {
    appbar.insertAdjacentHTML('afterbegin', `<a class="brand" href="${faculty ? 'governance.html' : 'home.html'}"><span class="brand-mark">AA</span><span>Academic Advisor</span></a>`);
  }
  const navNode = document.querySelector('.nav');
  if (navNode) navNode.innerHTML = nav(active, faculty);
  const userbar = document.querySelector('.userbar');
  if (userbar) {
    userbar.innerHTML = `<span class="user-chip">${esc(student.name)} · ${esc(student.id || 'Faculty')}</span><button class="btn" type="button" data-action="signout">Sign out</button>`;
    const btn = userbar.querySelector('[data-action="signout"]');
    if (btn) {
      btn.onclick = function(e) {
        e.preventDefault();
        signOut();
      };
    }
  }
  if (!document.getElementById('global-chatbot-widget') && !faculty) {
    initGlobalChatbot(student);
  }
  return student;
}

function coursePrereqs(course) {
  return course.prereqs || (course.prerequisite_groups || []).flatMap(group => (group.prerequisites || []).map(item => item.course_id));
}

function courseRow(course, student) {
  const done = (student?.completed || []).includes(course.id);
  return `<div class="data-row"><div><span class="code">${esc(course.id)}</span><strong> ${esc(course.name)}</strong><div class="muted">${esc(course.description || course.desc || 'Course information available in the C24 catalog.')}</div></div><div><span class="badge">${esc(course.credits || 0)} credits</span> <span class="badge ${done ? '' : 'warn'}">${done ? 'Completed' : `Semester ${esc(course.sem || '?')}`}</span></div></div>`;
}

window.api = api;
window.esc = esc;
window.toast = toast;
window.signOut = signOut;
window.initShell = initShell;
window.currentStudent = currentStudent;
window.coursePrereqs = coursePrereqs;
window.courseRow = courseRow;
window.initGlobalChatbot = initGlobalChatbot;

function initGlobalChatbot(student) {
  const html = `
    <div id="global-chatbot-widget" class="global-chatbot-widget">
      <div id="global-chatbot-window" class="global-chatbot-window">
        <div class="global-chatbot-header">
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#4ade80;"></span>
            <span>⚡ Autonomous Advisor AI</span>
          </div>
          <button id="global-chatbot-close" aria-label="Close chat">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
        </div>
        <div id="global-chatbot-messages" class="global-chatbot-messages">
          <div class="global-chatbot-message assistant">
            <strong>Autonomous AI Advisor</strong>
            <p>Hi ${esc(student.name.split(' ')[0])}! Ask me to verify course readiness, generate a degree pathway, identify bottlenecks, or review substitution options.</p>
          </div>
        </div>
        <div class="global-chatbot-chips">
          <button type="button" class="global-chip" data-prompt="Audit 24CS209 for Sem 1">⚡ Audit 24CS209</button>
          <button type="button" class="global-chip" data-prompt="Generate my optimal 4-year degree pathway">🗺️ Degree Pathway</button>
          <button type="button" class="global-chip" data-prompt="What courses are blocking my graduation?">🚨 Bottlenecks</button>
        </div>
        <form id="global-chatbot-form" class="global-chatbot-input">
          <textarea name="question" placeholder="Ask about courses, pathways, conflicts, bottlenecks, or substitutions..." required rows="1"></textarea>
          <button type="submit" aria-label="Send">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </form>
      </div>
      <button id="global-chatbot-toggle" class="global-chatbot-toggle" aria-label="Open chat">
        <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
      </button>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', html);

  const toggleBtn = document.getElementById('global-chatbot-toggle');
  const closeBtn = document.getElementById('global-chatbot-close');
  const chatWin = document.getElementById('global-chatbot-window');
  const form = document.getElementById('global-chatbot-form');
  const msgs = document.getElementById('global-chatbot-messages');
  const chips = document.querySelectorAll('.global-chip');

  chips.forEach(chip => {
    chip.onclick = () => {
      const p = chip.getAttribute('data-prompt');
      if (p && form.elements.question) {
        form.elements.question.value = p;
        form.dispatchEvent(new Event('submit'));
      }
    };
  });

  toggleBtn.onclick = () => chatWin.classList.add('open');
  closeBtn.onclick = () => chatWin.classList.remove('open');

  form.onsubmit = async (e) => {
    e.preventDefault();
    const input = form.elements.question;
    const question = input.value.trim();
    if (!question) return;

    msgs.insertAdjacentHTML('beforeend', `<div class="global-chatbot-message user"><strong>You</strong><p>${esc(question)}</p></div><div class="global-chatbot-message assistant chat-loading"><strong>Autonomous AI Advisor</strong><p>⚡ Executing academic reasoning...</p></div>`);
    msgs.scrollTop = msgs.scrollHeight;
    input.value = '';
    input.disabled = true;
    form.querySelector('button').disabled = true;

    try {
      const result = await api('/api/chat', { method: 'POST', body: JSON.stringify({ student_id: student.id, question }) });
      const citations = Array.isArray(result.citations) ? result.citations : [];
      const toolBadge = result.tool_executed ? `<span class="badge good" style="font-size:10px;margin-bottom:6px;display:inline-block;">⚡ Tool: ${esc(result.tool_executed)}</span>` : '';
      let replyHtml = esc(result.reply || 'I could not generate an answer.')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
      const loading = msgs.querySelector('.chat-loading:last-child');
      if (loading) {
        loading.outerHTML = `<div class="global-chatbot-message assistant"><strong>Autonomous AI Advisor</strong>${toolBadge}<div class="reply-text">${replyHtml}</div>${citations.length ? `<div class="chat-citations">${citations.map(c => `<span class="badge">${esc(typeof c === 'string' ? c : (c.reference || c.content || 'Source'))}</span>`).join('')}</div>` : ''}</div>`;
      }
    } catch (error) {
      const loading = msgs.querySelector('.chat-loading:last-child');
      if (loading) loading.outerHTML = `<div class="global-chatbot-message assistant"><strong>Autonomous AI Advisor</strong><p>${esc(error.message)}</p></div>`;
    } finally {
      input.disabled = false;
      form.querySelector('button').disabled = false;
      input.focus();
      msgs.scrollTop = msgs.scrollHeight;
    }
  };

  form.elements.question.onkeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  };
}
