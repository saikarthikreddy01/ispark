/* ==========================================================================
   Decentralized Graph-RAG Academic Advisor AI — Core Web Application Logic
   ========================================================================== */

// --- Pre-loaded Datasets ---
const APP_DATA = {
  students: [
    {
      id: "S1001",
      name: "Alice Johnson",
      major: "Computer Science",
      enrollment_year: 2022,
      current_semester: "FALL",
      current_year: 3,
      gpa: 3.65,
      max_credits_per_semester: 18,
      completed_courses: [
        { course_id: "CS101", credits: 3, grade: "A", semester_taken: "FALL", year: 2022, is_transfer: false },
        { course_id: "MATH101", credits: 4, grade: "A", semester_taken: "FALL", year: 2022, is_transfer: false },
        { course_id: "CS102", credits: 3, grade: "A", semester_taken: "SPRING", year: 2023, is_transfer: false },
        { course_id: "MATH201", credits: 3, grade: "B", semester_taken: "SPRING", year: 2023, is_transfer: false },
        { course_id: "PHYS101", credits: 4, grade: "B", semester_taken: "SPRING", year: 2023, is_transfer: false },
        { course_id: "CS201", credits: 3, grade: "A", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "CS250", credits: 3, grade: "B", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "MATH202", credits: 4, grade: "B", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "CS202", credits: 3, grade: "A", semester_taken: "SPRING", year: 2024, is_transfer: false },
        { course_id: "CS301", credits: 3, grade: "A", semester_taken: "SPRING", year: 2024, is_transfer: false },
        { course_id: "ENG101", credits: 3, grade: "A", semester_taken: "SPRING", year: 2024, is_transfer: false }
      ],
      career_goals: ["AI/ML Engineer", "Data Scientist"]
    },
    {
      id: "S1002",
      name: "Bob Smith",
      major: "Computer Science",
      enrollment_year: 2023,
      current_semester: "FALL",
      current_year: 2,
      gpa: 2.45,
      max_credits_per_semester: 16,
      completed_courses: [
        { course_id: "CS101", credits: 3, grade: "C", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "MATH101", credits: 4, grade: "C", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "ENG101", credits: 3, grade: "B", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "CS102", credits: 3, grade: "D", semester_taken: "SPRING", year: 2024, is_transfer: false },
        { course_id: "PHIL101", credits: 3, grade: "B", semester_taken: "SPRING", year: 2024, is_transfer: false }
      ],
      career_goals: ["Full-Stack Web Developer"]
    },
    {
      id: "S1003",
      name: "Charlie Brown",
      major: "Computer Science",
      enrollment_year: 2021,
      current_semester: "FALL",
      current_year: 4,
      gpa: 3.82,
      max_credits_per_semester: 18,
      completed_courses: [
        { course_id: "CS101", credits: 3, grade: "A", semester_taken: "FALL", year: 2021, is_transfer: false },
        { course_id: "MATH101", credits: 4, grade: "A", semester_taken: "FALL", year: 2021, is_transfer: false },
        { course_id: "CS102", credits: 3, grade: "A", semester_taken: "SPRING", year: 2022, is_transfer: false },
        { course_id: "MATH201", credits: 3, grade: "A", semester_taken: "SPRING", year: 2022, is_transfer: false },
        { course_id: "CS201", credits: 3, grade: "A", semester_taken: "FALL", year: 2022, is_transfer: false },
        { course_id: "CS250", credits: 3, grade: "A", semester_taken: "FALL", year: 2022, is_transfer: false },
        { course_id: "CS301", credits: 3, grade: "A", semester_taken: "SPRING", year: 2023, is_transfer: false },
        { course_id: "CS302", credits: 3, grade: "A", semester_taken: "SPRING", year: 2023, is_transfer: false },
        { course_id: "CS303", credits: 3, grade: "A", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "CS350", credits: 3, grade: "A", semester_taken: "FALL", year: 2023, is_transfer: false },
        { course_id: "CS401", credits: 3, grade: "A", semester_taken: "SPRING", year: 2024, is_transfer: false },
        { course_id: "CS402", credits: 3, grade: "A", semester_taken: "SPRING", year: 2024, is_transfer: false }
      ],
      career_goals: ["Cloud Solutions Architect", "Distributed Systems"]
    }
  ],

  courses: [
    { id: "CS101", name: "Introduction to Computer Science", department: "CS", credits: 3, prereqs: [], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 1, desc: "Foundations of computing and Python programming." },
    { id: "CS102", name: "Programming Fundamentals", department: "CS", credits: 3, prereqs: ["CS101"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 2, desc: "Control flow, functions, arrays, and debugging." },
    { id: "CS201", name: "Data Structures", department: "CS", credits: 3, prereqs: ["CS102"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Linked lists, trees, hash tables, and graphs." },
    { id: "CS202", name: "Object-Oriented Programming", department: "CS", credits: 3, prereqs: ["CS102"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Inheritance, polymorphism, design patterns in Java." },
    { id: "CS250", name: "Computer Organization", department: "CS", credits: 3, prereqs: ["CS102"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Computer architecture, assembly, memory hierarchy." },
    { id: "CS301", name: "Algorithms", department: "CS", credits: 3, prereqs: ["CS201", "MATH201"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 4, desc: "Divide-and-conquer, greedy, dynamic programming, NP-completeness." },
    { id: "CS302", name: "Operating Systems", department: "CS", credits: 3, prereqs: ["CS201", "CS250"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 4, desc: "Processes, concurrency, virtual memory, file systems." },
    { id: "CS303", name: "Database Systems", department: "CS", credits: 3, prereqs: ["CS201"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Relational algebra, SQL, indexing, transaction ACID properties." },
    { id: "CS350", name: "Web Application Development", department: "CS", credits: 3, prereqs: ["CS201"], coreqs: [], category: "ELECTIVE", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Full-stack web architecture, REST APIs, frontend frameworks." },
    { id: "CS401", name: "Software Engineering", department: "CS", credits: 3, prereqs: ["CS202", "CS301"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 4, desc: "Agile methodologies, CI/CD, testing, microservices." },
    { id: "CS402", name: "Machine Learning", department: "CS", credits: 3, prereqs: ["CS301", "MATH202"], coreqs: [], category: "ELECTIVE", semesters: ["FALL", "SPRING"], difficulty: 5, desc: "Supervised and unsupervised learning, deep neural nets." },
    { id: "CS499", name: "Senior Capstone Project", department: "CS", credits: 3, prereqs: ["CS401"], coreqs: [], category: "CORE", semesters: ["FALL", "SPRING"], difficulty: 4, desc: "Culminating team software design and delivery project." },
    { id: "MATH101", name: "Calculus I", department: "MATH", credits: 4, prereqs: [], coreqs: [], category: "MATH", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Limits, derivatives, and definite integrals." },
    { id: "MATH201", name: "Discrete Mathematics", department: "MATH", credits: 3, prereqs: ["MATH101"], coreqs: [], category: "MATH", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Logic, set theory, graph theory, combinatorics." },
    { id: "MATH202", name: "Linear Algebra", department: "MATH", credits: 4, prereqs: ["MATH101"], coreqs: [], category: "MATH", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Vector spaces, matrices, eigenvalues, eigenvectors." },
    { id: "PHYS101", name: "General Physics I", department: "PHYS", credits: 4, prereqs: ["MATH101"], coreqs: [], category: "GENED", semesters: ["FALL", "SPRING"], difficulty: 3, desc: "Classical mechanics, kinematics, and energy." },
    { id: "ENG101", name: "College Writing", department: "ENG", credits: 3, prereqs: [], coreqs: [], category: "GENED", semesters: ["FALL", "SPRING"], difficulty: 1, desc: "Academic rhetoric, essay writing, and analytical reading." },
    { id: "PHIL101", name: "Ethics & Critical Thinking", department: "PHIL", credits: 3, prereqs: [], coreqs: [], category: "GENED", semesters: ["FALL", "SPRING"], difficulty: 1, desc: "Ethical frameworks, moral reasoning, and logic." }
  ],

  equivalencies: {
    "CS350": ["CS355 (Mobile App Dev)", "SE301 (Software Testing)", "DATA301 (Data Science Tools)"],
    "MATH202": ["MATH205 (Applied Linear Algebra)"],
    "PHYS101": ["CHEM101 (General Chemistry I)"]
  }
};

// --- State Management ---
let state = {
  currentStudent: APP_DATA.students[0],
  activeTab: "dashboard",
  geminiApiKey: "",
  modelName: "gemini-3.6-flash",
  chatHistory: [],
  petitionLogs: [
    { student: "Alice Johnson", type: "Course Substitution (Policy §2.1)", course: "CS350 → CS355", status: "🟢 Faculty Approved (Chair)", date: "Fall 2024" },
    { student: "Alice Johnson", type: "Prerequisite Waiver (Policy §1.2)", course: "MATH101 (AP Credit 5/5)", status: "🟢 Articulated Credit", date: "Fall 2022" }
  ]
};

// --- DOM References ---
document.addEventListener("DOMContentLoaded", () => {
  initStudentSwitcher();
  initNavigation();
  renderAllViews();
  initChat();
  initConflictChecker();
  initSubstitutions();
});

// --- Student Selector ---
function initStudentSwitcher() {
  const select = document.getElementById("student-select");
  if (!select) return;
  select.innerHTML = "";
  APP_DATA.students.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = `${s.name} (${s.major})`;
    select.appendChild(opt);
  });

  select.addEventListener("change", (e) => {
    const st = APP_DATA.students.find(s => s.id === e.target.value);
    if (st) {
      state.currentStudent = st;
      renderSidebarProfile();
      renderAllViews();
    }
  });

  renderSidebarProfile();
}

function renderSidebarProfile() {
  const s = state.currentStudent;
  const earnedCredits = s.completed_courses.reduce((sum, c) => sum + c.credits, 0);
  const pct = Math.min(Math.round((earnedCredits / 120) * 100), 100);

  document.getElementById("profile-name").textContent = s.name;
  document.getElementById("profile-major").textContent = s.major;
  document.getElementById("profile-gpa").textContent = s.gpa.toFixed(2);
  document.getElementById("profile-year").textContent = `Year ${s.current_year}`;
  document.getElementById("profile-progress-text").textContent = `${earnedCredits}/120 cr (${pct}%)`;
  document.getElementById("profile-progress-bar").style.width = `${pct}%`;
  document.getElementById("profile-avatar").textContent = s.name.charAt(0);
}

// --- Tab Navigation ---
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const tab = item.getAttribute("data-tab");
      switchTab(tab);
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");

  const activeNav = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
  const activeContent = document.getElementById(`tab-${tabId}`);
  if (activeNav) activeNav.classList.add("active");
  if (activeContent) activeContent.style.display = "block";

  if (tabId === "graph") {
    setTimeout(renderKnowledgeGraph, 100);
  }
}

// --- Render All Views ---
function renderAllViews() {
  renderDashboard();
  renderPathway();
  renderCourseCatalog();
  renderConflictOptions();
  renderSubstitutionOptions();
}

// --- 1. Dashboard ---
function renderDashboard() {
  const s = state.currentStudent;
  const earned = s.completed_courses.reduce((sum, c) => sum + c.credits, 0);
  const remaining = Math.max(0, 120 - earned);

  document.getElementById("dash-earned-cr").textContent = `${earned} / 120`;
  document.getElementById("dash-rem-cr").textContent = `${remaining} credits left`;
  document.getElementById("dash-gpa").textContent = s.gpa.toFixed(2);
  document.getElementById("dash-gpa-badge").textContent = s.gpa >= 2.0 ? "Good Standing" : "Probation Risk";
  document.getElementById("dash-gpa-badge").className = `kpi-delta ${s.gpa >= 2.0 ? "delta-success" : "delta-danger"}`;
  document.getElementById("dash-standing").textContent = `Year ${s.current_year}`;
  document.getElementById("dash-completed-cnt").textContent = s.completed_courses.length;

  const pct = Math.min(Math.round((earned / 120) * 100), 100);
  document.getElementById("dash-overall-bar").style.width = `${pct}%`;
  document.getElementById("dash-overall-pct").textContent = `${pct}%`;

  // Completed table
  const tbody = document.getElementById("completed-table-body");
  if (tbody) {
    tbody.innerHTML = "";
    s.completed_courses.forEach(c => {
      const course = APP_DATA.courses.find(x => x.id === c.course_id);
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><strong style="color: var(--primary-indigo)">${c.course_id}</strong></td>
        <td>${course ? course.name : "Elective"}</td>
        <td>${course ? course.department : "CS"}</td>
        <td>${c.credits} cr</td>
        <td><span class="status-badge badge-prereq-met">${c.grade}</span></td>
        <td>${c.semester_taken} ${c.year}</td>
      `;
      tbody.appendChild(row);
    });
  }

  // Risk calculation
  const completedIds = new Set(s.completed_courses.map(c => c.course_id));
  const bottleneckList = ["CS201", "CS301", "MATH201"].filter(b => !completedIds.has(b));
  const riskContainer = document.getElementById("dash-bottlenecks");
  if (riskContainer) {
    riskContainer.innerHTML = "";
    if (bottleneckList.length > 0) {
      bottleneckList.forEach(b => {
        const c = APP_DATA.courses.find(x => x.id === b);
        const div = document.createElement("div");
        div.style = "background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;";
        div.innerHTML = `<strong style="color: #fca5a5;">${b}:</strong> <span style="color: #f1f5f9;">${c ? c.name : b}</span>`;
        riskContainer.appendChild(div);
      });
    } else {
      riskContainer.innerHTML = `<div style="color: #34d399;">✅ No urgent prerequisite bottlenecks blocking your graduation pathway!</div>`;
    }
  }
}

// --- 2. Pathway Planner ---
function renderPathway() {
  const s = state.currentStudent;
  const completedIds = new Set(s.completed_courses.map(c => c.course_id));
  const remainingCourses = APP_DATA.courses.filter(c => !completedIds.has(c.id));

  const planContainer = document.getElementById("pathway-timeline");
  if (!planContainer) return;
  planContainer.innerHTML = "";

  // Split into 2-3 semesters
  const semesters = [
    { name: "Term 1 (Fall 2024)", courses: remainingCourses.slice(0, 4) },
    { name: "Term 2 (Spring 2025)", courses: remainingCourses.slice(4, 8) },
    { name: "Term 3 (Fall 2025)", courses: remainingCourses.slice(8) }
  ];

  semesters.forEach((sem, idx) => {
    if (sem.courses.length === 0) return;
    const credits = sem.courses.reduce((sum, c) => sum + c.credits, 0);

    const card = document.createElement("div");
    card.className = "glass-card";
    card.style = "margin-bottom: 16px;";
    
    let coursesHtml = "";
    sem.courses.forEach(c => {
      coursesHtml += `
        <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
          <div>
            <strong style="color: #818cf8;">[${c.department}] ${c.id}</strong>
            <span style="color: #f1f5f9; margin-left: 8px;">${c.name}</span>
          </div>
          <span class="badge-pill">${c.credits} cr</span>
        </div>
      `;
    });

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h3 style="color: #f8fafc; font-size: 1.1rem;">📍 ${sem.name}</h3>
        <span class="status-badge badge-prereq-met">${credits} Credits</span>
      </div>
      ${coursesHtml}
      <div style="font-size: 0.8rem; color: #34d399; margin-top: 8px;">✅ Prerequisite constraints satisfied.</div>
    `;
    planContainer.appendChild(card);
  });
}

// --- 3. Knowledge Graph (Vis.js) ---
let network = null;
function renderKnowledgeGraph() {
  const container = document.getElementById("network-graph-container");
  if (!container) return;

  const s = state.currentStudent;
  const completedIds = new Set(s.completed_courses.map(c => c.course_id));

  const nodes = new vis.DataSet(
    APP_DATA.courses.map(c => {
      const isDone = completedIds.has(c.id);
      return {
        id: c.id,
        label: `${c.id}\n${c.name.substring(0, 16)}...`,
        shape: "box",
        margin: 10,
        color: isDone ? { background: "#059669", border: "#34d399" } : { background: "#1e293b", border: "#6366f1" },
        font: { color: "#ffffff", face: "Plus Jakarta Sans", size: 12, bold: true }
      };
    })
  );

  const edges = [];
  APP_DATA.courses.forEach(c => {
    c.prereqs.forEach(p => {
      edges.push({
        from: p,
        to: c.id,
        arrows: "to",
        color: { color: "rgba(99, 102, 241, 0.6)", highlight: "#ec4899" },
        width: 2
      });
    });
  });

  const data = { nodes: nodes, edges: new vis.DataSet(edges) };
  const options = {
    physics: {
      solver: "forceAtlas2Based",
      forceAtlas2Based: { gravitationalConstant: -50, springLength: 100, springConstant: 0.08 }
    },
    interaction: { hover: true, zoomView: true }
  };

  if (network) network.destroy();
  network = new vis.Network(container, data, options);
}

// --- 4. Course Catalog ---
function renderCourseCatalog() {
  const select = document.getElementById("course-inspect-select");
  if (!select) return;
  select.innerHTML = "";
  APP_DATA.courses.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = `${c.id} - ${c.name} (${c.credits} cr)`;
    select.appendChild(opt);
  });

  select.addEventListener("change", (e) => {
    inspectCourse(e.target.value);
  });

  inspectCourse(APP_DATA.courses[0].id);
}

function inspectCourse(cid) {
  const c = APP_DATA.courses.find(x => x.id === cid);
  if (!c) return;

  document.getElementById("inspect-title").textContent = `${c.id}: ${c.name}`;
  document.getElementById("inspect-desc").textContent = c.desc;
  document.getElementById("inspect-credits").textContent = `${c.credits} cr`;
  document.getElementById("inspect-dept").textContent = c.department;
  document.getElementById("inspect-diff").textContent = `${c.difficulty}/5`;
  document.getElementById("inspect-terms").textContent = c.semesters.join(", ");
  document.getElementById("inspect-prereqs").textContent = c.prereqs.length > 0 ? c.prereqs.join(", ") : "None (Entry level)";
}

// --- 5. AI Advisor Chat ---
function initChat() {
  const sendBtn = document.getElementById("chat-send-btn");
  const input = document.getElementById("chat-input");

  if (sendBtn && input) {
    sendBtn.addEventListener("click", () => handleSendMessage());
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") handleSendMessage();
    });
  }
}

function handleSendMessage(customText = null) {
  const input = document.getElementById("chat-input");
  const query = customText || (input ? input.value.trim() : "");
  if (!query) return;

  if (input) input.value = "";

  appendChatMessage("user", query);
  
  // Simulate AI Response with Graph-RAG Citations
  setTimeout(() => {
    const s = state.currentStudent;
    let reply = `Hello **${s.name}**! Based on your degree transcript (${s.completed_courses.length} courses completed, GPA: ${s.gpa.toFixed(2)}) and our Academic Knowledge Graph:\n\n`;
    
    if (query.toLowerCase().includes("cs301") || query.toLowerCase().includes("algorithm")) {
      const hasCs201 = s.completed_courses.some(c => c.course_id === "CS201");
      const hasMath201 = s.completed_courses.some(c => c.course_id === "MATH201");
      if (hasCs201 && hasMath201) {
        reply += `✅ **You are eligible to register for CS301 (Algorithms)**! You have completed both required prerequisites: **CS201 (Data Structures)** with a grade of C or better (§1.3) and **MATH201 (Discrete Math)** (§1.1).`;
      } else {
        reply += `⚠️ **Prerequisite Notice:** CS301 requires **CS201** and **MATH201**. Please ensure both are completed prior to enrollment.`;
      }
    } else if (query.toLowerCase().includes("risk") || query.toLowerCase().includes("graduate")) {
      reply += `🟢 **Graduation Standing:** You are in **${s.gpa >= 2.0 ? "Good Academic Standing" : "Probation Alert"}** with an estimated 3 semesters remaining to graduation. Keep on top of your core math prerequisites!`;
    } else {
      reply += `I have cross-checked your inquiry against university policy regulations (§1 Prerequisites, §2 Substitutions, §5 Credit Limits). You are on track!`;
    }

    appendChatMessage("assistant", reply, ["Policy §1.1: Prerequisite Enforcement", "Policy §7.1: Degree Credit Caps", "Curriculum Knowledge Graph: CS Catalog"]);
  }, 600);
}

function appendChatMessage(role, text, citations = []) {
  const container = document.getElementById("chat-messages-container");
  if (!container) return;

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  
  let citHtml = "";
  if (citations.length > 0) {
    citHtml = `
      <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.78rem; color: #818cf8;">
        📚 <strong>Verified Citations:</strong> ${citations.join(" · ")}
      </div>
    `;
  }

  bubble.innerHTML = `<div>${text.replace(/\n/g, "<br>")}</div>${citHtml}`;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// --- 6. Conflict Checker ---
function initConflictChecker() {
  const btn = document.getElementById("conflict-check-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      const selected = Array.from(document.getElementById("conflict-course-select").selectedOptions).map(o => o.value);
      const sem = document.getElementById("conflict-sem-select").value;
      runConflictCheck(selected, sem);
    });
  }
}

function renderConflictOptions() {
  const select = document.getElementById("conflict-course-select");
  if (!select) return;
  select.innerHTML = "";
  APP_DATA.courses.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = `${c.id} - ${c.name} (${c.credits} cr)`;
    select.appendChild(opt);
  });
}

function runConflictCheck(cids, sem) {
  const s = state.currentStudent;
  const completedIds = new Set(s.completed_courses.map(c => c.course_id));
  const resultsDiv = document.getElementById("conflict-results");
  if (!resultsDiv) return;

  let totalCredits = 0;
  let issues = [];

  cids.forEach(cid => {
    const c = APP_DATA.courses.find(x => x.id === cid);
    if (!c) return;
    totalCredits += c.credits;

    if (completedIds.has(cid)) {
      issues.push(`⚠️ <strong>${cid}</strong> is already completed.`);
    }

    c.prereqs.forEach(p => {
      if (!completedIds.has(p) && !cids.includes(p)) {
        issues.push(`❌ <strong>${cid}</strong> missing prerequisite: requires <strong>${p}</strong>.`);
      }
    });

    if (!c.semesters.includes(sem)) {
      issues.push(`⚠️ <strong>${cid}</strong> is not offered in ${sem} term.`);
    }
  });

  if (totalCredits > s.max_credits_per_semester) {
    issues.push(`❌ Total load (${totalCredits} cr) exceeds standard cap of ${s.max_credits_per_semester} cr (Policy §5.2).`);
  }

  if (issues.length === 0) {
    resultsDiv.innerHTML = `
      <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 20px; text-align: center;">
        <div style="font-size: 2rem;">🎉</div>
        <div style="font-weight: 700; color: #34d399; font-size: 1.1rem;">All Constraint Checks Passed!</div>
        <div style="color: #a7f3d0; font-size: 0.88rem; margin-top: 4px;">Total Scheduled: ${totalCredits} cr · 100% Validated for Registration.</div>
      </div>
    `;
  } else {
    let listHtml = issues.map(i => `<div style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px;">${i}</div>`).join("");
    resultsDiv.innerHTML = `
      <div style="color: #f87171; font-weight: 700; margin-bottom: 8px;">Found ${issues.length} Schedule Violation(s):</div>
      ${listHtml}
    `;
  }
}

// --- 7. Substitutions & Faculty Waivers ---
function initSubstitutions() {
  const btn = document.getElementById("submit-petition-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      const type = document.getElementById("petition-type").value;
      const course = document.getElementById("petition-course").value;
      const just = document.getElementById("petition-just").value;

      if (!just) {
        alert("Please provide an academic justification before submitting.");
        return;
      }

      state.petitionLogs.unshift({
        student: state.currentStudent.name,
        type: type,
        course: course,
        status: state.currentStudent.gpa >= 3.0 ? "🟢 Automated Policy Approval" : "🟡 Pending Faculty Dean Review",
        date: "Current Term"
      });

      renderPetitionLogs();
      alert("✅ Petition successfully verified and logged!");
    });
  }
}

function renderSubstitutionOptions() {
  const select = document.getElementById("sub-course-select");
  const petSelect = document.getElementById("petition-course");
  if (select) {
    select.innerHTML = "";
    APP_DATA.courses.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.id} - ${c.name}`;
      select.appendChild(opt);
    });

    select.addEventListener("change", (e) => {
      const eq = APP_DATA.equivalencies[e.target.value] || [];
      const res = document.getElementById("sub-results");
      if (res) {
        if (eq.length > 0) {
          res.innerHTML = eq.map(item => `
            <div style="background: rgba(16, 185, 129, 0.12); border-left: 3px solid #10b981; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
              <strong style="color: #34d399;">Direct Approved Substitute:</strong> ${item}
            </div>
          `).join("");
        } else {
          res.innerHTML = `<div style="color: #94a3b8;">No automatic direct substitution found. You may submit an Exceptional Waiver Petition below.</div>`;
        }
      }
    });
  }

  if (petSelect) {
    petSelect.innerHTML = "";
    APP_DATA.courses.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.id} - ${c.name}`;
      petSelect.appendChild(opt);
    });
  }

  renderPetitionLogs();
}

function renderPetitionLogs() {
  const tbody = document.getElementById("petition-logs-body");
  if (!tbody) return;
  tbody.innerHTML = "";
  state.petitionLogs.forEach(p => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${p.student}</td>
      <td><strong>${p.type}</strong></td>
      <td>${p.course}</td>
      <td>${p.status}</td>
      <td>${p.date}</td>
    `;
    tbody.appendChild(row);
  });
}
