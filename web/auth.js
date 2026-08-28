/* Academic AI Advisor — authentication module
   Talks to the existing FastAPI endpoints and preserves the existing
   session keys / redirect targets that portal.js and the dashboard
   pages already depend on. */

(function () {
    'use strict';

    var state = { role: 'student', mode: 'login', submitting: false };

    var COPY = {
        student: {
            login: {
                visualEyebrow: 'AI-powered academic intelligence',
                visualHeading: 'Plan your degree with intelligence.',
                visualText: 'Understand your degree dependencies, protect your graduation timeline, and move forward with evidence \u2014 not guesswork.',
                eyebrow: 'Student workspace',
                title: 'Sign in to continue',
                copy: 'Sign in to view your personalised degree plan, credit progress, and academic signals.',
                submit: 'Sign in to Academic Advisor',
                foot: 'Student accounts are linked to your official C24 academic record.',
                switchCopy: "Don't have an account?",
                switchLabel: 'Create account'
            },
            signup: {
                visualEyebrow: 'AI-powered academic intelligence',
                visualHeading: 'Build your academic workspace.',
                visualText: 'Create your profile once and let the knowledge graph track prerequisites, risk, and your path to graduation from day one.',
                eyebrow: 'Student workspace',
                title: 'Create your academic workspace',
                copy: 'Build your personalised academic profile and start planning your degree with AI.',
                submit: 'Create student account',
                foot: 'Your profile is linked to your official C24 academic record.',
                switchCopy: 'Already have an account?',
                switchLabel: 'Sign in'
            }
        },
        faculty: {
            login: {
                visualEyebrow: 'Faculty governance',
                visualHeading: 'Review with confidence.',
                visualText: 'Access exception petitions, formal checks, and department-level academic decisions backed by full policy traceability.',
                eyebrow: 'Faculty governance',
                title: 'Review with confidence',
                copy: 'Access exception petitions, formal checks, and department-level academic decisions.',
                submit: 'Open faculty workspace',
                foot: 'Authorized reviewers can approve or reject exceptional cases.',
                switchCopy: '',
                switchLabel: ''
            }
        }
    };

    function studentLoginFields() {
        return [
            { id: 'identity', label: 'Student ID', type: 'text', placeholder: '241FA04077', autocomplete: 'username', help: 'The registration number printed on your college ID card.', required: true },
            { id: 'password', label: 'Password', type: 'password', placeholder: 'Enter your password', autocomplete: 'current-password', required: true, toggle: true }
        ];
    }

    function studentSignupFields() {
        return [
            { id: 'name', label: 'Full name', type: 'text', placeholder: 'Ananya Rao', autocomplete: 'name', required: true },
            { id: 'identity', label: 'Student ID', type: 'text', placeholder: '241FA04077', autocomplete: 'username', help: 'The registration number printed on your college ID card.', required: true },
            { id: 'major', label: 'Major / department', type: 'text', placeholder: 'Computer Science', autocomplete: 'off', required: true },
            { id: 'expected_grad', label: 'Expected graduation', type: 'text', placeholder: 'Spring 2027', autocomplete: 'off', required: true },
            { id: 'password', label: 'Password', type: 'password', placeholder: 'Create a password', autocomplete: 'new-password', required: true, toggle: true, strength: true },
            { id: 'confirm', label: 'Confirm password', type: 'password', placeholder: 'Re-enter your password', autocomplete: 'new-password', required: true, toggle: true }
        ];
    }

    function facultyLoginFields() {
        return [
            { id: 'identity', label: 'Faculty username', type: 'text', placeholder: 'admin / hod_cse / dean', autocomplete: 'username', help: 'Use your institutional faculty or department username.', required: true },
            { id: 'password', label: 'Password', type: 'password', placeholder: 'Enter your password', autocomplete: 'current-password', required: true, toggle: true }
        ];
    }

    function currentFields() {
        if (state.role === 'faculty') return facultyLoginFields();
        return state.mode === 'signup' ? studentSignupFields() : studentLoginFields();
    }

    function currentCopy() {
        return state.role === 'faculty' ? COPY.faculty.login : COPY.student[state.mode];
    }

    function el(id) { return document.getElementById(id); }

    function fieldMarkup(field) {
        var helpMarkup = field.help ? '<small class="field-help" id="' + field.id + '-help">' + field.help + '</small>' : '';
        var describedBy = field.help ? ' aria-describedby="' + field.id + '-help"' : '';
        var input = '<input id="' + field.id + '" name="' + field.id + '" type="' + field.type + '" placeholder="' + field.placeholder + '" autocomplete="' + field.autocomplete + '"' + (field.required ? ' required' : '') + describedBy + '>';

        if (field.type === 'password' && field.toggle) {
            input = '<div class="password-field">' + input +
                '<button type="button" class="pw-toggle" data-target="' + field.id + '" aria-label="Show password" aria-pressed="false">' +
                '<svg viewBox="0 0 24 24" class="eye-open" aria-hidden="true"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" fill="none" stroke="currentColor" stroke-width="1.6"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>' +
                '<svg viewBox="0 0 24 24" class="eye-closed" aria-hidden="true" hidden><path d="M3 3l18 18M10.6 10.7a3 3 0 0 0 4.2 4.2M6.6 6.7C3.9 8.4 1 12 1 12s4 7 11 7c1.8 0 3.4-.4 4.8-1.1M17.9 17.9C20.5 16.1 23 12 23 12s-1.7-3-4.6-5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>' +
                '</button></div>';
        }

        var strengthMarkup = field.strength ? '<div class="pw-strength" id="pw-strength" aria-hidden="true"><div class="pw-strength-track"><span></span></div><small id="pw-strength-label">&nbsp;</small></div>' : '';

        return '<label for="' + field.id + '">' +
            (field.id === 'password' ? '<span class="field-label-row"><span>' + field.label + '</span>' + (state.role === 'student' && state.mode === 'login' ? '<a href="mailto:support@academicadvisor.edu">Need help?</a>' : '<span></span>') + '</span>' : field.label) +
            input + strengthMarkup + helpMarkup +
            '<small class="field-error" id="' + field.id + '-error" role="alert"></small>' +
            '</label>';
    }

    function renderFields() {
        var stack = el('field-stack');
        stack.innerHTML = currentFields().map(fieldMarkup).join('');

        stack.querySelectorAll('.pw-toggle').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var input = el(btn.dataset.target);
                var showing = input.type === 'text';
                input.type = showing ? 'password' : 'text';
                btn.setAttribute('aria-pressed', String(!showing));
                btn.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
                btn.querySelector('.eye-open').hidden = !showing;
                btn.querySelector('.eye-closed').hidden = showing;
            });
        });

        var pwField = el('password');
        if (pwField && el('pw-strength')) {
            pwField.addEventListener('input', function () { updateStrength(pwField.value); });
        }
        var confirmField = el('confirm');
        if (confirmField) {
            confirmField.addEventListener('blur', function () { validateField('confirm'); });
        }
    }

    function updateStrength(password) {
        var track = document.querySelector('#pw-strength .pw-strength-track span');
        var label = el('pw-strength-label');
        if (!track || !label) return;

        if (!password) { track.style.width = '0%'; track.className = ''; label.textContent = '\u00a0'; return; }

        var score = 0;
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;

        var tier = score <= 1 ? 'weak' : score <= 3 ? 'medium' : 'strong';
        var text = { weak: 'Weak', medium: 'Medium', strong: 'Strong' }[tier];
        track.className = 'strength-' + tier;
        track.style.width = { weak: '33%', medium: '66%', strong: '100%' }[tier];
        label.textContent = text + ' password';
    }

    function fieldError(id, message) {
        var errorNode = el(id + '-error');
        var input = el(id);
        if (errorNode) errorNode.textContent = message || '';
        if (input) input.setAttribute('aria-invalid', message ? 'true' : 'false');
    }

    function validateField(id) {
        var input = el(id);
        if (!input) return true;
        var value = input.value.trim();

        if (input.hasAttribute('required') && !value) {
            var labels = {
                identity: state.role === 'faculty' ? 'Please enter your faculty username.' : 'Please enter your student ID.',
                password: 'Please enter your password.',
                name: 'Please enter your full name.',
                major: 'Please enter your major or department.',
                expected_grad: 'Please enter your expected graduation.',
                confirm: 'Please confirm your password.'
            };
            fieldError(id, labels[id] || 'This field is required.');
            return false;
        }

        if (id === 'confirm') {
            var pw = el('password');
            if (pw && value && value !== pw.value.trim()) {
                fieldError(id, 'Passwords do not match.');
                return false;
            }
        }

        fieldError(id, '');
        return true;
    }

    function validateForm() {
        var ids = currentFields().map(function (f) { return f.id; });
        var valid = true;
        ids.forEach(function (id) { if (!validateField(id)) valid = false; });
        return valid;
    }

    function showNotice(message, tone) {
        var node = el('message');
        node.textContent = message;
        node.className = 'notice' + (tone === 'good' ? ' good' : '');
        node.style.display = message ? 'block' : 'none';
    }

    function applyCopy() {
        var c = currentCopy();
        if (el('visual-eyebrow')) el('visual-eyebrow').textContent = c.visualEyebrow;
        if (el('visual-heading')) el('visual-heading').textContent = c.visualHeading;
        if (el('visual-text')) el('visual-text').textContent = c.visualText;
        if (el('form-eyebrow')) el('form-eyebrow').textContent = c.eyebrow;
        if (el('form-title')) el('form-title').textContent = c.title;
        if (el('form-copy')) el('form-copy').textContent = c.copy;
        if (el('submit-label')) el('submit-label').textContent = c.submit;
        if (el('login-foot')) el('login-foot').textContent = c.foot;

        var switchWrap = el('auth-switch');
        if (state.role === 'faculty') {
            switchWrap.style.display = 'none';
        } else {
            switchWrap.style.display = '';
            el('switch-copy').textContent = c.switchCopy;
            el('switch-btn').textContent = c.switchLabel;
        }

        el('mode-switch').style.display = state.role === 'faculty' ? 'none' : 'grid';
        document.querySelectorAll('.mode-btn').forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.mode === state.mode);
        });
    }

    function render(withTransition) {
        var card = el('auth-card');
        if (!withTransition) {
            applyCopy();
            renderFields();
            showNotice('');
            return;
        }
        card.classList.add('card-fade');
        window.setTimeout(function () {
            applyCopy();
            renderFields();
            showNotice('');
            card.classList.remove('card-fade');
        }, 180);
    }

    function pulseCore() {
        var core = el('orbit-core');
        if (!core) return;
        core.classList.remove('core-pulse');
        // eslint-disable-next-line no-unused-expressions
        core.offsetWidth; // force reflow so the animation can restart
        core.classList.add('core-pulse');
    }

    function setRole(role) {
        if (state.role === role) return;
        state.role = role;
        if (role === 'faculty') state.mode = 'login';
        document.querySelectorAll('.role-btn').forEach(function (btn) {
            var selected = btn.dataset.role === role;
            btn.classList.toggle('active', selected);
            btn.setAttribute('aria-selected', String(selected));
        });
        render(true);
    }

    function setMode(mode) {
        if (state.mode === mode || state.role === 'faculty') return;
        state.mode = mode;
        render(true);
    }

    function friendlyError(message) {
        var known = {
            'Student ID not found.': 'We couldn\u2019t find that student ID. Check the number and try again.',
            'Incorrect password.': 'That password doesn\u2019t match our records.',
            'Student ID already registered.': 'This student ID is already registered. Please sign in instead.'
        };
        return known[message] || message || 'Something went wrong. Please try again.';
    }

    function setSubmitting(isSubmitting, label) {
        state.submitting = isSubmitting;
        var button = document.querySelector('.login-submit');
        button.disabled = isSubmitting;
        button.classList.toggle('is-loading', isSubmitting);
        el('submit-label').textContent = isSubmitting ? label : currentCopy().submit;
    }

    async function handleSubmit(event) {
        event.preventDefault();
        if (state.submitting) return;
        if (!validateForm()) return;

        showNotice('');
        pulseCore();

        var loadingLabel = state.role === 'faculty' ? 'Opening workspace\u2026'
            : state.mode === 'signup' ? 'Creating account\u2026' : 'Signing in\u2026';
        setSubmitting(true, loadingLabel);

        try {
            var endpoint, payload;

            if (state.role === 'faculty') {
                endpoint = '/api/admin/login';
                payload = { username: el('identity').value.trim(), password: el('password').value.trim() };
            } else if (state.mode === 'signup') {
                endpoint = '/api/auth/signup';
                payload = {
                    name: el('name').value.trim(),
                    regno: el('identity').value.trim(),
                    major: el('major').value.trim(),
                    expected_grad: el('expected_grad').value.trim(),
                    password: el('password').value.trim()
                };
            } else {
                endpoint = '/api/auth/login';
                payload = { regno: el('identity').value.trim(), password: el('password').value.trim() };
            }

            var response = await fetch('http://127.0.0.1:8000' + endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            var data = await response.json().catch(function () { return {}; });

            if (!response.ok) {
                throw new Error(data.detail || 'Unable to sign in');
            }

            if (state.role === 'faculty') {
                localStorage.setItem('academic_advisor_faculty_session', 'active');
                showNotice('Welcome back. Opening your workspace\u2026', 'good');
                window.setTimeout(function () { location.href = 'governance.html?faculty=1'; }, 450);
                return;
            }

            var studentId = data.student && data.student.id ? data.student.id : payload.regno;
            localStorage.setItem('academic_advisor_permanent_active_user_v3', studentId);

            if (state.mode === 'signup') {
                showNotice('Account created. Setting up your workspace\u2026', 'good');
            } else {
                showNotice('Signed in. Loading your workspace\u2026', 'good');
            }
            window.setTimeout(function () { location.href = 'home.html'; }, 450);
        } catch (error) {
            setSubmitting(false, '');
            showNotice(friendlyError(error.message));
        }
    }

    function init() {
        document.querySelectorAll('.role-btn').forEach(function (btn) {
            btn.addEventListener('click', function () { setRole(btn.dataset.role); });
        });
        document.querySelectorAll('.mode-btn').forEach(function (btn) {
            btn.addEventListener('click', function () { setMode(btn.dataset.mode); });
        });
        el('auth-form').addEventListener('submit', handleSubmit);
        el('switch-btn').addEventListener('click', function () {
            setMode(state.mode === 'login' ? 'signup' : 'login');
        });

        render(false);
    }

    document.addEventListener('DOMContentLoaded', init);
})();