const page = document.body.dataset.page;

async function boot() {
  const student = await initShell(page);
  if (!student) return;
  try {
    if (page === 'curriculum') await curriculum(student);
    if (page === 'home') await home(student);
    if (page === 'graph') await graph(student);
    if (page === 'retrieval') await retrieval();
    if (page === 'advisor') await advisor(student);
    if (page === 'pathway') await pathway(student);
    if (page === 'conflicts') await conflicts(student);
    if (page === 'risk') await risk(student);
    if (page === 'substitutions') await substitutions(student);
    if (page === 'governance') await governance(student);
  } catch (error) {
    const out = document.querySelector('[data-output]');
    if (out) out.innerHTML = `<div class="notice">${esc(error.message)}</div>`;
  }
}

async function home(student) {
  const [curriculumData, courses] = await Promise.all([api('/api/curriculum'), api('/api/courses')]);
  const completed = new Set(student?.completed || []);
  const requiredCredits = Number(curriculumData.total_credits_required || 160);
  const completedCredits = courses.filter(course => completed.has(course.id)).reduce((total, course) => total + Number(course.credits || 0), 0);
  const progress = requiredCredits ? Math.min(100, Math.round((completedCredits / requiredCredits) * 100)) : 0;
  const remaining = Math.max(0, requiredCredits - completedCredits);
  const nextCourses = courses.filter(course => !completed.has(course.id) && coursePrereqs(course).every(prereq => completed.has(prereq))).slice(0, 3);
  
  const nameNode = document.querySelector('[data-student-name]');
  if (nameNode) nameNode.textContent = (student?.name || '').split(' ')[0] || 'student';
  
  const summaryNode = document.querySelector('[data-summary]');
  if (summaryNode) summaryNode.innerHTML = `<div class="metric"><strong>${esc(progress)}%</strong><span>degree progress</span></div><div class="metric"><strong>${esc(completed.size)}</strong><span>courses completed</span></div><div class="metric"><strong>${esc(student?.gpa || '3.82')}</strong><span>current GPA</span></div><div class="metric"><strong>${esc(student?.expected_grad || 'May 2028')}</strong><span>target graduation</span></div>`;
  
  const bar = document.querySelector('[data-progress-bar]');
  if (bar) bar.style.width = `${progress}%`;
  
  const progLabel = document.querySelector('[data-progress-label]');
  if (progLabel) progLabel.textContent = `${completedCredits} of ${requiredCredits} credits completed`;
  
  const credLabel = document.querySelector('[data-credits-label]');
  if (credLabel) credLabel.textContent = `${remaining} credits remaining`;
  
  const standingNode = document.querySelector('[data-standing]');
  if (standingNode) standingNode.textContent = student?.standing || 'Good Standing';
  
  const noteNode = document.querySelector('[data-progress-note]');
  if (noteNode) noteNode.textContent = nextCourses.length ? `Next available: ${nextCourses.map(course => course.id).join(', ')}` : 'Your academic record is up to date.';
}

async function curriculum(student) {
  const data = await api('/api/curriculum');
  const summaryNode = document.querySelector('[data-summary]');
  if (summaryNode) summaryNode.innerHTML = `<div class="grid grid-3"><div class="metric"><strong>${esc(data.total_credits_required)}</strong><span>credits required</span></div><div class="metric"><strong>${esc(data.semesters.length)}</strong><span>planned semesters</span></div><div class="metric"><strong>${esc(student?.completed?.length || 0)}</strong><span>courses completed</span></div></div>`;
  
  const courses = (data.semesters || []).flatMap(semester => (semester.courses || []).map(course => ({ ...course, sem: semester.semester })));
  const render = list => {
    const out = document.querySelector('[data-output]');
    if (out) out.innerHTML = `<div class="data-list">${list.map(course => courseRow(course, student)).join('')}</div>`;
  };
  render(courses);
  
  const searchInput = document.querySelector('[data-search]');
  if (searchInput) {
    searchInput.oninput = event => render(courses.filter(course => `${course.id} ${course.name}`.toLowerCase().includes(event.target.value.toLowerCase())));
  }
}

async function graph(student) {
  const courses = await api('/api/courses');
  const counts = {}; courses.forEach(course => coursePrereqs(course).forEach(prereq => counts[prereq] = (counts[prereq] || 0) + 1));
  const sorted = courses.slice().sort((a,b) => (counts[b.id] || 0) - (counts[a.id] || 0));
  
  const out = document.querySelector('[data-output]');
  if (out) {
    out.innerHTML = `<div class="notice good">${courses.length} courses mapped. Drag nodes, zoom, and select a course to inspect prerequisite edges and downstream impact.</div><div class="graph-stage"><canvas class="graph-depth" aria-hidden="true"></canvas><div class="graph-network" aria-label="Interactive course prerequisite graph"></div></div><div class="graph-key"><span><i class="graph-dot graph-dot-course"></i>Course</span><span><i class="graph-dot graph-dot-bottleneck"></i>High downstream impact</span><span><i class="graph-line"></i>Prerequisite</span></div><div class="data-list">${sorted.map(course => `<div class="data-row"><div><span class="code">${esc(course.id)}</span><strong> ${esc(course.name)}</strong><div class="muted">Prerequisites: ${coursePrereqs(course).map(esc).join(', ') || 'None'}</div></div><span class="badge ${counts[course.id] > 2 ? 'warn' : ''}">${counts[course.id] || 0} dependents</span></div>`).join('')}</div>`;
  }

  if (!window.vis || !window.THREE) return;
  const networkEl = document.querySelector('.graph-network');
  if (networkEl) {
    const nodes = new vis.DataSet(courses.map(course => ({
      id: course.id,
      label: `${course.id}\n${course.name || 'Course'}`,
      title: `${course.id}: ${course.name || 'Course'}\n${course.credits || 0} credits`,
      value: 12 + (counts[course.id] || 0) * 3,
      color: counts[course.id] > 2 ? { background: '#e9c382', border: '#b26d18' } : { background: '#8bd8c7', border: '#187c70' },
      font: { color: '#123b3b', face: 'Space Grotesk', size: 13, bold: true }
    })));
    const edges = new vis.DataSet(courses.flatMap(course => coursePrereqs(course).filter(prereq => courses.some(item => item.id === prereq)).map(prereq => ({
      from: prereq, to: course.id, arrows: 'to', color: { color: 'rgba(139,216,199,.62)', highlight: '#f4d39b' }, smooth: { type: 'cubicBezier' }
    }))));
    new vis.Network(networkEl, { nodes, edges }, {
      physics: { stabilization: { iterations: 180 }, barnesHut: { gravitationalConstant: -4200, springLength: 145, springConstant: .03 } },
      interaction: { hover: true, navigationButtons: true, keyboard: true },
      nodes: { shape: 'box', borderWidth: 2, margin: 10, widthConstraint: { maximum: 150 }, scaling: { min: 14, max: 34 } },
      edges: { width: 1.5, selectionWidth: 3 }
    });
  }

  const canvas = document.querySelector('.graph-depth');
  if (canvas) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, (canvas.clientWidth || 800) / (canvas.clientHeight || 500), .1, 100);
    camera.position.z = 8;
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(canvas.clientWidth || 800, canvas.clientHeight || 500, false);
    const points = new THREE.Points(new THREE.BufferGeometry().setFromPoints(Array.from({ length: 90 }, () => new THREE.Vector3((Math.random() - .5) * 13, (Math.random() - .5) * 7, (Math.random() - .5) * 4))), new THREE.PointsMaterial({ color: 0x9fe9d8, size: .035, transparent: true, opacity: .65 }));
    scene.add(points);
    const animate = () => { points.rotation.y += .0008; points.rotation.x += .0002; renderer.render(scene, camera); requestAnimationFrame(animate); };
    animate();
  }
}

async function retrieval() {
  const [data, courses] = await Promise.all([api('/api/policies'), api('/api/courses')]);
  const edges = courses.reduce((total, course) => total + coursePrereqs(course).length, 0);
  const graphContext = courses.filter(course => coursePrereqs(course).length > 0).slice(0, 6).map(course => `<div class="data-row"><div><span class="code">${esc(course.id)}</span><strong> ${esc(course.name)}</strong><div class="muted">${coursePrereqs(course).map(esc).join(', ')} → ${esc(course.id)}</div></div><span class="badge">Graph edge</span></div>`).join('');
  const graphCourses = courses.filter(course => coursePrereqs(course).length > 0).slice(0, 8);
  const graphNodes = graphCourses.map((course, index) => `<span class="rag-node rag-node-${index + 1}"><b>${esc(course.id)}</b><small>${esc((course.name || '').split(' ').slice(0, 2).join(' '))}</small></span>`).join('');
  const graphEdges = graphCourses.map((course, index) => coursePrereqs(course).slice(0, 2).map((prereq, edgeIndex) => `<i class="rag-edge rag-edge-${index + 1}-${edgeIndex + 1}"></i>`).join('')).join('');
  
  const out = document.querySelector('[data-output]');
  if (out) {
    out.innerHTML = `<div class="grid grid-3"><div class="metric"><strong>${esc(data.policies.length)}</strong><span>policy sources</span></div><div class="metric"><strong>${esc(courses.length)}</strong><span>course nodes</span></div><div class="metric"><strong>${esc(edges)}</strong><span>prerequisite edges</span></div></div><div class="notice good">Graph-RAG context combines policies.md, the C24 course catalog, and ${esc(edges)} prerequisite relationships. <a href="graph.html"><u>Open full knowledge graph</u> →</a></div><div class="panel rag-graph-panel"><div class="rag-graph-heading"><div><span class="eyebrow">Live graph context</span><h2>Prerequisite intelligence map</h2><p>Course relationships are traversed alongside policy sources before an advising answer is generated.</p></div><span class="badge">${graphCourses.length} active nodes</span></div><div class="rag-graph-3d"><div class="rag-grid"></div><div class="rag-ring rag-ring-a"></div><div class="rag-ring rag-ring-b"></div><div class="rag-core"><b>RAG</b><small>CONTEXT</small></div>${graphEdges}${graphNodes}</div><div class="rag-legend"><span><i class="legend-dot dot-core"></i>Retrieval core</span><span><i class="legend-dot dot-course"></i>Course node</span><span><i class="legend-line"></i>Prerequisite edge</span></div></div><div class="grid grid-2"><div class="panel"><h2>Policy retrieval</h2><div class="data-list">${data.policies.map(policy => `<article><span class="code">${esc(policy.section)}</span><h3>${esc(policy.title)}</h3><p>${esc(policy.summary)}</p><span class="muted">Authority: ${esc(policy.authority)}</span></article>`).join('')}</div></div><div class="panel"><h2>Graph context</h2><p>Representative prerequisite paths available to retrieval.</p><div class="data-list">${graphContext}</div></div></div>`;
  }
}

async function advisor(student) {
  const form = document.querySelector('[data-form]');
  if (form) {
    form.onsubmit = async event => {
      event.preventDefault();
      const question = new FormData(event.target).get('question');
      const studentId = student?.id || '241FA04077';
      const result = await api('/api/chat', { method:'POST', body:JSON.stringify({ student_id:studentId, question }) });
      const citations = Array.isArray(result.citations) ? result.citations : [];
      const out = document.querySelector('[data-output]');
      if (out) {
        out.innerHTML = `<article class="panel"><h3>Advisor response</h3><p>${esc(result.reply || '').replace(/\n/g, '<br>')}</p><div class="data-list"><strong>Sources used</strong>${citations.map(citation => `<span class="badge">${esc(citation)}</span>`).join('')}</div></article>`;
      }
    };
  }
}

async function pathway(student) {
  const studentId = student?.id || '241FA04077';
  const data = await api('/api/pathway/generate', { method:'POST', body:JSON.stringify({ student_id:studentId, max_credits_per_semester:16, target_graduation:student?.expected_grad || 'May 2028' }) });
  const summaryNode = document.querySelector('[data-summary]');
  if (summaryNode) summaryNode.innerHTML = `<div class="grid grid-3"><div class="metric"><strong>${esc(data.total_planned_credits)}</strong><span>planned credits</span></div><div class="metric"><strong>${esc(data.total_semesters)}</strong><span>terms generated</span></div><div class="metric"><strong>${esc(data.target_graduation)}</strong><span>target graduation</span></div></div>`;
  
  const out = document.querySelector('[data-output]');
  if (out) out.innerHTML = `<div class="grid grid-2">${(data.pathway || []).map(term => `<article class="panel"><span class="eyebrow">${esc(term.name)}</span><h3>${esc(term.total_credits)} credits · ${esc(term.status)}</h3><div class="data-list">${(term.courses || []).map(course => courseRow(course, student)).join('') || '<div class="empty">No eligible courses in this term.</div>'}</div></article>`).join('')}</div>`;
}

async function conflicts(student) {
  const courses = await api('/api/courses');
  const courseOptions = document.querySelector('[data-course-options]');
  if (courseOptions) {
    courseOptions.innerHTML = courses.map(course => `<option value="${esc(course.id)}">${esc(course.id)} · ${esc(course.name)}</option>`).join('');
  }
  const form = document.querySelector('[data-form]');
  if (form) {
    form.onsubmit = async event => {
      event.preventDefault();
      const ids = [...(document.querySelector('[data-course-options]')?.selectedOptions || [])].map(option => option.value);
      const studentId = student?.id || '241FA04077';
      const semester = document.querySelector('[data-semester]')?.value || 'FALL';
      const result = await api('/api/audit/verify', { method:'POST', body:JSON.stringify({ student_id:studentId, selected_courses:ids, semester }) });
      const out = document.querySelector('[data-output]');
      if (out) {
        out.innerHTML = `<div class="notice ${result.is_valid ? 'good' : ''}">${esc(result.summary)} · ${esc(result.total_credits)} credits</div><div class="data-list">${[...(result.issues || []), ...(result.warnings || [])].map(esc).map(item => `<div class="data-row">${item}</div>`).join('') || '<div class="empty">No conflicts detected.</div>'}</div>`;
      }
    };
  }
}

async function risk(student) {
  const studentId = student?.id || '241FA04077';
  const data = await api(`/api/bottlenecks/${encodeURIComponent(studentId)}`);
  const summaryNode = document.querySelector('[data-summary]');
  if (summaryNode) summaryNode.innerHTML = `<div class="grid grid-3"><div class="metric"><strong>${esc(data.graduation_risk_score)}%</strong><span>${esc(data.graduation_risk_level)} graduation risk</span></div><div class="metric"><strong>${esc(data.uncompleted_bottlenecks)}</strong><span>uncompleted bottlenecks</span></div><div class="metric"><strong>${esc(data.projected_delay_semesters)}</strong><span>projected delay terms</span></div></div>`;
  
  const out = document.querySelector('[data-output]');
  if (out) out.innerHTML = `<div class="data-list">${(data.bottlenecks || []).map(item => `<div class="data-row"><div><span class="code">${esc(item.course_id)}</span><strong> ${esc(item.name)}</strong><div class="muted">Blocks: ${(item.blocked_courses || []).map(esc).join(', ')}</div></div><span class="badge ${item.risk_factor === 'CRITICAL' ? 'danger' : 'warn'}">${esc(item.risk_factor)}</span></div>`).join('')}</div>`;
}

async function substitutions(student) {
  const courses = await api('/api/courses');
  const courseOptions = document.querySelector('[data-course-options]');
  if (courseOptions) {
    courseOptions.innerHTML = courses.map(course => `<option value="${esc(course.id)}">${esc(course.id)} · ${esc(course.name)}</option>`).join('');
  }
  const loadBtn = document.querySelector('[data-load]');
  if (loadBtn) {
    loadBtn.onclick = async () => {
      const id = document.querySelector('[data-course-options]')?.value;
      if (!id) return;
      const data = await api(`/api/substitutions/${encodeURIComponent(id)}`);
      const studentId = student?.id || '241FA04077';
      const out = document.querySelector('[data-output]');
      if (out) {
        out.innerHTML = (data.substitutions || []).length ? `<div class="data-list">${data.substitutions.map(item => `<div class="data-row"><div><span class="code">${esc(item.course_id)}</span> → <strong>${esc(item.equivalent_course_id)}</strong><div class="muted">${esc(item.notes || 'Approved course equivalency')}</div></div><button class="btn btn-primary" onclick="applySub('${esc(item.course_id)}','${esc(item.equivalent_course_id)}','${esc(studentId)}')">Apply</button></div>`).join('')}</div>` : '<div class="empty">No approved substitutions found.</div>';
      }
    };
  }
}

async function applySub(original, substitute, studentId) {
  const data = await api('/api/substitutions/apply', { method:'POST', body:JSON.stringify({ student_id:studentId, original_course_id:original, substitute_course_id:substitute }) });
  toast(data.message);
}

async function governance(student) {
  const petitions = await api('/api/petitions');
  const visible = student?.id ? petitions.filter(item => item.student_id === student.id) : petitions;
  const form = document.querySelector('[data-form]');
  if (!student?.id && form) form.style.display = 'none';
  
  const out = document.querySelector('[data-output]');
  if (out) {
    out.innerHTML = `<div class="data-list">${visible.map(item => `<div class="panel"><div class="data-row"><strong>${esc(item.petition_type)}</strong><span class="badge ${item.status === 'PENDING' ? 'warn' : ''}">${esc(item.status)}</span></div><p>${esc(item.justification)}</p><span class="muted">Automated audit: ${item.automated_audit_eligible ? 'eligible' : 'needs review'}</span>${item.status === 'PENDING' ? `<div style="display:flex;gap:8px;margin-top:14px"><button class="btn btn-primary" onclick="reviewPetition('${esc(item.petition_id)}','APPROVED')">Approve</button><button class="btn" onclick="reviewPetition('${esc(item.petition_id)}','REJECTED')">Reject</button></div>` : ''}</div>`).join('') || '<div class="empty">No petitions submitted yet.</div>'}</div>`;
  }
  
  if (form) {
    form.onsubmit = async event => {
      event.preventDefault();
      const fd = new FormData(event.target);
      const studentId = student?.id || '241FA04077';
      const data = await api('/api/petitions/submit', { method:'POST', body:JSON.stringify({ student_id:studentId, petition_type:fd.get('petition_type'), course_id:fd.get('course_id') || null, target_semester:fd.get('target_semester'), requested_credits:Number(fd.get('requested_credits') || 0), justification:fd.get('justification') }) });
      toast(data.message);
      event.target.reset();
      governance(student);
    };
  }
}

async function reviewPetition(petitionId, decision) {
  const data = await api(`/api/petitions/${encodeURIComponent(petitionId)}/review`, { method:'POST', body:JSON.stringify({ decision, reviewer:'Faculty reviewer', comments:`${decision.toLowerCase()} after formal constraint review.` }) });
  toast(data.message);
  const student = await currentStudent();
  governance(student);
}

window.applySub = applySub;
window.reviewPetition = reviewPetition;

document.addEventListener('DOMContentLoaded', boot);
