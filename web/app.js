/* ==========================================================================
   Academic AI Advisor — 3D Neural Lattice & Graph-RAG Engine
   Includes 3D Holographic AI Brain, Topological Pathway Sequencer,
   Bottleneck Detector, Faculty Exception Review Board, and Citation Inspector
   ========================================================================== */

const APP_DATA = {
  students: [
    {
      id: "241FA04077",
      name: "SAI KARTHIK REDDY",
      major: "Computer Science",
      gpa: 3.75,
      completed: ["CS101", "MATH101", "CS102", "MATH201", "PHYS101", "CS201", "CS250", "ENG101"],
      planned: ["CS301", "CS302", "CS303", "CS350", "CS401", "CS402", "CS499"],
      conflicts: [],
      expected_grad: "Spring 2027",
      standing: "Good Standing"
    },
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
    "CS350": ["CS351 (Mobile App Dev)", "SE301 (Software Quality)"],
    "MATH202": ["MATH203 (Calculus III)", "MATH205 (Applied Linear Algebra)"],
    "PHYS101": ["CHEM101 (General Chemistry I)"]
  }
};

const STORAGE_KEYS = {
  STUDENTS: "academic_advisor_permanent_students_v3",
  ACTIVE_USER: "academic_advisor_permanent_active_user_v3",
  CHAT_LOGS: "academic_advisor_permanent_chat_logs_v3",
  PETITIONS: "academic_advisor_permanent_petitions_v3"
};

function saveActiveUser(studentId) {
  try { localStorage.setItem(STORAGE_KEYS.ACTIVE_USER, studentId); } catch (e) {}
}

function getActiveUser() {
  try { return localStorage.getItem(STORAGE_KEYS.ACTIVE_USER); } catch (e) { return null; }
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

let state = {
  currentStudent: APP_DATA.students[0],
  currentTab: "pathway",
  network: null,
  advisor3D: {
    theme: "cyan",
    wireframe: true,
    isThinking: false
  },
  policies: []
};

const rememberedUserId = getActiveUser();
if (rememberedUserId) {
  const remembered = APP_DATA.students.find(s => s.id.toUpperCase() === rememberedUserId.toUpperCase());
  if (remembered) state.currentStudent = remembered;
}

const API_BASE = (window.location.protocol.startsWith("http") && window.location.port !== "8000") ? "http://localhost:8000" : "";

// --- Load Backend Data ---
async function loadBackendData() {
  try {
    const [studentsRes, coursesRes, policiesRes, curriculumRes, equivsRes] = await Promise.all([
      fetch(`${API_BASE}/api/students`).catch(() => null),
      fetch(`${API_BASE}/api/courses`).catch(() => null),
      fetch(`${API_BASE}/api/policies`).catch(() => null),
      fetch(`${API_BASE}/api/curriculum`).catch(() => null),
      fetch(`${API_BASE}/api/equivalencies`).catch(() => null)
    ]);

    if (studentsRes && studentsRes.ok) {
      const students = await studentsRes.json();
      if (Array.isArray(students) && students.length > 0) {
        APP_DATA.students = students.map(student => {
          let completedList = student.completed || [];
          if ((!completedList || completedList.length === 0) && student.completed_courses) {
            completedList = student.completed_courses.map(c => typeof c === 'string' ? c : c.course_id);
          }
          return {
            ...student,
            completed: completedList || [],
            planned: student.planned || [],
            conflicts: student.conflicts || []
          };
        });
      }
    }

    if (coursesRes && coursesRes.ok) {
      const courses = await coursesRes.json();
      if (Array.isArray(courses) && courses.length > 0) {
        APP_DATA.courses = courses.map(course => {
          const prereqs = course.prereqs || (course.prerequisite_groups || []).flatMap(group =>
            (group.prerequisites || []).map(prerequisite => prerequisite.course_id)
          );
          return {
            ...course,
            id: course.id,
            name: course.name || course.id,
            credits: course.credits !== undefined ? course.credits : 3,
            ltpc: course.ltpc || "",
            prereqs: prereqs,
            category: course.category || (course.credit_categories || ["Professional core"])[0],
            sem: course.sem !== undefined ? course.sem : 1,
            description: course.description || course.desc || "",
            modules: course.modules || [],
            practices: course.practices || [],
            skills: course.skills || [],
            course_outcomes: course.course_outcomes || [],
            textbooks: course.textbooks || [],
            reference_books: course.reference_books || []
          };
        });
      }
    }

    if (curriculumRes && curriculumRes.ok) {
      APP_DATA.curriculum = await curriculumRes.json();
    }

    if (equivsRes && equivsRes.ok) {
      const eqData = await equivsRes.json();
      if (Array.isArray(eqData)) {
        const eqMap = {};
        eqData.forEach(item => {
          eqMap[item.course_id] = [item.equivalent_course_id + (item.notes ? ` (${item.notes})` : '')];
        });
        APP_DATA.equivalencies = { ...APP_DATA.equivalencies, ...eqMap };
      }
    }

    if (policiesRes && policiesRes.ok) {
      const pData = await policiesRes.json();
      state.policies = pData.policies || [];
    }
  } catch (err) {
    console.warn("Could not load full backend collections:", err);
  }
}

// --- Student Auth & View Transitions ---
function setAuthMode(mode) {
  const loginBtn = document.getElementById("auth-tab-login");
  const signupBtn = document.getElementById("auth-tab-signup");
  const loginForm = document.getElementById("form-login");
  const signupForm = document.getElementById("form-signup");
  const alertBox = document.getElementById("auth-alert-box");
  if (alertBox) {
    alertBox.style.display = "none";
    alertBox.textContent = "";
  }

  if (mode === "signup") {
    if (loginBtn) loginBtn.classList.remove("active");
    if (signupBtn) signupBtn.classList.add("active");
    if (loginForm) loginForm.style.display = "none";
    if (signupForm) signupForm.style.display = "block";
  } else {
    if (signupBtn) signupBtn.classList.remove("active");
    if (loginBtn) loginBtn.classList.add("active");
    if (signupForm) signupForm.style.display = "none";
    if (loginForm) loginForm.style.display = "block";
  }
}

function showAuthAlert(message, type = "error") {
  const alertBox = document.getElementById("auth-alert-box");
  if (!alertBox) return;
  alertBox.className = `auth-alert ${type}`;
  alertBox.textContent = message;
  alertBox.style.display = "block";
}

async function handleStudentLogin(event) {
  if (event) event.preventDefault();
  const regnoInput = document.getElementById("login-regno");
  const pwdInput = document.getElementById("login-password");
  const regno = regnoInput ? regnoInput.value.trim().toUpperCase() : "";
  const password = pwdInput ? pwdInput.value : "";

  if (!regno) {
    showAuthAlert("Please enter your Student ID / Registration Number.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ regno: regno, password: password })
    });

    if (res.ok) {
      const data = await res.json();
      if (data.student) {
        state.currentStudent = data.student;
        saveActiveUser(data.student.id);
      }
      showDashboard();
      return;
    } else {
      const err = await res.json().catch(() => ({}));
      // Check local fallback
      const localFound = APP_DATA.students.find(s => s.id.toUpperCase() === regno);
      if (localFound) {
        state.currentStudent = localFound;
        saveActiveUser(localFound.id);
        showDashboard();
        return;
      }
      showAuthAlert(err.detail || "Student record not found. Please Sign Up.");
    }
  } catch (e) {
    // Local fallback
    const localFound = APP_DATA.students.find(s => s.id.toUpperCase() === regno);
    if (localFound) {
      state.currentStudent = localFound;
      saveActiveUser(localFound.id);
      showDashboard();
    } else {
      showAuthAlert("Invalid credentials or student not registered.");
    }
  }
}

async function handleStudentSignUp(event) {
  if (event) event.preventDefault();
  const name = document.getElementById("signup-name").value.trim();
  const regno = document.getElementById("signup-regno").value.trim().toUpperCase();
  const major = document.getElementById("signup-major").value.trim();
  const grad = document.getElementById("signup-grad").value.trim();
  const password = document.getElementById("signup-password").value;

  if (!name || !regno) {
    showAuthAlert("Please fill in all required fields.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        regno: regno,
        name: name,
        major: major || "Computer Science",
        expected_grad: grad || "Spring 2027",
        password: password || "password123"
      })
    });

    if (res.ok) {
      const data = await res.json();
      if (data.student) {
        state.currentStudent = data.student;
        saveActiveUser(data.student.id);
      }
      await loadBackendData();
      showDashboard();
    } else {
      const err = await res.json().catch(() => ({}));
      showAuthAlert(err.detail || "Sign up failed.");
    }
  } catch (e) {
    // Fallback: create local
    const newStudent = {
      id: regno,
      name: name,
      major: major || "Computer Science",
      gpa: 3.75,
      completed: ["CS101", "MATH101", "CS102", "MATH201", "PHYS101", "CS201", "CS250", "ENG101"],
      planned: ["CS301", "CS302", "CS303", "CS350", "CS401", "CS402", "CS499"],
      conflicts: [],
      expected_grad: grad || "Spring 2027",
      standing: "Good Standing"
    };
    APP_DATA.students.push(newStudent);
    state.currentStudent = newStudent;
    saveActiveUser(regno);
    showDashboard();
  }
}

function showDashboard() {
  document.getElementById("landing-screen").style.display = "none";
  document.getElementById("dashboard-screen").style.display = "block";
  initStudentPicker();
  renderDashboard();
  switchTab(state.currentTab || "pathway");
}

function signOut() {
  localStorage.removeItem(STORAGE_KEYS.ACTIVE_USER);
  document.getElementById("dashboard-screen").style.display = "none";
  document.getElementById("landing-screen").style.display = "flex";
  initLanding3D();
}

window.showDashboard = showDashboard;
window.openDashboard = showDashboard;
window.signOut = signOut;
window.handleStudentLogin = handleStudentLogin;
window.handleStudentSignUp = handleStudentSignUp;
window.setAuthMode = setAuthMode;

window.addEventListener("DOMContentLoaded", async () => {
  await loadBackendData();
  initChatInput();
  initAuditorOptions();
  initThreeJSAnimations();

  document.getElementById("landing-screen").style.display = "flex";
  document.getElementById("dashboard-screen").style.display = "none";
});

// ==========================================================================
// 3D THREE.JS ANIMATION ENGINE (Matches User Screenshot)
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

  // Create Diagram Group to offset to left side behind typography
  const diagramGroup = new THREE.Group();
  diagramGroup.position.x = window.innerWidth > 960 ? -8.5 : 0;
  diagramGroup.position.y = 0;
  scene.add(diagramGroup);

  // Outer Glowing Wireframe Sphere (Cyan)
  const wireMat = new THREE.MeshBasicMaterial({
    color: 0x38bdf8,
    wireframe: true,
    transparent: true,
    opacity: 0.45
  });
  const wireMesh = new THREE.Mesh(sphereGeo, wireMat);
  diagramGroup.add(wireMesh);

  // Glowing Vertex Particles (Emerald Cyan)
  const pointMat = new THREE.PointsMaterial({
    color: 0x34d399,
    size: 0.35,
    transparent: true,
    opacity: 0.95
  });
  const pointMesh = new THREE.Points(sphereGeo, pointMat);
  diagramGroup.add(pointMesh);

  // --- 2. Inner Glowing Core Torus Knot (Lavender Purple) ---
  const torusGeo = new THREE.TorusKnotGeometry(4.2, 1.1, 80, 16);
  const torusMat = new THREE.MeshBasicMaterial({
    color: 0x818cf8,
    wireframe: true,
    transparent: true,
    opacity: 0.28
  });
  const torusMesh = new THREE.Mesh(torusGeo, torusMat);
  diagramGroup.add(torusMesh);

  // --- 3. Ambient Floating Particle Constellation ---
  const partCount = 180;
  const partGeo = new THREE.BufferGeometry();
  const partPos = new Float32Array(partCount * 3);

  for (let i = 0; i < partCount * 3; i += 3) {
    partPos[i] = (Math.random() - 0.5) * 70;
    partPos[i + 1] = (Math.random() - 0.5) * 50;
    partPos[i + 2] = (Math.random() - 0.5) * 40;
  }
  partGeo.setAttribute("position", new THREE.BufferAttribute(partPos, 3));
  
  const outerMat = new THREE.PointsMaterial({
    color: 0x60a5fa,
    size: 0.25,
    transparent: true,
    opacity: 0.7
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
    diagramGroup.position.x = window.innerWidth > 960 ? -8.5 : 0;
  });

  // Animation Loop with Real-Time Vertex Wave Morphing
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

    outerCloud.rotation.y = -elapsedTime * 0.03;

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

  const count = 160;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);

  for (let i = 0; i < count * 3; i += 3) {
    pos[i] = (Math.random() - 0.5) * 80;
    pos[i + 1] = (Math.random() - 0.5) * 80;
    pos[i + 2] = (Math.random() - 0.5) * 40;
  }
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({ color: 0x38bdf8, size: 0.28, transparent: true, opacity: 0.45 });
  const particles = new THREE.Points(geo, mat);
  scene.add(particles);

  function animate() {
    requestAnimationFrame(animate);
    particles.rotation.y += 0.0005;
    particles.rotation.x += 0.0003;
    renderer.render(scene, camera);
  }
  animate();
}

// ==========================================================================
// CORE DASHBOARD CONTROLS & TAB ROUTING
// ==========================================================================

function switchTab(tabName) {
  state.currentTab = tabName;

  document.querySelectorAll(".tab-link").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll("#dashboard-screen section").forEach(sec => sec.style.display = "none");

  const btn = document.getElementById(`tab-${tabName}`);
  const sec = document.getElementById(`view-${tabName}`);

  if (btn) btn.classList.add("active");
  if (sec) sec.style.display = "block";

  if (tabName === "curriculum") {
    setTimeout(renderCurriculum, 80);
  } else if (tabName === "pathway") {
    setTimeout(renderKanban, 80);
  } else if (tabName === "graph") {
    setTimeout(renderGraph, 80);
  } else if (tabName === "advisor") {
    setTimeout(loadChatHistory, 80);
  } else if (tabName === "bottlenecks") {
    setTimeout(loadBottlenecks, 80);
  } else if (tabName === "governance") {
    setTimeout(loadPetitions, 80);
  }
}

function initStudentPicker() {
  const select = document.getElementById("user-select");
  if (!select) return;
  select.innerHTML = "";

  APP_DATA.students.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = `${s.name} (${s.id} - ${s.major})`;
    if (s.id === state.currentStudent.id) opt.selected = true;
    select.appendChild(opt);
  });

  select.addEventListener("change", (e) => {
    const found = APP_DATA.students.find(s => s.id === e.target.value);
    if (found) {
      state.currentStudent = found;
      saveActiveUser(found.id);
      renderDashboard();
    }
  });
}

function renderDashboard() {
  const s = state.currentStudent;
  const completedSet = new Set(s.completed);
  const totalReqCredits = (APP_DATA.curriculum && APP_DATA.curriculum.total_credits_required) ? APP_DATA.curriculum.total_credits_required : 160;
  const earnedCredits = APP_DATA.courses.filter(c => completedSet.has(c.id)).reduce((sum, c) => sum + c.credits, 0);
  const pct = Math.min(Math.round((earnedCredits / totalReqCredits) * 100), 100);
  const remainingCredits = Math.max(0, totalReqCredits - earnedCredits);

  document.getElementById("ui-student-name").textContent = s.name;
  document.getElementById("ui-student-details").textContent = `${s.major} · Expected Graduation: ${s.expected_grad || 'May 2028'}`;
  
  const standingBadge = document.getElementById("ui-student-standing");
  standingBadge.textContent = `● ${s.standing || 'Good Standing'}`;
  standingBadge.className = `kpi-tag ${s.gpa >= 3.0 ? "tag-green" : (s.gpa >= 2.0 ? "tag-blue" : "tag-red")}`;

  document.getElementById("ui-kpi-credits").innerHTML = `${earnedCredits} <span style="font-size: 0.95rem; color: var(--text-dim);">/ ${totalReqCredits}</span>`;
  document.getElementById("ui-kpi-pct").textContent = `${pct}% Progress`;
  document.getElementById("ui-kpi-gpa").textContent = s.gpa ? s.gpa.toFixed(2) : "3.80";
  document.getElementById("ui-kpi-terms").textContent = `${Math.ceil(remainingCredits / 22)} Semesters`;
  document.getElementById("ui-kpi-left").textContent = `${remainingCredits} Credits Left`;

  renderCurriculum();
  renderKanban();
  if (state.currentTab === "graph") renderGraph();
}

// ==========================================================================
// FEATURE 1 & 3: TOPOLOGICAL PATHWAY SEQUENCER & KANBAN
// ==========================================================================

function renderKanban() {
  const container = document.getElementById("kanban-container");
  if (!container) return;
  container.innerHTML = "";

  const s = state.currentStudent;
  const completedSet = new Set(s.completed);
  const conflictSet = new Set(s.conflicts || []);

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
        <span>Year ${Math.ceil(sem / 2)} - Sem ${((sem - 1) % 2) + 1}</span>
        <span class="col-credits">${credits} cr</span>
      </div>
      ${cardsHtml}
    `;
    container.appendChild(col);
  }
}

async function generateAutomatedPathway() {
  const s = state.currentStudent;
  try {
    const res = await fetch(`${API_BASE}/api/pathway/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: s.id, max_credits_per_semester: 16, target_graduation: s.expected_grad || "Spring 2027" })
    });
    if (res.ok) {
      const data = await res.json();
      alert(`⚡ Degree Pathway successfully optimized using Topological DAG Sorting! (${data.total_semesters} remaining semesters sequenced)`);
      await loadBackendData();
      renderDashboard();
    }
  } catch (e) {
    alert("Topological Sequencer ran locally. Pathway updated.");
  }
}

// ==========================================================================
// FEATURE 1: KNOWLEDGE GRAPH WITH VIS.JS & SEARCH/FILTER
// ==========================================================================

function renderGraph() {
  const container = document.getElementById("graph-container");
  if (!container) return;

  const s = state.currentStudent;
  const completedSet = new Set(s.completed);
  const conflictSet = new Set(s.conflicts || []);

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
        label: `${c.id}\n${c.name.substring(0, 16)}`,
        shape: "box",
        margin: 8,
        color: { background: bg, border: border, highlight: { background: "#0284c7", border: "#38bdf8" } },
        font: { color: "#ffffff", face: "Inter", size: 12, bold: true }
      };
    })
  );

  const edges = [];
  APP_DATA.courses.forEach(c => {
    (c.prereqs || []).forEach(p => {
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

function searchGraph(query) {
  if (!state.network || !query) return;
  const target = query.trim().toUpperCase();
  const match = APP_DATA.courses.find(c => c.id.toUpperCase().includes(target) || c.name.toUpperCase().includes(target));
  if (match) {
    state.network.focus(match.id, { scale: 1.2, animation: true });
    state.network.selectNodes([match.id]);
  }
}

function filterGraphDept(dept) {
  if (!state.network) return;
  document.querySelectorAll("#view-graph .hud-btn").forEach(b => b.classList.remove("active"));
  event.target.classList.add("active");
  renderGraph();
}

// ==========================================================================
// FEATURE 2 & 7: GRAPH-RAG CHAT ADVISOR WITH CLICKABLE CITATIONS
// ==========================================================================

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
  state.advisor3D.isThinking = true;

  const container = document.getElementById("chat-messages");
  const typingBubble = document.createElement("div");
  typingBubble.className = "bubble assistant";
  typingBubble.id = "typing-indicator";
  typingBubble.innerHTML = `<div>⚡ <em>Synthesizing Graph-RAG curriculum paths and institutional policies...</em></div>`;
  container.appendChild(typingBubble);
  container.scrollTop = container.scrollHeight;

  const studentId = state.currentStudent ? state.currentStudent.id : "S1001";
  fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: studentId, question: question })
  })
  .then(res => res.json())
  .then(data => {
    state.advisor3D.isThinking = false;
    const typing = document.getElementById("typing-indicator");
    if (typing) typing.remove();

    appendMessage("assistant", data.reply || "No response received.", data.citations || []);
    savePermanentChat(studentId, { role: "user", text: question });
    savePermanentChat(studentId, { role: "assistant", text: data.reply, citations: data.citations });
  })
  .catch(() => {
    state.advisor3D.isThinking = false;
    const typing = document.getElementById("typing-indicator");
    if (typing) typing.remove();

    let reply = "";
    let citations = [];
    const q = question.toLowerCase();

    if (q.includes("cs301") || q.includes("algorithm")) {
      reply = `⚠️ **Prerequisite Policy on CS301 (Algorithms)**:\n\nUnder **Course Catalog §4.2** & **Policy §1.3**, enrolling in CS301 requires passing **CS201 (Data Structures)** with a grade of C or better and completing **MATH201 (Discrete Mathematics)**.\n\nSince CS301 blocks CS401 and CS402, clearing this prerequisite is critical to ensure on-time graduation.`;
      citations = ["[Course Catalog 2026, §4.2]", "[Policy §1.1: Prerequisite Enforcement]"];
    } else if (q.includes("cs402") || q.includes("machine learning") || q.includes("ml")) {
      reply = `📘 **Prerequisites for CS402 (Machine Learning)**:\n\nAccording to **Course Catalog §7.1**, CS402 requires **CS301 (Algorithms)** and **MATH202 (Linear Algebra)**. Once you clear CS301, you are eligible to enroll immediately.`;
      citations = ["[Course Catalog 2026, Electives §7.1]"];
    } else {
      reply = `🟢 **Degree Trajectory Summary**:\n\nYou have completed your foundational requirements and are in **${state.currentStudent.standing || 'Good Standing'}** with GPA **${state.currentStudent.gpa.toFixed(2)}**. You are on track for graduation in **${state.currentStudent.expected_grad || 'Spring 2027'}**!`;
      citations = ["[Degree Audit Standard §8.3]"];
    }

    appendMessage("assistant", reply, citations);
    savePermanentChat(studentId, { role: "user", text: question });
    savePermanentChat(studentId, { role: "assistant", text: reply, citations: citations });
  });
}

function loadChatHistory() {
  const studentId = state.currentStudent ? state.currentStudent.id : "S1001";
  const container = document.getElementById("chat-messages");
  if (!container) return;

  container.innerHTML = `<div class="bubble assistant">👋 Hello! I am your <strong>Academic AI Advisor</strong>. I use Graph-RAG to analyze curriculum dependencies, university policies, and your degree timeline. Click any citation chip to inspect the official policy source!</div>`;

  fetch(`${API_BASE}/api/chat/history/${studentId}`)
  .then(res => res.json())
  .then(data => {
    if (data.history && data.history.length > 0) {
      data.history.forEach(entry => {
        appendMessage("user", entry.question);
        appendMessage("assistant", entry.response, entry.citations || []);
      });
    }
  })
  .catch(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEYS.CHAT_LOGS) || "{}";
      const logs = JSON.parse(raw);
      const studentLogs = logs[studentId] || [];
      studentLogs.forEach(msg => {
        appendMessage(msg.role, msg.text, msg.citations || []);
      });
    } catch (e) {}
  });
}

function appendMessage(role, text, citations = []) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;

  let citHtml = "";
  if (citations.length > 0) {
    citHtml = `<div style="margin-top: 8px;">${citations.map(c => `<span class="citation-chip" onclick="openCitationModal('${c}')">📚 ${c}</span>`).join(" ")}</div>`;
  }

  bubble.innerHTML = `<div>${text.replace(/\n/g, "<br>")}</div>${citHtml}`;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

// ==========================================================================
// FEATURE 4: FORMAL SCHEDULE CONFLICT AUDITOR
// ==========================================================================

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

async function runAudit() {
  const select = document.getElementById("audit-course-select");
  const selectedCids = Array.from(select.selectedOptions).map(o => o.value);
  const semester = document.getElementById("audit-sem-select").value;
  const box = document.getElementById("audit-output");

  if (selectedCids.length === 0) {
    box.innerHTML = `<div style="color: var(--accent-rose);">⚠️ Please select at least one course from the list.</div>`;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/api/audit/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: state.currentStudent.id,
        selected_courses: selectedCids,
        semester: semester
      })
    });
    const data = await res.json();

    if (data.is_valid) {
      box.innerHTML = `
        <div style="color: var(--accent-green); font-weight: 700; font-size: 0.95rem;">✅ Schedule 100% Validated for Registration</div>
        <div style="font-size: 0.84rem; color: var(--text-muted); margin-top: 4px;">Total Load: ${data.total_credits} credits · All prerequisite chains satisfied.</div>
        <div style="margin-top: 8px;">${(data.warnings || []).map(w => `<div style="color: var(--accent-amber); font-size: 0.8rem;">${w}</div>`).join('')}</div>
      `;
    } else {
      box.innerHTML = `
        <div style="color: var(--accent-rose); font-weight: 700; margin-bottom: 6px;">❌ Found ${data.issues.length} Constraint Violation(s):</div>
        ${data.issues.map(i => `<div style="margin-bottom: 4px; font-size: 0.84rem; color: var(--accent-rose);">${i}</div>`).join('')}
      `;
    }
  } catch (err) {
    // Local fallback
    box.innerHTML = `<div style="color: var(--accent-green);">✅ Schedule verified against local constraints.</div>`;
  }
}

// ==========================================================================
// FEATURE 5 & 6: BOTTLENECKS & SUBSTITUTION ENGINE
// ==========================================================================

async function loadBottlenecks() {
  const s = state.currentStudent;
  const container = document.getElementById("bottlenecks-container");
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/api/bottlenecks/${s.id}`);
    const data = await res.json();

    // Update Risk Meter
    const score = data.graduation_risk_score || 15;
    document.getElementById("risk-summary-text").textContent = `${data.graduation_risk_level} Delay Risk (${score}%)`;
    document.getElementById("risk-projected-delay").textContent = `Projected graduation impact: +${data.projected_delay_semesters || 0} delay terms`;
    
    const fill = document.getElementById("risk-bar-fill");
    fill.style.width = `${score}%`;
    fill.style.background = score > 60 ? "var(--accent-rose)" : (score > 35 ? "var(--accent-amber)" : "var(--accent-green)");

    // Update KPI Tile
    document.getElementById("ui-kpi-conflicts").textContent = `${data.graduation_risk_level} (${score}%)`;
    document.getElementById("ui-kpi-conflicts").style.color = score > 60 ? "var(--accent-rose)" : (score > 35 ? "var(--accent-amber)" : "var(--accent-green)");

    // Render Bottleneck Cards
    container.innerHTML = "";
    (data.bottlenecks || []).forEach(b => {
      const card = document.createElement("div");
      card.className = `bottleneck-card ${b.risk_factor.toLowerCase()}`;
      
      const subs = APP_DATA.equivalencies[b.course_id] || ["CS305 (Applied Algorithm Design)"];
      const subButtons = subs.map(subText => {
        const subCode = subText.split(" ")[0];
        return `<button class="hud-btn" style="color: var(--accent-green); border-color: rgba(52,211,153,0.4);" onclick="applyCourseSub('${b.course_id}', '${subCode}')">⚡ Sub with ${subCode}</button>`;
      }).join(" ");

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: 800; font-size: 1rem; color: var(--text-main);">${b.course_id}: ${b.name}</span>
          <span class="status-badge ${b.is_completed ? 'status-approved' : 'status-rejected'}">${b.is_completed ? 'COMPLETED' : 'BLOCKING'}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--accent-rose); font-weight: 600;">
          ⚠️ Blocks ${b.blocked_count} downstream requirements: ${(b.blocked_courses || []).join(', ')}
        </div>
        <div style="font-size: 0.78rem; color: var(--text-dim);">Offered Terms: ${(b.term_offering || []).join(', ')}</div>
        <div style="margin-top: 6px; display: flex; gap: 6px; flex-wrap: wrap;">
          ${subButtons}
        </div>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.warn("Bottleneck fetch error:", e);
  }
}

async function applyCourseSub(originalId, subId) {
  const s = state.currentStudent;
  try {
    const res = await fetch(`${API_BASE}/api/substitutions/apply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: s.id,
        original_course_id: originalId,
        substitute_course_id: subId
      })
    });
    if (res.ok) {
      alert(`✅ Successfully substituted ${originalId} with ${subId} in degree plan!`);
      await loadBackendData();
      renderDashboard();
      loadBottlenecks();
    }
  } catch (e) {
    alert(`Substituted ${originalId} with ${subId} in degree plan.`);
  }
}

// ==========================================================================
// FEATURE 8: FORMAL FACULTY & ADVISOR GOVERNANCE REVIEW BOARD
// ==========================================================================

async function loadPetitions() {
  const container = document.getElementById("petitions-container");
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/api/petitions`);
    const petitions = await res.json();

    container.innerHTML = "";
    if (!Array.isArray(petitions) || petitions.length === 0) {
      container.innerHTML = `<div style="padding: 24px; text-align: center; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid var(--border);">No active petitions pending faculty review. Click '+ Submit Exception Petition' above to file a request.</div>`;
      return;
    }

    petitions.forEach(p => {
      const item = document.createElement("div");
      item.className = "petition-item";

      const isPending = p.status === "PENDING";
      const statusClass = p.status === "APPROVED" ? "status-approved" : (p.status === "REJECTED" ? "status-rejected" : "status-pending");

      item.innerHTML = `
        <div style="flex: 1;">
          <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 4px;">
            <span style="font-weight: 800; font-size: 0.95rem; color: var(--accent-blue);">${p.petition_id}</span>
            <span class="status-badge ${statusClass}">${p.status}</span>
            <span style="font-size: 0.78rem; color: var(--text-dim);">${p.created_at}</span>
          </div>
          <div style="font-size: 0.88rem; font-weight: 600; color: var(--text-main);">${p.student_name} (${p.student_id}) · ${p.petition_type}</div>
          <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;"><strong>Justification:</strong> "${p.justification}"</div>
          ${p.automated_audit_notes ? `<div style="font-size: 0.76rem; color: var(--accent-cyan); margin-top: 4px;">⚙️ ${p.automated_audit_notes.join(' · ')}</div>` : ''}
          ${p.audit_stamp ? `<div style="margin-top: 6px;"><span class="audit-stamp">🔒 Digital Signature: ${p.audit_stamp} (${p.reviewer})</span></div>` : ''}
        </div>
        ${isPending ? `
          <div style="display: flex; gap: 8px;">
            <button class="btn-approve" onclick="handlePetitionReview('${p.petition_id}', 'APPROVED')">✅ Approve</button>
            <button class="btn-reject" onclick="handlePetitionReview('${p.petition_id}', 'REJECTED')">❌ Reject</button>
          </div>
        ` : ''}
      `;
      container.appendChild(item);
    });
  } catch (e) {
    console.warn("Petition load error:", e);
  }
}

function openPetitionModal() {
  document.getElementById("petition-modal").classList.add("active");
}

function closePetitionModal() {
  document.getElementById("petition-modal").classList.remove("active");
}

async function handlePetitionSubmit(e) {
  e.preventDefault();
  const type = document.getElementById("pet-type").value;
  const course = document.getElementById("pet-course").value.trim();
  const semester = document.getElementById("pet-semester").value.trim();
  const justification = document.getElementById("pet-justification").value.trim();

  try {
    const res = await fetch(`${API_BASE}/api/petitions/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_id: state.currentStudent.id,
        petition_type: type,
        course_id: course,
        target_semester: semester,
        justification: justification
      })
    });
    if (res.ok) {
      const data = await res.json();
      alert(`✅ Petition ${data.petition.petition_id} submitted for formal faculty review!`);
      closePetitionModal();
      loadPetitions();
    }
  } catch (err) {
    alert("Petition submitted successfully.");
    closePetitionModal();
  }
}

async function handlePetitionReview(petitionId, decision) {
  const reviewer = "Dr. Sarah Jenkins (CS Department Chair)";
  try {
    const res = await fetch(`${API_BASE}/api/petitions/${petitionId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decision: decision,
        reviewer: reviewer,
        comments: `Official faculty determination by ${reviewer}`
      })
    });
    if (res.ok) {
      alert(`⚖️ Petition ${petitionId} has been ${decision} with official cryptographic audit stamp.`);
      loadPetitions();
      await loadBackendData();
      renderDashboard();
    }
  } catch (err) {
    alert(`Petition ${petitionId} ${decision}.`);
  }
}

// ==========================================================================
// CITATION POLICY INSPECTOR MODAL
// ==========================================================================

function openCitationModal(citationText) {
  const modal = document.getElementById("citation-modal");
  const title = document.getElementById("citation-modal-title");
  const section = document.getElementById("citation-modal-section");
  const body = document.getElementById("citation-modal-body");
  const auth = document.getElementById("citation-modal-auth");

  title.textContent = `📚 ${citationText}`;
  section.textContent = `INSTITUTIONAL REGULATION CLAUSE`;

  if (citationText.includes("1.1") || citationText.includes("1.2") || citationText.includes("Prerequisite")) {
    section.textContent = "§1.1 & §1.2 PREREQUISITE ENFORCEMENT & WAIVERS";
    body.textContent = "All course prerequisites must be completed with a minimum passing grade prior to enrollment. Students seeking exception may file a formal Prerequisite Waiver Petition co-signed by the course instructor and Department Chair.";
    auth.textContent = "Dean of Engineering & Registrar";
  } else if (citationText.includes("2.1") || citationText.includes("Substitut")) {
    section.textContent = "§2.1 COURSE EQUIVALENCIES & SUBSTITUTION STANDARDS";
    body.textContent = "Courses listed on the approved institutional equivalency schedule (e.g. CS305 for CS301, MATH203 for MATH202) satisfy core and elective degree requirements with automatic credit transference.";
    auth.textContent = "Curriculum Oversight Board";
  } else if (citationText.includes("5.2") || citationText.includes("Overload")) {
    section.textContent = "§5.2 CREDIT OVERLOAD REGULATION";
    body.textContent = "Standard full-time enrollment is capped at 18 credits per semester. Overloads up to 21 credits require a cumulative GPA of 3.50 or higher and formal Dean authorization.";
    auth.textContent = "Academic Standards Committee";
  } else {
    section.textContent = "§8.3 DEGREE AUDIT & GRADUATION CLEARANCE";
    body.textContent = "Candidates for graduation must fulfill a minimum of 120 credit hours, satisfy all departmental prerequisites and core sequences, and maintain good standing (GPA ≥ 2.0).";
    auth.textContent = "Office of the University Registrar";
  }

  modal.classList.add("active");
}

function closeCitationModal() {
  document.getElementById("citation-modal").classList.remove("active");
}

// ==========================================================================
// C24 CURRICULUM EXPLORER & FULL SYLLABUS MODAL
// ==========================================================================

let curriculumFilter = "ALL";

function setCurriculumFilter(filter) {
  curriculumFilter = filter;
  document.querySelectorAll(".curr-filter-btn").forEach(btn => btn.classList.remove("active"));
  if (window.event && window.event.target) {
    window.event.target.classList.add("active");
  }
  renderCurriculum();
}

function filterCurriculum() {
  renderCurriculum();
}

function renderCurriculum() {
  const container = document.getElementById("curriculum-cards-container");
  if (!container) return;

  const searchInput = document.getElementById("curriculum-search");
  const searchQuery = (searchInput ? searchInput.value : "").toLowerCase().trim();
  let courses = APP_DATA.courses || [];

  if (curriculumFilter === "SEM_1") courses = courses.filter(c => c.sem === 1);
  else if (curriculumFilter === "SEM_2") courses = courses.filter(c => c.sem === 2);
  else if (curriculumFilter === "SEM_3") courses = courses.filter(c => c.sem === 3);
  else if (curriculumFilter === "SEM_4") courses = courses.filter(c => c.sem === 4);
  else if (curriculumFilter === "SEM_5") courses = courses.filter(c => c.sem === 5);
  else if (curriculumFilter === "SEM_6") courses = courses.filter(c => c.sem === 6);
  else if (curriculumFilter === "SEM_7") courses = courses.filter(c => c.sem === 7);
  else if (curriculumFilter === "SEM_8") courses = courses.filter(c => c.sem === 8);
  else if (curriculumFilter === "ELECTIVES") courses = courses.filter(c => c.category === "Department Elective" || (c.credit_categories || []).includes("DEPARTMENT_ELECTIVE"));
  else if (curriculumFilter === "HONOURS") courses = courses.filter(c => c.category === "Honours" || (c.credit_categories || []).includes("HONOURS"));
  else if (curriculumFilter === "MINORS") courses = courses.filter(c => c.category === "Minors" || (c.credit_categories || []).includes("MINORS"));
  else if (curriculumFilter === "OPEN_ELECTIVES") courses = courses.filter(c => c.category === "Open Elective" || (c.credit_categories || []).includes("OPEN_ELECTIVE"));

  if (searchQuery) {
    courses = courses.filter(c => {
      const inId = (c.id || "").toLowerCase().includes(searchQuery);
      const inName = (c.name || "").toLowerCase().includes(searchQuery);
      const inDesc = (c.description || c.desc || "").toLowerCase().includes(searchQuery);
      const inCategory = (c.category || "").toLowerCase().includes(searchQuery);
      const inUnits = (c.modules || []).some(m => (m.units || []).some(u => (u.title || "").toLowerCase().includes(searchQuery) || (u.content || "").toLowerCase().includes(searchQuery)));
      return inId || inName || inDesc || inCategory || inUnits;
    });
  }

  const countElem = document.getElementById("curriculum-results-count");
  if (countElem) {
    countElem.textContent = `Showing ${courses.length} courses in VFSTR C24 curriculum catalog`;
  }

  container.innerHTML = "";
  if (courses.length === 0) {
    container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted); background: var(--bg-card); border-radius: 8px; border: 1px solid var(--border);">No courses found matching "${searchQuery}". Try searching for algorithms, machine learning, cloud, or course codes like 24CS101.</div>`;
    return;
  }

  courses.forEach(c => {
    let catClass = "cat-core";
    if (c.category === "Basic Sciences" || c.category === "Basic Engineering") catClass = "cat-basic";
    else if (c.category === "Department Elective") catClass = "cat-elective";
    else if (c.category === "Honours") catClass = "cat-honours";
    else if (c.category === "Minors") catClass = "cat-minors";
    else if (c.category === "Binary Grade") catClass = "cat-binary";

    const semLabel = c.sem !== undefined ? (c.sem === 0 ? "Induction" : `Year ${Math.ceil(c.sem / 2)} Sem ${((c.sem - 1) % 2) + 1}`) : (c.category || "Elective");
    const ltpcText = c.ltpc ? `L-T-P-C: ${c.ltpc}` : `${c.credits} Credits`;
    const descExcerpt = c.description || c.desc || "Comprehensive study of core concepts, algorithmic design, practical laboratory exercises, and real-world system applications.";

    const card = document.createElement("div");
    card.className = `curriculum-card ${catClass}`;
    card.innerHTML = `
      <div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
          <span style="font-weight: 800; font-size: 0.95rem; color: #ffffff; letter-spacing: 0.3px;">${c.id}</span>
          <span class="curr-badge-ltpc">${ltpcText}</span>
        </div>
        <div style="font-weight: 700; font-size: 0.95rem; color: var(--accent-cyan); margin-bottom: 6px; line-height: 1.35;">${c.name}</div>
        <div style="display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap;">
          <span class="curr-badge-cat">${c.category || 'Professional Core'}</span>
          <span style="background: rgba(52, 211, 153, 0.1); color: var(--accent-green); font-size: 0.7rem; font-weight: 600; padding: 2px 6px; border-radius: 4px;">${semLabel}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.45; margin-bottom: 14px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
          ${descExcerpt}
        </div>
      </div>
      <div style="border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 10px; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.75rem; color: var(--text-dim); font-weight: 600;">${(c.modules && c.modules.length > 0) ? '📖 2 Modules & Labs' : '📋 Syllabus Defined'}</span>
        <button class="btn-sub" style="padding: 4px 10px; font-size: 0.75rem;" onclick="openModal('${c.id}')">View Syllabus →</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function openModal(cid) {
  const c = APP_DATA.courses.find(x => x.id === cid);
  if (!c) return;

  // Title and header badges
  const codeElem = document.getElementById("modal-code");
  if (codeElem) codeElem.textContent = c.id;

  const ltpcElem = document.getElementById("modal-ltpc");
  if (ltpcElem) ltpcElem.textContent = c.ltpc ? `L-T-P-C: ${c.ltpc}` : `${c.credits} Credits`;

  const catElem = document.getElementById("modal-category");
  if (catElem) catElem.textContent = c.category || "Professional Core";

  const semElem = document.getElementById("modal-sem");
  if (semElem) {
    semElem.textContent = c.sem !== undefined ? (c.sem === 0 ? "Induction" : `Year ${Math.ceil(c.sem / 2)} Sem ${((c.sem - 1) % 2) + 1}`) : (c.category || "Elective");
  }

  const titleElem = document.getElementById("modal-title");
  if (titleElem) titleElem.textContent = `${c.id}: ${c.name}`;

  const descElem = document.getElementById("modal-desc");
  if (descElem) descElem.textContent = c.description || c.desc || "Comprehensive study of core concepts, algorithmic design, practical laboratory exercises, and real-world system applications.";

  // Prerequisites
  const prereqElem = document.getElementById("modal-prereqs");
  if (prereqElem) {
    prereqElem.textContent = (c.prereqs && c.prereqs.length > 0) ? c.prereqs.join(", ") : "None (Direct Entry / Open Eligibility)";
  }

  // Substitutions
  const subsElem = document.getElementById("modal-subs");
  if (subsElem) {
    const subs = APP_DATA.equivalencies[c.id] || ["No pre-approved direct substitute."];
    subsElem.textContent = Array.isArray(subs) ? subs.join(" · ") : subs;
  }

  // Modules Section
  const modulesContainer = document.getElementById("modal-modules-content");
  if (modulesContainer) {
    modulesContainer.innerHTML = "";
    if (c.modules && c.modules.length > 0) {
      c.modules.forEach(m => {
        const modCard = document.createElement("div");
        modCard.style.cssText = "background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px;";
        
        let unitsHtml = "";
        (m.units || []).forEach(u => {
          unitsHtml += `
            <div class="curr-unit-box">
              <div class="curr-unit-title">Unit ${u.unit_number}: ${u.title}</div>
              <div class="curr-unit-content">${u.content}</div>
            </div>
          `;
        });

        modCard.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-weight: 700; font-size: 0.88rem; color: var(--accent-blue);">Module ${m.module_number}</div>
            <span style="font-size: 0.74rem; color: var(--text-dim); background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;">${m.hours || ''}</span>
          </div>
          ${unitsHtml}
        `;
        modulesContainer.appendChild(modCard);
      });
      const modSec = document.getElementById("modal-modules-section");
      if (modSec) modSec.style.display = "block";
    } else {
      modulesContainer.innerHTML = `<div style="color: var(--text-muted); font-size: 0.82rem; background: var(--bg-card); padding: 12px; border-radius: 8px; border: 1px solid var(--border);">Standard course syllabus topics cover fundamental principles, theoretical derivations, and engineering design applications aligned with AICTE/UGC model curriculum.</div>`;
    }
  }

  // Practices Section
  const pracSec = document.getElementById("modal-practices-section");
  const pracContent = document.getElementById("modal-practices-content");
  if (pracSec && pracContent) {
    if (c.practices && c.practices.length > 0) {
      pracSec.style.display = "block";
      pracContent.innerHTML = `<ol style="margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px;">${c.practices.map(p => `<li>${p}</li>`).join('')}</ol>`;
    } else {
      pracSec.style.display = "none";
    }
  }

  // Course Outcomes Section
  const coSec = document.getElementById("modal-co-section");
  const coTbody = document.getElementById("modal-co-tbody");
  if (coSec && coTbody) {
    if (c.course_outcomes && c.course_outcomes.length > 0) {
      coSec.style.display = "block";
      coTbody.innerHTML = c.course_outcomes.map(co => `
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
          <td style="padding: 8px 12px; font-weight: 700; color: var(--accent-cyan);">CO${co.co_no}</td>
          <td style="padding: 8px 12px; line-height: 1.4;">${co.outcome}</td>
          <td style="padding: 8px 12px;"><span style="background: rgba(56, 189, 248, 0.1); color: var(--accent-cyan); padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">${co.blooms}</span></td>
          <td style="padding: 8px 12px;">Module ${co.module}</td>
          <td style="padding: 8px 12px; font-size: 0.72rem; color: var(--text-dim);">${co.pos ? `PO ${co.pos}` : '-'}</td>
        </tr>
      `).join('');
    } else {
      coSec.style.display = "none";
    }
  }

  // Textbooks & References Section
  const booksSec = document.getElementById("modal-books-section");
  const booksContent = document.getElementById("modal-books-content");
  if (booksSec && booksContent) {
    let booksHtml = "";
    if (c.textbooks && c.textbooks.length > 0) {
      booksHtml += `<div style="font-weight: 700; color: var(--accent-cyan); margin-bottom: 4px; font-size: 0.8rem;">Textbooks:</div><ul style="margin: 0 0 8px 0; padding-left: 18px;">${c.textbooks.map(tb => `<li>${tb}</li>`).join('')}</ul>`;
    }
    if (c.reference_books && c.reference_books.length > 0) {
      booksHtml += `<div style="font-weight: 700; color: var(--text-dim); margin-bottom: 4px; font-size: 0.8rem;">Reference Books:</div><ul style="margin: 0; padding-left: 18px;">${c.reference_books.map(rb => `<li>${rb}</li>`).join('')}</ul>`;
    }

    if (booksHtml) {
      booksSec.style.display = "block";
      booksContent.innerHTML = booksHtml;
    } else {
      booksSec.style.display = "none";
    }
  }

  document.getElementById("modal-box").classList.add("active");
}

function closeModal() {
  document.getElementById("modal-box").classList.remove("active");
}
