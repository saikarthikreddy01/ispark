const API = window.location.protocol === 'file:' ? 'http://127.0.0.1:8000' : window.location.origin;
let signingOut = false;
const AUTH_STORAGE_KEYS = [
  'academic_advisor_permanent_active_user_v3',
  'academic_advisor_faculty_session',
  'academic_advisor_cached_student'
];

function loginPageUrl() {
  return new URL('login.html', document.baseURI).href;
}

function hasActiveSession() {
  try {
    return Boolean(
      localStorage.getItem('academic_advisor_permanent_active_user_v3') ||
      localStorage.getItem('academic_advisor_faculty_session') === 'active'
    );
  } catch (error) {
    return false;
  }
}

function clearAuthStorage() {
  AUTH_STORAGE_KEYS.forEach(key => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });
}

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
  try {
    const s = await api(`/api/student/${encodeURIComponent(savedId)}`);
    if (s && s.id) {
      localStorage.setItem('academic_advisor_cached_student', JSON.stringify(s));
      return s;
    }
  } catch (err) {
    console.warn('API fetch student failed, checking cached student data:', err);
    try {
      const cached = localStorage.getItem('academic_advisor_cached_student');
      if (cached) return JSON.parse(cached);
    } catch {}
    return { id: savedId, name: 'Student (' + savedId + ')', major: 'Computer Science', completed: [] };
  }
  return null;
}

function isFacultySession() {
  const savedId = localStorage.getItem('academic_advisor_permanent_active_user_v3');
  if (savedId) {
    localStorage.removeItem('academic_advisor_faculty_session');
    return false;
  }
  return localStorage.getItem('academic_advisor_faculty_session') === 'active';
}

function signOut(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  if (signingOut) return;
  signingOut = true;

  try {
    clearAuthStorage();
  } catch (e) {
    console.warn('Storage clear error:', e);
  }

  try {
    fetch(API + '/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
      keepalive: true
    }).catch(function() {});
  } catch (e) {}

  // replace() prevents the authenticated page from remaining in browser history.
  window.location.replace(loginPageUrl());
}
window.signOut = signOut;

// Browsers may restore a protected page from the back-forward cache. Re-check
// storage whenever the page is shown and return signed-out users to login.
window.addEventListener('pageshow', function() {
  if (!hasActiveSession()) {
    window.location.replace(loginPageUrl());
  }
});

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
  const visibleItems = faculty ? items.filter(([, , key]) => key === 'governance') : items.filter(([, , key]) => key !== 'profile');
  return visibleItems.map(([href,label,key]) => `<a class="${key === active ? 'active' : ''}" href="${href}">${label}</a>`).join('');
}

async function initShell(active) {
  const student = await currentStudent();
  if (!student) { location.href = 'login.html'; return null; }
  const faculty = isFacultySession();
  if (faculty && active !== 'governance') { location.href = 'governance.html'; return null; }
  const appbar = document.querySelector('.appbar');
  if (appbar && !appbar.querySelector('.brand')) {
    appbar.insertAdjacentHTML('afterbegin', `<a class="brand" href="${faculty ? 'governance.html' : 'home.html'}"><span class="brand-mark">AA</span><span>Academic Advisor</span></a>`);
  }
  const navNode = document.querySelector('.nav');
  if (navNode) navNode.innerHTML = nav(active, faculty);
  const userbar = document.querySelector('.userbar');
  if (userbar) {
    const initial = (student.name || 'S').charAt(0).toUpperCase();
    const displayId = student.id || 'Faculty';
    const profileHref = faculty ? 'governance.html' : 'profile.html';

    // Use a real anchor so profile navigation works even if JavaScript event
    // delegation changes. Students go to profile; faculty remain in governance.
    const profileLink = document.createElement('a');
    profileLink.href = profileHref;
    profileLink.className = 'profile-icon-btn';
    profileLink.setAttribute('data-action', 'profile');
    profileLink.title = 'My Profile';
    profileLink.style.cssText = 'display:inline-flex;align-items:center;gap:8px;text-decoration:none;border:1px solid var(--line,#e2e8f0);border-radius:8px;padding:5px 12px;font-size:13px;color:inherit;background:transparent;cursor:pointer;position:relative;z-index:9999;pointer-events:auto;';

    const avatar = document.createElement('span');
    avatar.textContent = initial;
    avatar.style.cssText = 'width:26px;height:26px;border-radius:50%;background:#2563eb;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0;pointer-events:none;';

    const nameSpan = document.createElement('span');
    nameSpan.textContent = student.name || '';
    nameSpan.style.cssText = 'max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500;pointer-events:none;';

    const idSpan = document.createElement('span');
    idSpan.textContent = displayId;
    idSpan.style.cssText = 'font-family:monospace;color:#64748b;font-size:11px;pointer-events:none;';

    profileLink.appendChild(avatar);
    profileLink.appendChild(nameSpan);
    profileLink.appendChild(idSpan);

    // Build sign out button with attributes and handlers
    const signOutBtn = document.createElement('button');
    signOutBtn.className = 'btn';
    signOutBtn.type = 'button';
    signOutBtn.setAttribute('data-action', 'signout');
    signOutBtn.textContent = 'Sign out';
    signOutBtn.style.cssText = 'cursor:pointer;position:relative;z-index:9999;pointer-events:auto;';
    signOutBtn.addEventListener('click', signOut);

    // Clear and inject
    userbar.innerHTML = '';
    userbar.appendChild(profileLink);
    userbar.appendChild(signOutBtn);
  }
  if (!document.getElementById('global-chatbot-widget') && !faculty) {
    initGlobalChatbot(student);
  }
  return student;
}

// Global sign-out delegation is retained as a fallback. Profile navigation is
// handled by the anchor's href and must not be intercepted here.
document.addEventListener('click', function(e) {
  const target = e.target instanceof Element ? e.target : e.target?.parentElement;
  if (!target) return;
  // Sign Out click detection
  const signoutElem = target.closest('[data-action="signout"]') || (target.tagName === 'BUTTON' && target.textContent.trim() === 'Sign out');
  if (signoutElem) {
    signOut(e);
    return;
  }
}, true);

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
          <button type="button" class="global-chip" data-prompt="What are my graduation bottlenecks and delay risks?">🚨 Bottlenecks</button>
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
