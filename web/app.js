/* ==========================================================================
   PathFinder AI — Ultra-Clean Application Engine
   ========================================================================== */

// --- Comprehensive Academic Dataset ---
const APP_DATA = {
  students: [
    {
      id: "S1001",
      name: "Alice Johnson",
      major: "Computer Science",
      minor: "Mathematics",
      gpa: 3.65,
      completed_courses: ["CS101", "MATH101", "CS102", "MATH201", "PHYS101", "CS201", "CS250", "MATH202", "CS202", "ENG101", "PHIL101"],
      planned_courses: ["CS302", "CS303", "CS350", "CS401", "CS402", "CS499"],
      conflicts: ["CS301"],
      expected_graduation: "Spring 2026",
      standing: "Good Academic Standing",
      career_goal: "AI/ML Engineer"
    },
    {
      id: "S1002",
      name: "Bob Smith",
      major: "Computer Science",
      minor: "None",
      gpa: 2.45,
      completed_courses: ["CS101", "MATH101", "ENG101", "CS102", "PHIL101"],
      planned_courses: ["CS201", "CS202", "CS250", "MATH201"],
      conflicts: ["CS201", "MATH201"],
      expected_graduation: "Spring 2027",
      standing: "Academic Warning",
      career_goal: "Full-Stack Web Development"
    },
    {
      id: "S1003",
      name: "Charlie Brown",
      major: "Computer Science",
      minor: "Data Science",
      gpa: 3.82,
      completed_courses: ["CS101", "MATH101", "CS102", "MATH201", "CS201", "CS250", "CS301", "CS302", "CS303", "CS350", "CS401", "CS402"],
      planned_courses: ["CS499"],
      conflicts: [],
      expected_graduation: "Fall 2025",
      standing: "Dean's Honor List",
      career_goal: "Cloud & Distributed Systems"
    }
  ],

  courses: [
    { id: "CS101", name: "Intro to Computer Science", credits: 3, prereqs: [], category: "Core", semester_order: 1, desc: "Foundations of programming and algorithmic problem solving." },
    { id: "MATH101", name: "Calculus I", credits: 4, prereqs: [], category: "Math", semester_order: 1, desc: "Limits, derivatives, and integral calculus." },
    { id: "ENG101", name: "College Writing", credits: 3, prereqs: [], category: "GenEd", semester_order: 1, desc: "Analytical reading, rhetoric, and academic composition." },
    { id: "CS102", name: "Programming Fundamentals", credits: 3, prereqs: ["CS101"], category: "Core", semester_order: 2, desc: "Object-oriented structures, memory management, and debugging." },
    { id: "MATH201", name: "Discrete Mathematics", credits: 3, prereqs: ["MATH101"], category: "Math", semester_order: 2, desc: "Propositional logic, graph theory, and combinatorics." },
    { id: "PHYS101", name: "General Physics I", credits: 4, prereqs: ["MATH101"], category: "GenEd", semester_order: 2, desc: "Classical mechanics, kinetics, and energy." },
    { id: "CS201", name: "Data Structures", credits: 3, prereqs: ["CS102"], category: "Core", semester_order: 3, desc: "Linked lists, binary trees, hash tables, and algorithm efficiency." },
    { id: "CS250", name: "Computer Organization", credits: 3, prereqs: ["CS102"], category: "Core", semester_order: 3, desc: "CPU architecture, assembly language, and hardware interfacing." },
    { id: "MATH202", name: "Linear Algebra", credits: 4, prereqs: ["MATH101"], category: "Math", semester_order: 3, desc: "Matrices, vector spaces, and eigenvalues." },
    { id: "CS202", name: "Object-Oriented Programming", credits: 3, prereqs: ["CS102"], category: "Core", semester_order: 4, desc: "Advanced design patterns and architecture in Java." },
    { id: "PHIL101", name: "Ethics in Technology", credits: 3, prereqs: [], category: "GenEd", semester_order: 4, desc: "Moral implications of AI, privacy, and digital governance." },
    { id: "CS301", name: "Algorithms", credits: 3, prereqs: ["CS201", "MATH201"], category: "Core", semester_order: 5, desc: "Divide-and-conquer, dynamic programming, and complexity analysis." },
    { id: "CS302", name: "Operating Systems", credits: 3, prereqs: ["CS201", "CS250"], category: "Core", semester_order: 5, desc: "Concurrency, virtual memory, scheduling, and file systems." },
    { id: "CS303", name: "Database Systems", credits: 3, prereqs: ["CS201"], category: "Core", semester_order: 6, desc: "Relational modeling, SQL optimization, and ACID properties." },
    { id: "CS350", name: "Web App Architecture", credits: 3, prereqs: ["CS201"], category: "Elective", semester_order: 6, desc: "Cloud deployment, REST services, and frontend engineering." },
    { id: "CS401", name: "Software Engineering", credits: 3, prereqs: ["CS202", "CS301"], category: "Core", semester_order: 7, desc: "Agile workflows, automated testing, and CI/CD pipelines." },
    { id: "CS402", name: "Machine Learning", credits: 3, prereqs: ["CS301", "MATH202"], category: "Elective", semester_order: 7, desc: "Supervised and unsupervised models, neural networks." },
    { id: "CS499", name: "Senior Capstone Project", credits: 3, prereqs: ["CS401"], category: "Core", semester_order: 8, desc: "Culminating team software development and presentation." }
  ],

  equivalencies: {
    "CS301": ["CS305 (Applied Algorithm Design)", "MATH350 (Combinatorial Optimization)"],
    "CS350": ["CS355 (Mobile App Dev)", "SE301 (Software Quality & Testing)"],
    "MATH202": ["MATH205 (Applied Linear Algebra)"],
    "PHYS101": ["CHEM101 (General Chemistry I)"]
  }
};

// --- Application State ---
let state = {
  currentStudent: APP_DATA.students[0],
  currentView: "pathway",
  network: null
};

// --- Lifecycle Init ---
document.addEventListener("DOMContentLoaded", () => {
  initStudentPicker();
  renderApp();
  initChatInput();
  initAuditorOptions();
});

// --- Tab View Controller ---
function setMainView(viewName) {
  state.currentView = viewName;
  
  document.querySelectorAll(".nav-tab").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".view-section").forEach(sec => sec.style.display = "none");

  const activeBtn = document.getElementById(`tab-btn-${viewName}`);
  const activeSec = document.getElementById(`section-${viewName}`);
  
  if (activeBtn) activeBtn.classList.add("active");
  if (activeSec) activeSec.style.display = "block";

  if (viewName === "graph") {
    setTimeout(renderPrereqGraph, 100);
  }
}

// --- Student Picker ---
function initStudentPicker() {
  const select = document.getElementById("student-picker");
  if (!select) return;
  select.innerHTML = "";

  APP_DATA.students.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = `${s.name} (${s.major})`;
    select.appendChild(opt);
  });

  select.addEventListener("change", (e) => {
    const found = APP_DATA.students.find(s => s.id === e.target.value);
    if (found) {
      state.currentStudent = found;
      renderApp();
    }
  });
}

// --- Master Render ---
function renderApp() {
  const s = state.currentStudent;
  const completedSet = new Set(s.completed_courses);
  const earnedCredits = APP_DATA.courses.filter(c => completedSet.has(c.id)).reduce((sum, c) => sum + c.credits, 0);
  const pct = Math.min(Math.round((earnedCredits / 120) * 100), 100);
  const remainingCredits = Math.max(0, 120 - earnedCredits);

  // Update Header & KPIs
  document.getElementById("student-heading").textContent = s.name;
  document.getElementById("student-subheading").textContent = `Major: ${s.major} · Minor: ${s.minor} · Expected Graduation: ${s.expected_graduation}`;
  
  const statusBadge = document.getElementById("student-status-badge");
  statusBadge.textContent = `● ${s.standing}`;
  statusBadge.className = `stat-badge ${s.gpa >= 3.0 ? "badge-success" : (s.gpa >= 2.0 ? "badge-warning" : "badge-danger")}`;

  document.getElementById("kpi-credits").innerHTML = `${earnedCredits} <span style="font-size: 1rem; color: var(--text-muted);">/ 120 cr</span>`;
  document.getElementById("kpi-credits-pct").textContent = `${pct}% Progress`;
  document.getElementById("kpi-gpa").textContent = s.gpa.toFixed(2);
  document.getElementById("kpi-semesters").textContent = `${Math.ceil(remainingCredits / 15)} Terms`;
  document.getElementById("kpi-conflicts").textContent = `${s.conflicts.length} Course${s.conflicts.length === 1 ? '' : 's'}`;

  renderKanban();
  if (state.currentView === "graph") {
    renderPrereqGraph();
  }
}

// --- 1. Render Clean Kanban ---
function renderKanban() {
  const container = document.getElementById("kanban-feed");
  if (!container) return;
  container.innerHTML = "";

  const s = state.currentStudent;
  const completedSet = new Set(s.completed_courses);
  const conflictSet = new Set(s.conflicts);

  const semesters = [
    "Semester 1 (Fall)", "Semester 2 (Spring)",
    "Semester 3 (Fall)", "Semester 4 (Spring)",
    "Semester 5 (Fall)", "Semester 6 (Spring)",
    "Semester 7 (Fall)", "Semester 8 (Spring)"
  ];

  for (let sem = 1; sem <= 8; sem++) {
    const col = document.createElement("div");
    col.className = "kanban-column";

    const semCourses = APP_DATA.courses.filter(c => c.semester_order === sem);
    const credits = semCourses.reduce((sum, c) => sum + c.credits, 0);

    let cardsHtml = "";
    semCourses.forEach(c => {
      let statusClass = "planned";
      let statusText = "Planned";
      let badgeStyle = "background: rgba(37, 99, 235, 0.15); color: #93c5fd;";

      if (completedSet.has(c.id)) {
        statusClass = "passed";
        statusText = "Passed";
        badgeStyle = "background: rgba(16, 185, 129, 0.15); color: #34d399;";
      } else if (conflictSet.has(c.id)) {
        statusClass = "at-risk";
        statusText = "At-Risk";
        badgeStyle = "background: rgba(239, 68, 68, 0.15); color: #f87171;";
      }

      cardsHtml += `
        <div class="course-card ${statusClass}" onclick="openModal('${c.id}')">
          <div class="card-top">
            <span class="card-code">${c.id}</span>
            <span class="card-status" style="${badgeStyle}">${statusText}</span>
          </div>
          <div class="card-name">${c.name}</div>
          <div class="card-meta">${c.credits} Credits · ${c.category}</div>
        </div>
      `;
    });

    col.innerHTML = `
      <div class="column-header">
        <span class="column-title">${semesters[sem - 1]}</span>
        <span class="column-badge">${credits} cr</span>
      </div>
      ${cardsHtml}
    `;

    container.appendChild(col);
  }
}

// --- 2. Render Knowledge Graph (Vis.js) ---
function renderPrereqGraph() {
  const container = document.getElementById("graph-canvas");
  if (!container) return;

  const s = state.currentStudent;
  const completedSet = new Set(s.completed_courses);
  const conflictSet = new Set(s.conflicts);

  const nodes = new vis.DataSet(
    APP_DATA.courses.map(c => {
      let bg = "#182234";
      let border = "#3b82f6";

      if (completedSet.has(c.id)) {
        bg = "#065f46";
        border = "#10b981";
      } else if (conflictSet.has(c.id)) {
        bg = "#7f1d1d";
        border = "#ef4444";
      }

      return {
        id: c.id,
        label: `${c.id}\n${c.name.substring(0, 16)}...`,
        shape: "box",
        margin: 10,
        color: { background: bg, border: border, highlight: { background: "#2563eb", border: "#60a5fa" } },
        font: { color: "#ffffff", face: "Inter", size: 12, bold: true }
      };
    })
  );

  const edges = [];
  APP_DATA.courses.forEach(c => {
    c.prereqs.forEach(p => {
      const isConflicted = conflictSet.has(c.id);
      edges.push({
        from: p,
        to: c.id,
        arrows: "to",
        color: isConflicted ? { color: "#ef4444" } : { color: "rgba(96, 165, 250, 0.4)" },
        width: isConflicted ? 3 : 2
      });
    });
  });

  const data = { nodes: nodes, edges: new vis.DataSet(edges) };
  const options = {
    physics: {
      solver: "forceAtlas2Based",
      forceAtlas2Based: { gravitationalConstant: -40, springLength: 90, springConstant: 0.08 }
    },
    interaction: { hover: true, zoomView: true }
  };

  if (state.network) state.network.destroy();
  state.network = new vis.Network(container, data, options);

  state.network.on("click", (params) => {
    if (params.nodes.length > 0) {
      openModal(params.nodes[0]);
    }
  });
}

// --- 3. Advisor Chat Logic ---
function initChatInput() {
  const btn = document.getElementById("chat-submit-btn");
  const input = document.getElementById("chat-input-box");

  if (btn && input) {
    btn.addEventListener("click", () => {
      const text = input.value.trim();
      if (text) {
        input.value = "";
        sendAdvisorPrompt(text);
      }
    });

    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        const text = input.value.trim();
        if (text) {
          input.value = "";
          sendAdvisorPrompt(text);
        }
      }
    });
  }
}

function sendAdvisorPrompt(question) {
  appendChatMessage("user", question);

  setTimeout(() => {
    let reply = "";
    let citations = [];

    const q = question.toLowerCase();
    if (q.includes("cs301") || q.includes("algorithm")) {
      reply = `⚠️ **Prerequisite Policy Notice on CS301 (Algorithms)**:\n\nUnder **Course Catalog 2026 §4.2**, enrollment in CS301 requires passing **CS201 (Data Structures)** with a grade of C or better and completing **MATH201 (Discrete Mathematics)**.\n\nSince CS301 is a single-term Fall offering, clearing these foundational prerequisites is critical to prevent graduation delays.`;
      citations = ["[Course Catalog 2026, §4.2: CS Core]", "[Academic Regulation §1.1: Prerequisite Enforcement]"];
    } else if (q.includes("cs402") || q.includes("machine learning") || q.includes("ml")) {
      reply = `📘 **Prerequisites for CS402 (Machine Learning)**:\n\nCS402 requires **CS301 (Algorithms)** and **MATH202 (Linear Algebra)**. Your transcript confirms MATH202 is already satisfied. Once you clear CS301, you are eligible to enroll immediately.`;
      citations = ["[Course Catalog 2026, Electives §7.1]"];
    } else {
      reply = `🟢 **Academic Progress Summary**:\n\nYou have successfully completed **78 of 120 credits** (65% degree fulfillment) with a cumulative GPA of **3.65**. You are on track for graduation in **Spring 2026**!`;
      citations = ["[Degree Audit Standard §8.3]"];
    }

    appendChatMessage("assistant", reply, citations);
  }, 450);
}

function appendChatMessage(role, text, citations = []) {
  const container = document.getElementById("chat-stream");
  if (!container) return;

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;

  let citHtml = "";
  if (citations.length > 0) {
    citHtml = `<div style="margin-top: 6px;">${citations.map(c => `<span class="citation-tag">📚 ${c}</span>`).join(" ")}</div>`;
  }

  bubble.innerHTML = `<div>${text.replace(/\n/g, "<br>")}</div>${citHtml}`;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// --- 4. Conflict Auditor ---
function initAuditorOptions() {
  const select = document.getElementById("auditor-courses-select");
  if (!select) return;
  select.innerHTML = "";

  APP_DATA.courses.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = `${c.id} - ${c.name} (${c.credits} cr)`;
    select.appendChild(opt);
  });
}

function runScheduleAudit() {
  const select = document.getElementById("auditor-courses-select");
  const selectedCids = Array.from(select.selectedOptions).map(o => o.value);
  const sem = document.getElementById("auditor-sem-select").value;
  const box = document.getElementById("audit-results-box");

  if (selectedCids.length === 0) {
    box.innerHTML = `<div style="color: #f87171;">⚠️ Please select at least one course from the list.</div>`;
    return;
  }

  const s = state.currentStudent;
  const completedSet = new Set(s.completed_courses);
  let issues = [];
  let totalCredits = 0;

  selectedCids.forEach(cid => {
    const c = APP_DATA.courses.find(x => x.id === cid);
    if (!c) return;
    totalCredits += c.credits;

    if (completedSet.has(cid)) {
      issues.push(`⚠️ <strong>${cid}</strong> is already completed on your transcript.`);
    }

    c.prereqs.forEach(p => {
      if (!completedSet.has(p) && !selectedCids.includes(p)) {
        issues.push(`❌ <strong>${cid}</strong> missing prerequisite: requires <strong>${p}</strong>.`);
      }
    });
  });

  if (totalCredits > 18) {
    issues.push(`❌ Total load (${totalCredits} cr) exceeds standard limit of 18 credits (Policy §5.2).`);
  }

  if (issues.length === 0) {
    box.innerHTML = `
      <div style="color: #34d399; font-weight: 700; font-size: 1rem;">✅ All Clear! 100% Validated for Registration</div>
      <div style="font-size: 0.84rem; color: #a7f3d0; margin-top: 4px;">Total Selected: ${totalCredits} credits · All prerequisite requirements satisfied.</div>
    `;
  } else {
    box.innerHTML = `
      <div style="color: #f87171; font-weight: 700; margin-bottom: 8px;">Found ${issues.length} Schedule Issue(s):</div>
      ${issues.map(i => `<div style="margin-bottom: 6px; font-size: 0.85rem; color: #fca5a5;">${i}</div>`).join("")}
    `;
  }
}

// --- Modal Dialog ---
function openModal(cid) {
  const c = APP_DATA.courses.find(x => x.id === cid);
  if (!c) return;

  document.getElementById("modal-code-title").textContent = `${c.id}: ${c.name}`;
  document.getElementById("modal-meta").textContent = `${c.category} · ${c.credits} Credits`;
  document.getElementById("modal-desc").textContent = c.desc;
  document.getElementById("modal-prereqs").textContent = c.prereqs.length > 0 ? c.prereqs.join(", ") : "None (Entry level)";
  
  const subs = APP_DATA.equivalencies[c.id] || ["No pre-approved direct substitute."];
  document.getElementById("modal-subs").textContent = subs.join(" · ");

  document.getElementById("course-modal").classList.add("active");
}

function closeModal() {
  document.getElementById("course-modal").classList.remove("active");
}
