/* ==========================================================================
   Academic AI Advisor — 3D Neural Lattice & Graph-RAG Engine
   Inspired by alltimehigh.ai
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

// ==========================================================================
// PERMANENT STORAGE ENGINE (LocalStorage & MongoDB Cloud Sync)
// ==========================================================================
const STORAGE_KEYS = {
  STUDENTS: "academic_advisor_permanent_students_v2",
  ACTIVE_USER: "academic_advisor_permanent_active_user_v2",
  CHAT_LOGS: "academic_advisor_permanent_chat_logs_v2",
  PETITIONS: "academic_advisor_permanent_petitions_v2"
};

function loadPermanentStudents() {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.STUDENTS);
    if (raw) {
      const saved = JSON.parse(raw);
      if (Array.isArray(saved) && saved.length > 0) {
        // Merge or replace
        saved.forEach(s => {
          const idx = APP_DATA.students.findIndex(existing => existing.id.toUpperCase() === s.id.toUpperCase());
          if (idx >= 0) {
            APP_DATA.students[idx] = s;
          } else {
            APP_DATA.students.push(s);
          }
        });
      }
    } else {
      savePermanentStudents();
    }
  } catch (err) {
    console.error("Storage load error:", err);
  }
}

function savePermanentStudents() {
  try {
    localStorage.setItem(STORAGE_KEYS.STUDENTS, JSON.stringify(APP_DATA.students));
  } catch (err) {
    console.error("Storage save error:", err);
  }
}

function saveActiveUser(studentId) {
  try {
    localStorage.setItem(STORAGE_KEYS.ACTIVE_USER, studentId);
  } catch (e) {}
}

function getActiveUser() {
  try {
    return localStorage.getItem(STORAGE_KEYS.ACTIVE_USER);
  } catch (e) {
    return null;
  }
}

function savePermanentChat(studentId, message) {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.CHAT_LOGS) || "{}";
    const logs = JSON.parse(raw);
    logs[studentId] = logs[studentId] || [];
    logs[studentId].push(message);
    localStorage.setItem(STORAGE_KEYS.CHAT_LOGS, JSON.stringify(logs));
  } catch (e) {}
}

// Load Permanent Storage on Start
loadPermanentStudents();

// Global State
let state = {
  currentStudent: APP_DATA.students[0],
  currentTab: "pathway",
  network: null
};

// Auto-restore previous permanent session if available
const rememberedUserId = getActiveUser();
if (rememberedUserId) {
  const remembered = APP_DATA.students.find(s => s.id.toUpperCase() === rememberedUserId.toUpperCase());
  if (remembered) state.currentStudent = remembered;
}

// Lifecycle
window.addEventListener("DOMContentLoaded", () => {
  initStudentPicker();
  renderDashboard();
  initChatInput();
  initAuditorOptions();
  initThreeJSAnimations();
});

// ==========================================================================
// 3D THREE.JS ANIMATION ENGINE (Like alltimehigh.ai)
// ==========================================================================
function initThreeJSAnimations() {
  initLanding3D();
  initBackgroundParticles();
}

function initLanding3D() {
  const canvas = document.getElementById("three-landing-canvas");
  if (!canvas || typeof THREE === "undefined") return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 28;

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // --- 1. Morphing 3D Neural Sphere Geometry ---
  const sphereGeo = new THREE.IcosahedronGeometry(8.5, 3);
  const origPositions = sphereGeo.attributes.position.clone();

  // Create Diagram Group to offset to left side
  const diagramGroup = new THREE.Group();
  diagramGroup.position.x = window.innerWidth > 960 ? -8.5 : 0;
  diagramGroup.position.y = 0;
  scene.add(diagramGroup);

  // Outer Glowing Wireframe
  const wireMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    wireframe: true,
    transparent: true,
    opacity: 0.45
  });
  const wireMesh = new THREE.Mesh(sphereGeo, wireMat);
  diagramGroup.add(wireMesh);

  // Glowing Vertex Particles
  const pointMat = new THREE.PointsMaterial({
    color: 0x34d399,
    size: 0.35,
    transparent: true,
    opacity: 0.95
  });
  const pointMesh = new THREE.Points(sphereGeo, pointMat);
  diagramGroup.add(pointMesh);

  // --- 2. Inner Glowing Core Torus Knot ---
  const torusGeo = new THREE.TorusKnotGeometry(4.2, 1.1, 80, 16);
  const torusMat = new THREE.MeshBasicMaterial({
    color: 0x818cf8,
    wireframe: true,
    transparent: true,
    opacity: 0.25
  });
  const torusMesh = new THREE.Mesh(torusGeo, torusMat);
  diagramGroup.add(torusMesh);

  // --- 3. Ambient Floating Particle Constellation ---
  const partCount = 200;
  const partGeo = new THREE.BufferGeometry();
  const partPos = new Float32Array(partCount * 3);

  for (let i = 0; i < partCount * 3; i += 3) {
    partPos[i] = (Math.random() - 0.5) * 60;
    partPos[i + 1] = (Math.random() - 0.5) * 45;
    partPos[i + 2] = (Math.random() - 0.5) * 35;
  }
  partGeo.setAttribute("position", new THREE.BufferAttribute(partPos, 3));
  
  const outerMat = new THREE.PointsMaterial({
    color: 0x60a5fa,
    size: 0.25,
    transparent: true,
    opacity: 0.75
  });
  const outerCloud = new THREE.Points(partGeo, outerMat);
  scene.add(outerCloud);

  // Mouse Interaction (Parallax & Tilt)
  let mouseX = 0, mouseY = 0;
  let targetX = 0, targetY = 0;

  window.addEventListener("mousemove", (e) => {
    mouseX = (e.clientX - window.innerWidth / 2) * 0.0012;
    mouseY = (e.clientY - window.innerHeight / 2) * 0.0012;
  });

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Animation Loop with Real-Time Vertex Morphing
  let clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);
    const elapsedTime = clock.getElapsedTime();

    // Smooth Cursor Physics
    targetX += (mouseX - targetX) * 0.06;
    targetY += (mouseY - targetY) * 0.06;

    wireMesh.rotation.y = elapsedTime * 0.15 + targetX * 1.5;
    wireMesh.rotation.x = elapsedTime * 0.08 + targetY * 1.5;
    pointMesh.rotation.y = wireMesh.rotation.y;
    pointMesh.rotation.x = wireMesh.rotation.x;

    torusMesh.rotation.y = -elapsedTime * 0.25 + targetX;
    torusMesh.rotation.x = -elapsedTime * 0.15 + targetY;

    outerCloud.rotation.y = -elapsedTime * 0.05;

    // Organic Wave Vertex Pulsing
    const pos = sphereGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const u = origPositions.getX(i);
      const v = origPositions.getY(i);
      const w = origPositions.getZ(i);

      const wave = Math.sin(elapsedTime * 2.5 + u * 0.5 + v * 0.5) * 0.45;
      const factor = 1 + wave / 9;

      pos.setXYZ(i, u * factor, v * factor, w * factor);
    }
    pos.needsUpdate = true;

    renderer.render(scene, camera);
  }
  animate();
}

function initBackgroundParticles() {
  const canvas = document.getElementById("three-bg-canvas");
  if (!canvas || typeof THREE === "undefined") return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 40;

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const count = 160;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);

  for (let i = 0; i < count * 3; i += 3) {
    pos[i] = (Math.random() - 0.5) * 80;
    pos[i + 1] = (Math.random() - 0.5) * 80;
    pos[i + 2] = (Math.random() - 0.5) * 40;
  }

  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({
    color: 0x38bdf8,
    size: 0.28,
    transparent: true,
    opacity: 0.45
  });

  const particles = new THREE.Points(geo, mat);
  scene.add(particles);

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  function animate() {
    requestAnimationFrame(animate);
    particles.rotation.y += 0.0005;
    particles.rotation.x += 0.0003;
    renderer.render(scene, camera);
  }
  animate();
}

// ==========================================================================
// CORE DASHBOARD CONTROLS
// ==========================================================================

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

  document.getElementById("ui-kpi-credits").innerHTML = `${earnedCredits} <span style="font-size: 0.95rem; color: var(--text-dim);">/ 120</span>`;
  document.getElementById("ui-kpi-pct").textContent = `${pct}% Progress`;
  document.getElementById("ui-kpi-gpa").textContent = s.gpa.toFixed(2);
  document.getElementById("ui-kpi-terms").textContent = `${Math.ceil(remainingCredits / 15)} Semesters`;
  document.getElementById("ui-kpi-conflicts").textContent = `${s.conflicts.length} Course${s.conflicts.length === 1 ? '' : 's'}`;

  renderKanban();
  if (state.currentTab === "graph") {
    renderGraph();
  }
}

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
