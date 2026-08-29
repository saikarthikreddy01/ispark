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

function formatAgentMarkdown(text) {
  let formatted = esc(text || '');
  // Bold
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Italic
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // Code tags
  formatted = formatted.replace(/`([^`]+)`/g, '<code class="code">$1</code>');
  // Line breaks
  formatted = formatted.replace(/\n/g, '<br>');
  return formatted;
}

function citationLabel(citation) {
  if (typeof citation === 'string') return citation;
  if (!citation || typeof citation !== 'object') return 'Academic source';
  const reference = citation.reference || citation.title || citation.content || 'Academic source';
  const status = citation.source_status ? ` · ${citation.source_status}` : '';
  return `${reference}${status}`;
}

function renderAgentTrace(trace) {
  if (!Array.isArray(trace) || !trace.length) return '';
  return `<details class="agent-trace"><summary>View agent execution trace <span>${esc(trace.length)} steps</span></summary><ol>${trace.map(item => `<li><span class="agent-trace-status ${item.status === 'ok' ? 'good' : ''}"></span><div><strong>${esc(item.agent || 'Advisor agent')}</strong><p>${esc(item.action || 'Completed academic reasoning')}</p></div></li>`).join('')}</ol></details>`;
}

function renderAdvisorEvidence(result) {
  const details = Array.isArray(result.citation_details) && result.citation_details.length
    ? result.citation_details
    : (Array.isArray(result.citations) ? result.citations : []);
  const verification = result.verification || {};
  const conflicts = Array.isArray(result.conflicts) ? result.conflicts : [];
  const decision = verification.decision || (result.query_type === 'out_of_scope' ? 'OUT_OF_SCOPE' : 'ADVISORY_RESULT');
  const decisionTone = ['VERIFIED', 'VALID', 'ELIGIBLE'].some(word => String(decision).includes(word)) ? 'good' : (String(decision).includes('REVIEW') ? 'warn' : '');
  const meta = `<div class="advisor-result-meta"><span class="badge">${esc(result.query_type || 'general')}</span><span class="badge ${decisionTone}">${esc(decision)}</span><span class="badge">${esc((result.agent_trace || []).length)} agent steps</span></div>`;
  const conflictHtml = conflicts.length ? `<div class="advisor-findings"><strong>Detected academic signals</strong>${conflicts.slice(0, 5).map(item => `<p><span>${esc(item.type || 'Finding')}</span>${esc(item.message || item.detail || item.course_id || 'Review required')}</p>`).join('')}</div>` : '';
  const citationsHtml = details.length ? `<div class="chat-citations"><span>Verified evidence</span>${details.map(citation => `<span class="badge">${esc(citationLabel(citation))}</span>`).join('')}</div>` : '<div class="chat-citations evidence-empty"><span>No external policy citation was required for this response.</span></div>';
  const facultyHtml = result.needs_faculty_approval ? '<div class="notice advisor-faculty-note">This recommendation requires faculty review. The advisor prepared an evidence packet but did not approve the exception.</div>' : '';
  const pathwayLink = result.query_type === 'pathway' ? '<a class="advisor-follow-link" href="pathway.html">Open the interactive degree pathway <span aria-hidden="true">&rarr;</span></a>' : '';
  return `${meta}${conflictHtml}${facultyHtml}${citationsHtml}${renderAgentTrace(result.agent_trace)}${pathwayLink}`;
}

async function advisor(student) {
  const form = document.querySelector('[data-form]');
  const out = document.querySelector('[data-output]');
  const quickChips = document.querySelectorAll('[data-quick-actions] .quick-chip');
  const status = document.querySelector('[data-agent-status]');
  const context = document.querySelector('[data-advisor-context]');

  if (context) {
    context.innerHTML = `<div><span>Student</span><strong>${esc(student?.id || 'Unknown')}</strong></div><div><span>Current term</span><strong>${esc(student?.current_semester || 'Not set')}</strong></div><div><span>GPA</span><strong>${esc(student?.gpa ?? '—')} / ${esc(student?.gpa_scale || 10)}</strong></div><div><span>Completed</span><strong>${esc(student?.completed?.length || 0)} subjects</strong></div>`;
  }

  if (quickChips.length && form) {
    quickChips.forEach(chip => {
      chip.onclick = () => {
        const prompt = chip.getAttribute('data-prompt');
        if (prompt && form.elements.question) {
          form.elements.question.value = prompt;
          if (form.requestSubmit) form.requestSubmit();
          else form.dispatchEvent(new Event('submit'));
        }
      };
    });
  }

  if (form) {
    form.onsubmit = async event => {
      event.preventDefault();
      const input = form.elements.question;
      const question = input.value.trim();
      if (!question) return;
      const studentId = student?.id || '241FA04077';
      out.insertAdjacentHTML('beforeend', `<article class="chat-message user"><strong>You</strong><p>${esc(question)}</p></article><article class="chat-message assistant chat-loading"><strong>Academic AI Advisor</strong><p>Routing the request, retrieving graph evidence, and verifying constraints&hellip;</p></article>`);
      out.scrollTop = out.scrollHeight;
      input.value = '';
      input.disabled = true;
      form.querySelector('button').disabled = true;
      if (status) status.textContent = 'Agents working…';
      try {
        const result = await api('/api/chat', { method:'POST', body:JSON.stringify({ student_id:studentId, question }) });
        const loading = out.querySelector('.chat-loading:last-child');
        if (loading) {
          loading.outerHTML = `<article class="chat-message assistant advisor-result"><strong>Academic AI Advisor</strong><div class="agent-reply-content">${formatAgentMarkdown(result.reply || 'I could not generate an answer. Please try again.')}</div>${renderAdvisorEvidence(result)}</article>`;
        }
        if (status) status.textContent = result.needs_faculty_approval ? 'Faculty review required' : 'Answer verified';
      } catch (error) {
        const loading = out.querySelector('.chat-loading:last-child');
        if (loading) loading.outerHTML = `<article class="chat-message assistant advisor-error"><strong>Academic AI Advisor</strong><p>${esc(error.message)}</p><small>Check that the FastAPI server is running, then try again.</small></article>`;
        if (status) status.textContent = 'Unable to complete request';
      } finally {
        input.disabled = false;
        form.querySelector('button').disabled = false;
        input.focus();
        out.scrollTop = out.scrollHeight;
      }
    };

    form.elements.question.onkeydown = event => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (form.requestSubmit) form.requestSubmit();
      }
    };
  }
}

async function pathway(student) {
  const studentId = student?.id || '241FA04077';
  const form = document.querySelector('[data-pathway-form]');
  const summaryNode = document.querySelector('[data-summary]');
  const out = document.querySelector('[data-output]');
  const planStatus = document.querySelector('[data-plan-status]');

  if (form?.elements.target_graduation) form.elements.target_graduation.value = student?.expected_grad || 'May 2028';

  async function generatePlan() {
    const startSemester = form?.elements.start_semester?.value || 'AUTO';
    const electiveTrack = form?.elements.elective_track?.value || 'GENERAL';
    const pacingStrategy = form?.elements.pacing_strategy?.value || 'BALANCED';
    const maxCredits = Number(form?.elements.max_credits?.value || 16);
    const targetGraduation = form?.elements.target_graduation?.value.trim() || student?.expected_grad || 'May 2028';
    const submit = form?.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;
    if (out) out.innerHTML = '<div class="empty pathway-loading">Building the semester-aware, prerequisite-safe degree pathway&hellip;</div>';
    if (planStatus) planStatus.innerHTML = '';

    try {
      const data = await api('/api/pathway/generate', {
        method: 'POST',
        body: JSON.stringify({
          student_id: studentId,
          max_credits_per_semester: maxCredits,
          target_graduation: targetGraduation,
          start_semester: startSemester,
          elective_track: electiveTrack,
          pacing_strategy: pacingStrategy
        })
      });

      const progress = Number(data.degree_progress_percent || 0);
      const catBreakdown = Array.isArray(data.category_breakdown) ? data.category_breakdown : [];
      const workload = data.workload_overview || {};

      if (summaryNode) {
        summaryNode.innerHTML = `
          <div class="grid grid-3 pathway-metrics">
            <div class="metric">
              <strong>${esc(progress)}%</strong>
              <span>degree completion (${esc(data.completed_credits || 0)}/${esc(data.degree_credits_required || 160)} CR)</span>
            </div>
            <div class="metric">
              <strong>${esc(data.total_planned_credits || 0)} CR</strong>
              <span>planned across ${esc(data.total_semesters || 0)} terms (~${esc(data.average_credits_per_term || 0)} CR/term)</span>
            </div>
            <div class="metric">
              <strong>${esc(data.timeline_feasibility === 'ON_TRACK' ? '🎯 On Track' : data.timeline_feasibility === 'ACCELERATED' ? '⚡ Fast-Track' : '📋 Extension Review')}</strong>
              <span>graduation timeline status (Target: ${esc(data.target_graduation)})</span>
            </div>
          </div>
          <div class="degree-progress"><span style="width:${Math.min(100, Math.max(0, progress))}%"></span></div>
          <p class="pathway-credit-label">${esc(data.completed_credits || 0)} of ${esc(data.degree_credits_required || 160)} required credits completed &middot; projected ${esc(data.projected_credits || 0)} credits &middot; ${esc(workload.theory_practical_ratio || '')} &middot; ${esc(workload.bottlenecks_cleared_count || 0)} key gateway courses scheduled</p>

          ${catBreakdown.length ? `
            <div class="panel pathway-categories-panel">
              <header class="pathway-categories-head">
                <div>
                  <span class="eyebrow">Degree Requirements Audit</span>
                  <h3 style="margin: 2px 0 0; font-size: 16px;">Curriculum Category Fulfillment</h3>
                </div>
                <span class="badge good">${catBreakdown.filter(c => c.status === 'Fulfilled').length} of ${catBreakdown.length} Categories Satisfied</span>
              </header>
              <div class="pathway-category-grid">
                ${catBreakdown.map(cat => `
                  <div class="pathway-category-card">
                    <div class="pathway-category-meta">
                      <strong>${esc(cat.category_name)}</strong>
                      <span class="badge ${cat.status === 'Fulfilled' ? 'good' : 'muted'}">${esc(cat.status)}</span>
                    </div>
                    <div class="pathway-mini-progress"><span style="width:${Math.min(100, Math.max(0, cat.fulfillment_percent))}%"></span></div>
                    <div class="pathway-category-sub">
                      <span>${esc(cat.total_credits)} / ${esc(cat.required_credits)} CR (${esc(cat.fulfillment_percent)}%)</span>
                      <small>${esc(cat.completed_credits)} completed + ${esc(cat.planned_credits)} planned</small>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}
        `;
      }

      const unscheduled = Array.isArray(data.unscheduled_courses) ? data.unscheduled_courses : [];
      const constraints = Array.isArray(data.constraints_checked) ? data.constraints_checked : [];
      if (planStatus) {
        planStatus.innerHTML = `
          <div class="notice ${data.success ? 'good' : ''}">
            <strong>${data.success ? '✓ Verified Candidate Academic Pathway' : 'Faculty or Advisor Review Required'}</strong>
            <span>Active Sequence: Starting ${esc(data.start_semester)} &middot; Target ${esc(data.target_graduation)} &middot; ${esc(maxCredits)}-CR Term Limit &middot; Track: ${esc(data.elective_track || 'General')}</span>
            <div class="constraint-tags">${constraints.map(item => `<span>${esc(item)}</span>`).join('')}</div>
            ${unscheduled.length ? `<p><strong>Unscheduled:</strong> ${unscheduled.map(esc).join(', ')}</p>` : '<p>All required and selected catalog courses for this graduation pathway were successfully sequenced.</p>'}
          </div>
        `;
      }

      const terms = Array.isArray(data.pathway) ? data.pathway : [];
      if (out) {
        out.innerHTML = terms.length ? `
          <div class="pathway-timeline">
            ${terms.map((term, index) => `
              <article class="panel pathway-term">
                <div class="pathway-term-index">
                  <span>${String(index + 1).padStart(2, '0')}</span>
                  <i></i>
                </div>
                <div class="pathway-term-body">
                  <header>
                    <div>
                      <span class="eyebrow">${esc(term.academic_term || term.name)} &bull; ${esc(term.name)}</span>
                      <h3>${esc(term.total_credits)} credits</h3>
                    </div>
                    <div class="pathway-term-badges">
                      <span class="chip-metric">${esc(term.theory_credits || 0)} CR Theory</span>
                      <span class="chip-metric">${esc(term.practical_credits || 0)} CR Lab</span>
                      <span class="chip-metric diff-chip">Diff: ${esc(term.difficulty_score || '2.5')}/4.0</span>
                      <span class="badge ${term.workload_intensity === 'Intensive' ? 'danger' : term.workload_intensity === 'Light' ? 'muted' : 'good'}">${esc(term.workload_intensity || 'Balanced')}</span>
                    </div>
                  </header>
                  <div class="pathway-course-list">
                    ${(term.courses || []).map(course => `
                      <div class="pathway-course ${course.is_track_match ? 'track-matched' : ''}">
                        <div>
                          <div class="pathway-course-top">
                            <span class="code">${esc(course.id)}</span>
                            <span class="cat-tag">${esc(course.category || 'Core')}</span>
                            ${course.is_track_match ? '<span class="track-tag">Track Focus</span>' : ''}
                            ${course.is_bottleneck ? '<span class="bottleneck-tag">Gateway Course</span>' : ''}
                          </div>
                          <strong>${esc(course.name)}</strong>
                          <small class="ltpc-info">${esc(course.ltpc ? `L-T-P-C: ${course.ltpc}` : `${course.credits} Credits`)} &middot; ${coursePrereqs(course).length ? `After: ${coursePrereqs(course).map(esc).join(', ')}` : 'No blocking prerequisite'}</small>
                        </div>
                        <span class="cr-badge">${esc(course.credits || 0)} CR</span>
                      </div>
                    `).join('') || '<div class="empty">No eligible courses in this term.</div>'}
                  </div>
                </div>
              </article>
            `).join('')}
          </div>
        ` : '<div class="notice">No pathway could be generated. Review the unscheduled courses and prerequisite data.</div>';
      }
    } catch (error) {
      if (out) out.innerHTML = `<div class="notice">${esc(error.message)}</div>`;
      if (planStatus) planStatus.innerHTML = '<div class="notice">The pathway could not be generated. Confirm that the FastAPI server and student record are available.</div>';
    } finally {
      if (submit) submit.disabled = false;
    }
  }

  if (form) form.onsubmit = event => { event.preventDefault(); generatePlan(); };
  await generatePlan();
}

async function conflicts(student) {
  const courses = await api('/api/courses');
  const courseAccordion = document.querySelector('[data-course-accordion]');
  
  if (courseAccordion) {
    const sems = {};
    courses.forEach(course => {
      const s = course.sem || 0;
      if (!sems[s]) sems[s] = [];
      sems[s].push(course);
    });
    
    let html = '';
    const years = [
      { name: "First Year", sems: [1, 2] },
      { name: "Second Year", sems: [3, 4] },
      { name: "Third Year", sems: [5, 6] },
      { name: "Fourth Year", sems: [7, 8] }
    ];
    
    years.forEach(year => {
      let yearHtml = '';
      year.sems.forEach(s => {
        if (sems[s] && sems[s].length > 0) {
          const semCourses = sems[s].map(c => `
            <label class="accordion-item">
              <input type="checkbox" name="courses" value="${esc(c.id)}">
              <span class="code">${esc(c.id)}</span> ${esc(c.name)}
            </label>
          `).join('');
          yearHtml += `
            <details class="accordion-sem">
              <summary>Semester ${s}</summary>
              <div class="accordion-content">
                ${semCourses}
              </div>
            </details>
          `;
        }
      });
      if (yearHtml) {
        html += `
          <details class="accordion-year">
            <summary>${year.name}</summary>
            <div class="accordion-content">
              ${yearHtml}
            </div>
          </details>
        `;
      }
    });
    
    courseAccordion.innerHTML = html || '<div class="empty">No courses found.</div>';
  }

  const form = document.querySelector('[data-form]');
  if (form) {
    form.onsubmit = async event => {
      event.preventDefault();
      const ids = [...document.querySelectorAll('[data-course-accordion] input:checked')].map(cb => cb.value);
      const studentId = student?.id || '241FA04077';
      const semester = document.querySelector('[data-semester]')?.value || 'SEM 1';
      
      const out = document.querySelector('[data-output]');
      if (out) out.innerHTML = `<div class="empty">Running formal verification...</div>`;
      
      const result = await api('/api/audit/verify', { method:'POST', body:JSON.stringify({ student_id:studentId, selected_courses:ids, semester }) });
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
    out.innerHTML = `<div class="data-list">${visible.map(item => `<div class="panel"><div class="data-row"><strong>${esc(item.petition_type)}</strong><span class="badge ${item.status === 'PENDING' ? 'warn' : ''}">${esc(item.status)}</span></div><p>${esc(item.justification)}</p><span class="muted">Automated audit: ${item.automated_audit_eligible ? 'eligible' : 'needs review'}</span>${(item.status === 'PENDING' && !student?.id) ? `<div style="display:flex;gap:8px;margin-top:14px"><button class="btn btn-primary" onclick="reviewPetition('${esc(item.petition_id)}','APPROVED')">Approve</button><button class="btn" onclick="reviewPetition('${esc(item.petition_id)}','REJECTED')">Reject</button></div>` : ''}</div>`).join('') || '<div class="empty">No petitions submitted yet.</div>'}</div>`;
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
  const normalizedDecision = String(decision || '').toUpperCase();
  if (!['APPROVED', 'REJECTED'].includes(normalizedDecision)) {
    toast('Choose Approve or Reject.');
    return;
  }

  try {
    const data = await api(`/api/petitions/${encodeURIComponent(petitionId)}/review`, {
      method:'POST',
      body:JSON.stringify({
        decision: normalizedDecision,
        reviewer:'Faculty reviewer',
        comments:`${normalizedDecision.toLowerCase()} after formal constraint review.`
      })
    });
    toast(data.message);
    const activeSession = await currentStudent();
    await governance(activeSession);
  } catch (error) {
    toast(`Faculty review failed: ${error.message}`);
  }
}

window.applySub = applySub;
window.reviewPetition = reviewPetition;

document.addEventListener('DOMContentLoaded', boot);
