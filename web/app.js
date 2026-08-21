/* ==========================================================================
   PathFinder AI — Master Client-Side Logic & Graph-RAG Engine
   ========================================================================== */

// --- Comprehensive Academic Dataset ---
const APP_DATA = {
  students: [
    {
      id: "S1001",
      name: "Alice Johnson",
      major: "Computer Science",
      gpa: 3.65,
      completed_courses: ["CS101", "MATH101", "CS102", "MATH201", "PHYS101", "CS201", "CS250", "MATH202", "CS202", "ENG101", "PHIL101"],
      planned_courses: ["CS302", "CS303", "CS350", "CS401", "CS402", "CS499"],
      conflicts: ["CS301"], // Flagged conflict (attempting CS301 while missing MATH201 prerequisite grade standard)
      expected_graduation: "Spring 2026",
      career_goal: "AI/ML Engineer"
    },
    {
      id: "S1002",
      name: "Bob Smith",
      major: "Computer Science",
      gpa: 2.45,
      completed_courses: ["CS101", "MATH101", "ENG101", "CS102", "PHIL101"],
      planned_courses: ["CS201", "CS202", "CS250", "MATH201"],
      conflicts: ["CS201", "MATH201"],
      expected_graduation: "Spring 2027",
      career_goal: "Full-Stack Web Development"
    },
    {
      id: "S1003",
      name: "Charlie Brown",
      major: "Computer Science",
      gpa: 3.82,
      completed_courses: ["CS101", "MATH101", "CS102", "MATH201", "CS201", "CS250", "CS301", "CS302", "CS303", "CS350", "CS401", "CS402"],
      planned_courses: ["CS499"],
      conflicts: [],
      expected_graduation: "Fall 2025",
      career_goal: "Cloud & Distributed Systems"
    }
  ],

  courses: [
    { id: "CS101", name: "Intro to Computer Science", credits: 3, prereqs: [], category: "CORE", semester_order: 1, desc: "Foundations of programming in Python." },
    { id: "MATH101", name: "Calculus I", credits: 4, prereqs: [], category: "MATH", semester_order: 1, desc: "Limits, derivatives, integrals." },
    { id: "ENG101", name: "College Writing", credits: 3, prereqs: [], category: "GENED", semester_order: 1, desc: "Academic rhetoric & composition." },
    { id: "CS102", name: "Programming Fundamentals", credits: 3, prereqs: ["CS101"], category: "CORE", semester_order: 2, desc: "Data structures, memory, and algorithms." },
    { id: "MATH201", name: "Discrete Mathematics", credits: 3, prereqs: ["MATH101"], category: "MATH", semester_order: 2, desc: "Logic, graphs, set theory, combinatorics." },
    { id: "PHYS101", name: "General Physics I", credits: 4, prereqs: ["MATH101"], category: "GENED", semester_order: 2, desc: "Mechanics, kinematics, thermodynamics." },
    { id: "CS201", name: "Data Structures", credits: 3, prereqs: ["CS102"], category: "CORE", semester_order: 3, desc: "Linked lists, binary trees, hash tables, graphs." },
    { id: "CS250", name: "Computer Organization", credits: 3, prereqs: ["CS102"], category: "CORE", semester_order: 3, desc: "Assembly, CPU architecture, memory caches." },
    { id: "MATH202", name: "Linear Algebra", credits: 4, prereqs: ["MATH101"], category: "MATH", semester_order: 3, desc: "Matrix operations, eigenvalues, vector spaces." },
    { id: "CS202", name: "Object-Oriented Programming", credits: 3, prereqs: ["CS102"], category: "CORE", semester_order: 4, desc: "OOP design patterns, Java/C++ architecture." },
    { id: "PHIL101", name: "Ethics in Technology", credits: 3, prereqs: [], category: "GENED", semester_order: 4, desc: "Moral reasoning and tech governance." },
    { id: "CS301", name: "Algorithms", credits: 3, prereqs: ["CS201", "MATH201"], category: "CORE", semester_order: 5, desc: "Divide-conquer, greedy, dynamic programming." },
    { id: "CS302", name: "Operating Systems", credits: 3, prereqs: ["CS201", "CS250"], category: "CORE", semester_order: 5, desc: "Processes, virtual memory, concurrency, I/O." },
    { id: "CS303", name: "Database Systems", credits: 3, prereqs: ["CS201"], category: "CORE", semester_order: 6, desc: "Relational algebra, SQL, indexes, transactions." },
    { id: "CS350", name: "Web Application Architecture", credits: 3, prereqs: ["CS201"], category: "ELECTIVE", semester_order: 6, desc: "Full-stack cloud systems, microservices." },
    { id: "CS401", name: "Software Engineering", credits: 3, prereqs: ["CS202", "CS301"], category: "CORE", semester_order: 7, desc: "Agile, CI/CD, unit testing, delivery." },
    { id: "CS402", name: "Machine Learning", credits: 3, prereqs: ["CS301", "MATH202"], category: "ELECTIVE", semester_order: 7, desc: "Neural networks, regression, classification." },
    { id: "CS499", name: "Senior Capstone Project", credits: 3, prereqs: ["CS401"], category: "CORE", semester_order: 8, desc: "Culminating industry project delivery." }
  ],

  equivalencies: {
    "CS301": ["CS305 (Applied Algorithm Design)", "MATH350 (Combinatorial Algorithms)"],
    "CS350": ["CS355 (Mobile App Dev)", "SE301 (Software Testing)", "DATA301 (Data Tools)"],
    "MATH202": ["MATH205 (Applied Linear Algebra)"],
    "PHYS101": ["CHEM101 (General Chemistry I)"]
  }
};

// --- Application State ---
let state = {
  currentStudent: APP_DATA.students[0],
  activeTab: "timeline",
  network: null
};

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  initStudentDropdown();
  renderAllViews();
  initChatEngine();
});

// --- Student Selector ---
function initStudentDropdown() {
  const select = document.getElementById("top-student-select");
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
      renderAllViews();
    }
  });
}

// --- Render All Master Components ---
function renderAllViews() {
  updateTopNavStats();
  renderKanbanTimeline();
  if (state.activeTab === "graph") {
    renderPrereqGraph();
  }
}

// --- Top Navbar Stats ---
function updateTopNavStats() {
  const s = state.currentStudent;
  const completedCourses = APP_DATA.courses.filter(c => s.completed_courses.includes(c.id));
  const earnedCredits = completedCourses.reduce((sum, c) => sum + c.credits, 0);
  const pct = Math.min(Math.round((earnedCredits / 120) * 100), 100);

  document.getElementById("top-credits-text").textContent = `${earnedCredits} / 120 cr`;
  document.getElementById("top-progress-pct").textContent = `${pct}%`;
  document.getElementById("top-gpa-text").textContent = s.gpa.toFixed(2);
  document.getElementById("top-grad-horizon").textContent = `· ${s.expected_graduation}`;
}

// --- 1. Render Horizontal Semester Kanban Timeline ---
function renderKanbanTimeline() {
  const container = document.getElementById("kanban-columns-feed");
  if (!container) return;
  container.innerHTML = "";

  const s = state.currentStudent;
  const completedSet = new Set(s.completed_courses);
  const conflictSet = new Set(s.conflicts);

  // 8 Semester Columns
  const semesterNames = [
    "Semester 1 (Fall)", "Semester 2 (Spring)",
    "Semester 3 (Fall)", "Semester 4 (Spring)",
    "Semester 5 (Fall)", "Semester 6 (Spring)",
    "Semester 7 (Fall)", "Semester 8 (Spring)"
  ];

  for (let sem = 1; sem <= 8; sem++) {
    const col = document.createElement("div");
    col.className = "kanban-column";
    
    const semCourses = APP_DATA.courses.filter(c => c.semester_order === sem);
    const totalSemCredits = semCourses.reduce((sum, c) => sum + c.credits, 0);

    let coursesHtml = "";
    semCourses.forEach(c => {
      let statusClass = "status-planned";
      let badgeHtml = '<span class="course-status-badge badge-blue">Planned</span>';

      if (completedSet.has(c.id)) {
        statusClass = "status-completed";
        badgeHtml = '<span class="course-status-badge badge-green">Passed</span>';
      } else if (conflictSet.has(c.id)) {
        statusClass = "status-at-risk";
        badgeHtml = '<span class="course-status-badge badge-red">At-Risk</span>';
      }

      coursesHtml += `
        <div class="course-card ${statusClass}" id="card-${c.id}" onclick="openCourseModal('${c.id}')">
          <div class="course-code">
            <span>${c.id}</span>
            ${badgeHtml}
          </div>
          <div class="course-name">${c.name}</div>
          <div style="font-size: 0.72rem; color: var(--text-subtle); margin-top: 4px;">${c.credits} Credits</div>
        </div>
      `;
    });

    col.innerHTML = `
      <div class="kanban-column-header">
        <div class="kanban-column-title">${semesterNames[sem - 1]}</div>
        <div class="kanban-column-credits">${totalSemCredits} cr</div>
      </div>
      ${coursesHtml}
    `;

    container.appendChild(col);
  }
}

// --- 2. Render Interactive Prerequisite Graph (Vis.js) ---
function renderPrereqGraph(highlightNodeId = null) {
  const container = document.getElementById("graph-viewport-container");
  if (!container) return;

  const s = state.currentStudent;
  const completedSet = new Set(s.completed_courses);
  const conflictSet = new Set(s.conflicts);

  const nodes = new vis.DataSet(
    APP_DATA.courses.map(c => {
      let bg = "#1e293b";
      let border = "#3b82f6";

      if (completedSet.has(c.id)) {
        bg = "#065f46";
        border = "#34d399";
      } else if (conflictSet.has(c.id) || c.id === highlightNodeId) {
        bg = "#991b1b";
        border = "#f87171";
      }

      return {
        id: c.id,
        label: `${c.id}\n${c.name.substring(0, 15)}...`,
        shape: "box",
        margin: 10,
        color: { background: bg, border: border, highlight: { background: "#2563eb", border: "#60a5fa" } },
        font: { color: "#ffffff", face: "Plus Jakarta Sans", size: 12, bold: true }
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
        color: isConflicted ? { color: "#ef4444", highlight: "#f87171" } : { color: "rgba(96, 165, 250, 0.5)", highlight: "#34d399" },
        width: isConflicted ? 3 : 2
      });
    });
  });

  const data = { nodes: nodes, edges: new vis.DataSet(edges) };
  const options = {
    physics: {
      solver: "forceAtlas2Based",
      forceAtlas2Based: { gravitationalConstant: -45, springLength: 90, springConstant: 0.08 }
    },
    interaction: { hover: true, zoomView: true }
  };

  if (state.network) state.network.destroy();
  state.network = new vis.Network(container, data, options);

  state.network.on("click", (params) => {
    if (params.nodes.length > 0) {
      openCourseModal(params.nodes[0]);
    }
  });

  if (highlightNodeId) {
    state.network.focus(highlightNodeId, { scale: 1.2, animation: { duration: 600, easingFunction: "easeInOutQuad" } });
  }
}

// --- View Tab Switcher ---
function switchVisualTab(tabName) {
  state.activeTab = tabName;
  const btnTimeline = document.getElementById("btn-tab-timeline");
  const btnGraph = document.getElementById("btn-tab-graph");
  const viewTimeline = document.getElementById("view-timeline-container");
  const viewGraph = document.getElementById("view-graph-container");
  const viewTitle = document.getElementById("view-title");
  const viewSub = document.getElementById("view-subtitle");

  if (tabName === "timeline") {
    btnTimeline.classList.add("active");
    btnGraph.classList.remove("active");
    viewTimeline.style.display = "block";
    viewGraph.style.display = "none";
    viewTitle.textContent = "🗺️ Degree Pathway Timeline";
    viewSub.textContent = "Semester-by-semester sequencing color-coded by prerequisite status.";
  } else {
    btnGraph.classList.add("active");
    btnTimeline.classList.remove("active");
    viewGraph.style.display = "block";
    viewTimeline.style.display = "none";
    viewTitle.textContent = "🕸️ Prerequisite & Conflict Knowledge Graph";
    viewSub.textContent = "Interactive node graph highlighting dependencies and critical prerequisite bottlenecks.";
    setTimeout(() => renderPrereqGraph(), 100);
  }
}

// --- Visual Agentic Reasoning: Question & Cross-Highlighting ---
function initChatEngine() {
  const sendBtn = document.getElementById("advisor-send-btn");
  const input = document.getElementById("advisor-user-input");

  if (sendBtn && input) {
    sendBtn.addEventListener("click", () => {
      const q = input.value.trim();
      if (q) {
        input.value = "";
        askAdvisorQuestion(q);
      }
    });

    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        const q = input.value.trim();
        if (q) {
          input.value = "";
          askAdvisorQuestion(q);
        }
      }
    });
  }
}

function askAdvisorQuestion(questionText) {
  appendChatMessage("user", questionText);

  // Agentic Reasoning Simulation with Node Highlighting
  setTimeout(() => {
    let reply = "";
    let targetNode = null;
    let citations = [];

    const lower = questionText.toLowerCase();
    if (lower.includes("cs301") || lower.includes("algorithm")) {
      targetNode = "CS301";
      reply = `⚠️ **Prerequisite Conflict Flagged on CS301 (Algorithms)**:\n\nAccording to **Course Catalog 2026 §4.2**, enrolling in CS301 requires passing **CS201 (Data Structures)** with a grade of C or better and completing **MATH201 (Discrete Math)**.\n\nI have highlighted **CS301** in red on your Knowledge Graph and Pathway.`;
      citations = ["[Course Catalog 2026, Sec 4.2]", "[Academic Policy §1.1: Prerequisite Enforcement]"];
    } else if (lower.includes("cs402") || lower.includes("machine learning") || lower.includes("ml")) {
      targetNode = "CS402";
      reply = `📘 **Prerequisites for CS402 (Machine Learning)**:\n\nCS402 requires **CS301 (Algorithms)** and **MATH202 (Linear Algebra)**. Since MATH202 is completed, once you clear CS301 you are fully eligible to take Machine Learning!`;
      citations = ["[Course Catalog 2026, CS Electives §7.1]"];
    } else {
      targetNode = "CS499";
      reply = `🟢 **Degree Horizon Audit**:\n\nYou have completed **78/120 credits** (65%). With an average semester load of 15 credits, you are on track to graduate on schedule in **Spring 2026**!`;
      citations = ["[Degree Audit Regulation §8.3]"];
    }

    appendChatMessage("assistant", reply, citations);

    // Trigger Visual Agentic Reasoning: Highlight on Graph & Pulse Timeline Card
    if (targetNode) {
      // Pulse card on timeline
      const card = document.getElementById(`card-${targetNode}`);
      if (card) {
        card.classList.add("pulse-highlight");
        card.scrollIntoView({ behavior: "smooth", inline: "center" });
        setTimeout(() => card.classList.remove("pulse-highlight"), 4000);
      }

      // Highlight on Graph
      if (state.activeTab === "graph") {
        renderPrereqGraph(targetNode);
      }
    }
  }, 500);
}

function appendChatMessage(role, text, citations = []) {
  const container = document.getElementById("chat-messages-stream");
  if (!container) return;

  const bubble = document.createElement("div");
  bubble.className = `msg-bubble ${role}`;

  let citHtml = "";
  if (citations.length > 0) {
    citHtml = `
      <div style="margin-top: 8px;">
        ${citations.map(c => `<span class="citation-pill" onclick="switchVisualTab('graph')">📚 ${c}</span>`).join(" ")}
      </div>
    `;
  }

  bubble.innerHTML = `<div>${text.replace(/\n/g, "<br>")}</div>${citHtml}`;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// --- Modals (Course Details & Substitutions) ---
function openCourseModal(cid) {
  const c = APP_DATA.courses.find(x => x.id === cid);
  if (!c) return;

  const overlay = document.getElementById("course-modal-overlay");
  document.getElementById("modal-course-title").textContent = `${c.id}: ${c.name}`;
  document.getElementById("modal-course-dept").textContent = `${c.category} · ${c.credits} Credits`;
  document.getElementById("modal-course-desc").textContent = c.desc;
  document.getElementById("modal-course-prereqs").textContent = c.prereqs.length > 0 ? c.prereqs.join(", ") : "None (Entry level)";
  
  const subs = APP_DATA.equivalencies[c.id] || ["No pre-approved direct substitute."];
  document.getElementById("modal-course-subs").textContent = subs.join(" · ");

  overlay.classList.add("active");
}

function openSubstitutionModal(cid) {
  openCourseModal(cid);
}

function closeModal() {
  document.getElementById("course-modal-overlay").classList.remove("active");
}
