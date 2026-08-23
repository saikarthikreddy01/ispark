const API = '';

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

function signOut() {
  localStorage.removeItem('academic_advisor_permanent_active_user_v3');
  localStorage.removeItem('academic_advisor_faculty_session');
  location.href = 'index.html';
}

function toast(message) {
  const node = document.getElementById('toast');
  if (node) {
    node.textContent = message;
    node.style.display = 'block';
    setTimeout(() => node.style.display = 'none', 2800);
  }
}

function nav(active) {
  const items = [
    ['home.html','Home','home'], ['curriculum.html','Curriculum','curriculum'], ['graph.html','Knowledge graph','graph'], ['retrieval.html','Graph-RAG','retrieval'], ['advisor.html','Advisor','advisor'],
    ['pathway.html','Degree pathway','pathway'], ['conflicts.html','Conflict audit','conflicts'], ['risk.html','Risk','risk'],
    ['substitutions.html','Substitutions','substitutions'], ['governance.html','Faculty review','governance']
  ];
  return items.map(([href,label,key]) => `<a class="${key === active ? 'active' : ''}" href="${href}">${label}</a>`).join('');
}

async function initShell(active) {
  const student = await currentStudent();
  if (!student) { location.href = 'index.html'; return null; }
  const appbar = document.querySelector('.appbar');
  if (appbar) {
    appbar.insertAdjacentHTML('afterbegin', `<a class="brand" href="home.html"><span class="brand-mark">AA</span><span>Academic Advisor</span></a>`);
  }
  const navNode = document.querySelector('.nav');
  if (navNode) navNode.innerHTML = nav(active);
  const userbar = document.querySelector('.userbar');
  if (userbar) {
    userbar.innerHTML = `<span class="user-chip">${esc(student.name)} · ${esc(student.id || 'Faculty')}</span><button class="btn" type="button" onclick="signOut()">Sign out</button>`;
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