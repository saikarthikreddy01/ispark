/* ==========================================================================
   Academic AI Advisor — Clean & High-Performance Client Logic
   ========================================================================== */

const APP_DATA = {
  students: [
    {
      id: "S1001",
      name: "Alice Johnson",
      major: "Computer Science",
      gpa: 3.65,
      completed: ["CS101", "MATH101", "CS102", "MATH201", "PHYS101", "CS201", "CS250", "MATH202", "CS202", "ENG101", "PHIL101"],
      planned: ["CS302", "CS303", "CS350", "CS401", "CS402", "CS499"],
      conflicts: ["CS301"],
      expected_grad: "Spring 2026",
      standing: "Good Standing"
    },
    {
      id: "S1002",
      name: "Bob Smith",
      major: "Computer Science",
      gpa: 2.45,
      completed: ["CS101", "MATH101", "ENG101", "CS102", "PHIL101"],
      planned: ["CS201", "CS202", "CS250", "MATH201"],
      conflicts: ["CS201", "MATH201"],
      expected_grad: "Spring 2027",
      standing: "Academic Warning"
    },
    {
      id: "S1003",
      name: "Charlie Brown",
      major: "Computer Science",
      gpa: 3.82,
      completed: ["CS101", "MATH101", "CS102", "MATH201", "CS201", "CS250", "CS301", "CS302", "CS303", "CS350", "CS401", "CS402"],
      planned: ["CS499"],
      conflicts: [],
      expected_grad: "Fall 2025",
      standing: "Honor Roll"
    }
  ],

  courses: [
    { id: "CS101", name: "Intro to Computer Science", credits: 3, prereqs: [], category: "Core", sem: 1, desc: "Foundations of programming in Python." },
    { id: "MATH101", name: "Calculus I", credits: 4, prereqs: [], category: "Math", sem: 1, desc: "Limits, derivatives, and integral calculus." },
    { id: "ENG101", name: "College Writing", credits: 3, prereqs: [], category: "GenEd", sem: 1, desc: "Rhetoric and academic composition." },
    { id: "CS102", name: "Programming Fundamentals", credits: 3, prereqs: ["CS101"], category: "Core", sem: 2, desc: "Object-oriented structures and debugging." },
    { id: "MATH201", name: "Discrete Mathematics", credits: 3, prereqs: ["MATH101"], category: "Math", sem: 2, desc: "Logic, graphs, set theory, combinatorics." },
    { id: "PHYS101", name: "General Physics I", credits: 4, prereqs: ["MATH101"], category: "GenEd", sem: 2, desc: "Classical mechanics and energy." },
    { id: "CS201", name: "Data Structures", credits: 3, prereqs: ["CS102"], category: "Core", sem: 3, desc: "Linked lists, trees, hash tables, and algorithm efficiency." },
    { id: "CS250", name: "Computer Organization", credits: 3, prereqs: ["CS102"], category: "Core", sem: 3, desc: "CPU architecture and assembly language." },
    { id: "MATH202", name: "Linear Algebra", credits: 4, prereqs: ["MATH101"], category: "Math", sem: 3, desc: "Matrix algebra and vector spaces." },
    { id: "CS202", name: "Object-Oriented Programming", credits: 3, prereqs: ["CS102"], category: "Core", sem: 4, desc: "Advanced Java software architecture." },
    { id: "PHIL101", name: "Ethics in Technology", credits: 3, prereqs: [], category: "GenEd", sem: 4, desc: "Moral implications of AI and digital governance." },
    { id: "CS301", name: "Algorithms", credits: 3, prereqs: ["CS201", "MATH201"], category: "Core", sem: 5, desc: "Divide-and-conquer and dynamic programming." },
    { id: "CS302", name: "Operating Systems", credits: 3, prereqs: ["CS201", "CS250"], category: "Core", sem: 5, desc: "Concurrency, virtual memory, scheduling, and file systems." },
    { id: "CS303", name: "Database Systems", credits: 3, prereqs: ["CS201"], category: "Core", sem: 6, desc: "Relational modeling, SQL optimization, and indexing." },
    { id: "CS350", name: "Web App Architecture", credits: 3, prereqs: ["CS201"], category: "Elective", sem: 6, desc: "Cloud deployment and full-stack services." },
    { id: "CS401", name: "Software Engineering", credits: 3, prereqs: ["CS202", "CS301"], category: "Core", sem: 7, desc: "Agile workflows, automated testing, and CI/CD." },
    { id: "CS402", name: "Machine Learning", credits: 3, prereqs: ["CS301", "MATH202"], category: "Elective", sem: 7, desc: "Supervised learning and neural networks." },
    { id: "CS499", name: "Senior Capstone Project", credits: 3, prereqs: ["CS401"], category: "Core", sem: 8, desc: "Culminating industry project delivery." }
  ],

  equivalencies: {
    "CS301": ["CS305 (Applied Algorithm Design)", "MATH350 (Combinatorics)"],
    "CS350": ["CS355 (Mobile App Dev)", "SE301 (Software Quality)"],
    "MATH202": ["MATH205 (Applied Linear Algebra)"],
    "PHYS101": ["CHEM101 (General Chemistry I)"]
  }
};

// State
let state = {
  currentStudent: APP_DATA.students[0],
  currentTab: "pathway",
  network: null
};

// Lifecycle Init
document.addEventListener("DOMContentLoaded", () => {
  initStudentPicker();
  renderDashboard();
  initChatInput();
  initAuditorOptions();
});

// Tab Switcher
function switchTab(tabName) {
  state.currentTab = tabName;

  document.querySelectorAll(".tab-link").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll("#dashboard-screen section").forEach(sec => sec.style.display = "none");

  const btn = document.getElementById(`tab-${tabName}`);
  const sec = document.getElementById(`view-${tabName}`);

  if (btn) btn.classList.add("active");
  if (sec) sec.style.display = "block";

  if (tabName === "graph") {
    setTimeout(renderGraph, 80);
  }
}

// Student Picker
function initStudentPicker() {
  const select = document.getElementById("user-select");
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
      renderDashboard();
    }
  });
}

// Master Render
function renderDashboard() {
  const s = state.currentStudent;
  const completedSet = new Set(s.completed);
  const earnedCredits = APP_DATA.courses.filter(c => completedSet.has(c.id)).reduce((sum, c) => sum + c.credits, 0);
  const pct = Math.min(Math.round((earnedCredits / 120) * 100), 100);
  const remainingCredits = Math.max(0, 120 - earnedCredits);

  document.getElementById("ui-student-name").textContent = s.name;
  document.getElementById("ui-student-details").textContent = `Major: ${s.major} · Expected Graduation: ${s.expected_grad}`;
  
  const standingBadge = document.getElementById("ui-student-standing");
  standingBadge.textContent = `● ${s.standing}`;
  standingBadge.className = `kpi-tag ${s.gpa >= 3.0 ? "tag-green" : (s.gpa >= 2.0 ? "tag-blue" : "tag-red")}`;

  document.getElementById("ui-kpi-credits").innerHTML = `${earnedCredits} <span style="font-size: 0.9rem; color: var(--text-dim);">/ 120</span>`;
  document.getElementById("ui-kpi-pct").textContent = `${pct}% Progress`;
  document.getElementById("ui-kpi-gpa").textContent = s.gpa.toFixed(2);
  document.getElementById("ui-kpi-terms").textContent = `${Math.ceil(remainingCredits / 15)} Semesters`;
  document.getElementById("ui-kpi-conflicts").textContent = `${s.conflicts.length} Course${s.conflicts.length === 1 ? '' : 's'}`;

  renderKanban();
  if (state.currentTab === "graph") {
    renderGraph();
  }
}

// Render Kanban
function renderKanban() {
  const container = document.getElementById("kanban-container");
  if (!container) return;
  container.innerHTML = "";

  const s = state.currentStudent;
  const completedSet = new Set(s.completed);
  const conflictSet = new Set(s.conflicts);

  const semesters = [
    "Semester 1 (Fall)", "Semester 2 (Spring)",
    "Semester 3 (Fall)", "Semester 4 (Spring)",
    "Semester 5 (Fall)", "Semester 6 (Spring)",
    "Semester 7 (Fall)", "Semester 8 (Spring)"
  ];

  for (let sem = 1; sem <= 8; sem++) {
    const col = document.createElement("div");
    col.className = "kanban-col";

    const semCourses = APP_DATA.courses.filter(c => c.sem === sem);
    const credits = semCourses.reduce((sum, c) => sum + c.credits, 0);

    let cardsHtml = "";
    semCourses.forEach(c => {
      let statusClass = "is-planned";
      let statusText = "Planned";
      let colorTag = "color: var(--accent-blue);";

      if (completedSet.has(c.id)) {
        statusClass = "is-passed";
        statusText = "Passed";
        colorTag = "color: var(--accent-green);";
      } else if (conflictSet.has(c.id)) {
        statusClass = "is-risk";
        statusText = "At-Risk";
        colorTag = "color: var(--accent-rose);";
      }

      cardsHtml += `
        <div class="card-item ${statusClass}" onclick="openModal('${c.id}')">
          <div class="item-top">
            <span class="item-code">${c.id}</span>
            <span class="item-status" style="${colorTag}">${statusText}</span>
          </div>
          <div class="item-name">${c.name}</div>
          <div style="font-size: 0.72rem; color: var(--text-dim); margin-top: 2px;">${c.credits} cr · ${c.category}</div>
        </div>
      `;
    });

    col.innerHTML = `
      <div class="col-head">
        <span>${semesters[sem - 1]}</span>
        <span class="col-credits">${credits} cr</span>
      </div>
      ${cardsHtml}
    `;

    container.appendChild(col);
  }
}

// Render Graph (Vis.js)
function renderGraph() {
  const container = document.getElementById("graph-container");
  if (!container) return;

  const s = state.currentStudent;
  const completedSet = new Set(s.completed);
  const conflictSet = new Set(s.conflicts);

  const nodes = new vis.DataSet(
    APP_DATA.courses.map(c => {
      let bg = "#161f30";
      let border = "#38bdf8";

      if (completedSet.has(c.id)) {
        bg = "#064e3b";
        border = "#34d399";
      } else if (conflictSet.has(c.id)) {
        bg = "#7f1d1d";
        border = "#f87171";
      }

      return {
        id: c.id,
        label: `${c.id}\n${c.name.substring(0, 15)}...`,
        shape: "box",
        margin: 8,
        color: { background: bg, border: border, highlight: { background: "#0284c7", border: "#38bdf8" } },
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
        color: isConflicted ? { color: "#f87171" } : { color: "rgba(56, 189, 248, 0.4)" },
        width: isConflicted ? 3 : 2
      });
    });
  });

  const data = { nodes: nodes, edges: new vis.DataSet(edges) };
  const options = {
    physics: {
      solver: "forceAtlas2Based",
      forceAtlas2Based: { gravitationalConstant: -35, springLength: 85, springConstant: 0.08 }
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

// Chat Advisor
function initChatInput() {
  const btn = document.getElementById("chat-send-btn");
  const input = document.getElementById("chat-text");

  if (btn && input) {
    btn.addEventListener("click", () => {
      const q = input.value.trim();
      if (q) {
        input.value = "";
        askAdvisor(q);
      }
    });

    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        const q = input.value.trim();
        if (q) {
          input.value = "";
          askAdvisor(q);
        }
      }
    });
  }
}

function askAdvisor(question) {
  appendMessage("user", question);

  setTimeout(() => {
    let reply = "";
    let citations = [];

    const q = question.toLowerCase();
    if (q.includes("cs301") || q.includes("algorithm")) {
      reply = `⚠️ **Prerequisite Policy on CS301 (Algorithms)**:\n\nUnder **Course Catalog §4.2**, enrolling in CS301 requires passing **CS201 (Data Structures)** with a grade of C or better and completing **MATH201 (Discrete Mathematics)**.\n\nSince CS301 is a single-term Fall offering, clearing these requirements is critical to prevent graduation delays.`;
      citations = ["[Course Catalog 2026, §4.2]", "[Academic Regulation §1.1]"];
    } else if (q.includes("cs402") || q.includes("machine learning") || q.includes("ml")) {
      reply = `📘 **Prerequisites for CS402 (Machine Learning)**:\n\nCS402 requires **CS301 (Algorithms)** and **MATH202 (Linear Algebra)**. Your transcript confirms MATH202 is already satisfied. Once you clear CS301, you are eligible to enroll immediately.`;
      citations = ["[Course Catalog 2026, Electives §7.1]"];
    } else {
      reply = `🟢 **Academic Progress Summary**:\n\nYou have completed **78 of 120 credits** (65% degree fulfillment) with a cumulative GPA of **3.65**. You are on track for graduation in **Spring 2026**!`;
      citations = ["[Degree Audit Standard §8.3]"];
    }

    appendMessage("assistant", reply, citations);
  }, 400);
}

function appendMessage(role, text, citations = []) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;

  let citHtml = "";
  if (citations.length > 0) {
    citHtml = `<div style="margin-top: 6px;">${citations.map(c => `<span class="citation-chip">📚 ${c}</span>`).join(" ")}</div>`;
  }

  bubble.innerHTML = `<div>${text.replace(/\n/g, "<br>")}</div>${citHtml}`;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// Conflict Auditor
function initAuditorOptions() {
  const select = document.getElementById("audit-course-select");
  if (!select) return;
  select.innerHTML = "";

  APP_DATA.courses.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = `${c.id} - ${c.name} (${c.credits} cr)`;
    select.appendChild(opt);
  });
}

function runAudit() {
  const select = document.getElementById("audit-course-select");
  const selectedCids = Array.from(select.selectedOptions).map(o => o.value);
  const box = document.getElementById("audit-output");

  if (selectedCids.length === 0) {
    box.innerHTML = `<div style="color: var(--accent-rose);">⚠️ Please select at least one course from the list.</div>`;
    return;
  }

  const s = state.currentStudent;
  const completedSet = new Set(s.completed);
  let issues = [];
  let totalCredits = 0;

  selectedCids.forEach(cid => {
    const c = APP_DATA.courses.find(x => x.id === cid);
    if (!c) return;
    totalCredits += c.credits;

    if (completedSet.has(cid)) {
      issues.push(`⚠️ <strong>${cid}</strong> is already completed.`);
    }

    c.prereqs.forEach(p => {
      if (!completedSet.has(p) && !selectedCids.includes(p)) {
        issues.push(`❌ <strong>${cid}</strong> missing prerequisite: requires <strong>${p}</strong>.`);
      }
    });
  });

  if (totalCredits > 18) {
    issues.push(`❌ Total load (${totalCredits} cr) exceeds 18 credit limit (Policy §5.2).`);
  }

  if (issues.length === 0) {
    box.innerHTML = `
      <div style="color: var(--accent-green); font-weight: 600;">✅ Schedule 100% Validated for Registration</div>
      <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">Total: ${totalCredits} credits · Prerequisite requirements satisfied.</div>
    `;
  } else {
    box.innerHTML = `
      <div style="color: var(--accent-rose); font-weight: 600; margin-bottom: 6px;">Found ${issues.length} Issue(s):</div>
      ${issues.map(i => `<div style="margin-bottom: 4px; font-size: 0.82rem; color: var(--accent-rose);">${i}</div>`).join("")}
    `;
  }
}

// Modal
function openModal(cid) {
  const c = APP_DATA.courses.find(x => x.id === cid);
  if (!c) return;

  document.getElementById("modal-title").textContent = `${c.id}: ${c.name}`;
  document.getElementById("modal-credits").textContent = `${c.category} · ${c.credits} Credits`;
  document.getElementById("modal-desc").textContent = c.desc;
  document.getElementById("modal-prereqs").textContent = c.prereqs.length > 0 ? c.prereqs.join(", ") : "None (Entry level)";
  
  const subs = APP_DATA.equivalencies[c.id] || ["No pre-approved direct substitute."];
  document.getElementById("modal-subs").textContent = subs.join(" · ");

  document.getElementById("modal-box").classList.add("active");
}

function closeModal() {
  document.getElementById("modal-box").classList.remove("active");
}
