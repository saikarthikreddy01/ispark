
    let studentId = null;
    let academicHistory = [];
    let careerGoals = [];

    async function loadProfile() {
      const student = await initShell('profile');
      if (!student) return;
      studentId = student.id;
      academicHistory = student.academic_history || [];
      careerGoals = student.career_goals || [];
      document.getElementById('career-goals-input').value = careerGoals.join(', ');
      renderSemesters();
    }

    function renderSemesters() {
      const container = document.getElementById('semesters-container');
      container.innerHTML = '';
      
      academicHistory.forEach((sem, sIndex) => {
        const block = document.createElement('div');
        block.className = 'semester-block';
        
        const header = document.createElement('div');
        header.className = 'semester-header';
        header.innerHTML = `
          <h3><input type="text" value="${esc(sem.title || \`Year \${Math.floor(sIndex/2)+1} Sem \${(sIndex%2)+1}\`)}" onchange="updateSemTitle(${sIndex}, this.value)" style="border:none; font-weight:600; font-size:16px; width:200px; background:transparent;"></h3>
          <button type="button" class="remove-btn" onclick="removeSemester(${sIndex})">Remove Semester</button>
        `;
        block.appendChild(header);

        if (sem.courses && sem.courses.length > 0) {
          const labels = document.createElement('div');
          labels.className = 'header-labels';
          labels.style.gridTemplateColumns = '2fr 3fr 1fr 1fr 1fr auto';
          labels.innerHTML = `<div>Course Code</div><div>Course Name</div><div>Grade</div><div>GPA (0-10)</div><div>Credits</div><div></div>`;
          block.appendChild(labels);
        }

        const coursesDiv = document.createElement('div');
        (sem.courses || []).forEach((course, cIndex) => {
          const row = document.createElement('div');
          row.className = 'subject-row';
          row.style.gridTemplateColumns = '2fr 3fr 1fr 1fr 1fr auto';
          
          let displayGpa = course.gpa !== undefined && course.gpa !== null && course.gpa !== '' ? esc(course.gpa) + ' / 10' : '';
          
          row.innerHTML = `
            <input type="text" placeholder="e.g. 24CS101" value="${esc(course.code || '')}" onchange="updateCourse(${sIndex}, ${cIndex}, 'code', this.value)" required>
            <input type="text" placeholder="e.g. Programming" value="${esc(course.name || '')}" onchange="updateCourse(${sIndex}, ${cIndex}, 'name', this.value)" required>
            <input type="text" placeholder="e.g. A+" value="${esc(course.grade || '')}" onchange="updateCourse(${sIndex}, ${cIndex}, 'grade', this.value.trim().toUpperCase())" required>
            <input type="number" step="0.01" min="0" max="10" placeholder="0.00-10.00" value="${esc(course.gpa || '')}" onchange="updateCourse(${sIndex}, ${cIndex}, 'gpa', this.value)" required title="Subject GPA / Grade Points (0-10)">
            <input type="number" placeholder="Credits" value="${esc(course.credits || '')}" onchange="updateCourse(${sIndex}, ${cIndex}, 'credits', this.value)" required>
            <button type="button" class="remove-btn" onclick="removeCourse(${sIndex}, ${cIndex})">&times;</button>
          `;
          coursesDiv.appendChild(row);
        });
        block.appendChild(coursesDiv);

        const addBtn = document.createElement('button');
        addBtn.className = 'add-subject-btn';
        addBtn.type = 'button';
        addBtn.textContent = '+ Add Subject';
        addBtn.onclick = () => addCourse(sIndex);
        block.appendChild(addBtn);

        container.appendChild(block);
      });
    }

    window.updateSemTitle = (sIndex, val) => { academicHistory[sIndex].title = val; };
    window.updateCourse = (sIndex, cIndex, field, val) => { academicHistory[sIndex].courses[cIndex][field] = val; };
    
    window.addSemester = () => {
      academicHistory.push({ title: `Year ${Math.floor(academicHistory.length/2)+1} Sem ${(academicHistory.length%2)+1}`, courses: [] });
      renderSemesters();
    };
    
    window.removeSemester = (sIndex) => {
      academicHistory.splice(sIndex, 1);
      renderSemesters();
    };

    window.addCourse = (sIndex) => {
      if (!academicHistory[sIndex].courses) academicHistory[sIndex].courses = [];
      academicHistory[sIndex].courses.push({ code: '', name: '', grade: '', gpa: '', credits: '' });
      renderSemesters();
    };

    window.removeCourse = (sIndex, cIndex) => {
      academicHistory[sIndex].courses.splice(cIndex, 1);
      renderSemesters();
    };

    document.getElementById('add-sem-btn').onclick = addSemester;

    document.getElementById('profile-form').onsubmit = async (e) => {
      e.preventDefault();
      const btn = document.getElementById('save-btn');
      
      const goalsText = document.getElementById('career-goals-input').value;
      const goalsArray = goalsText.split(',').map(g => g.trim()).filter(g => g.length > 0);
      
      btn.textContent = 'Saving...';
      btn.disabled = true;
      try {
        await api(`/api/student/${encodeURIComponent(studentId)}/profile`, {
          method: 'PUT',
          body: JSON.stringify({ academic_history: academicHistory, career_goals: goalsArray })
        });
        toast('Profile saved successfully!');
      } catch (err) {
        toast('Error saving profile: ' + err.message);
      }
      btn.textContent = 'Save Profile';
      btn.disabled = false;
    };

    document.addEventListener('DOMContentLoaded', loadProfile);
  