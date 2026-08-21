import streamlit as st

def inject_custom_css():
    """Injects a minimal, academic, and professional Blue & Emerald Green design system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

        /* Global Typography */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Academic Gradient Accents */
        .gradient-text {
            background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            display: inline-block;
        }

        .gradient-text-blue {
            background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        /* Glassmorphism Academic Cards */
        .glass-card {
            background: rgba(30, 41, 59, 0.65);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            transition: all 0.25s ease;
        }

        .glass-card:hover {
            border-color: rgba(59, 130, 246, 0.4);
            box-shadow: 0 14px 30px -8px rgba(37, 99, 235, 0.25);
        }

        .glass-card-compact {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 10px;
        }

        /* KPI Metric Containers */
        .kpi-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 14px;
            position: relative;
            overflow: hidden;
        }

        .kpi-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, #2563eb 0%, #10b981 100%);
        }

        .kpi-title {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #94a3b8;
            margin-bottom: 4px;
            font-weight: 600;
        }

        .kpi-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.2;
        }

        .kpi-delta {
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-weight: 600;
            margin-top: 5px;
        }

        .delta-success {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .delta-warning {
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .delta-danger {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .delta-info {
            background: rgba(59, 130, 246, 0.15);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        /* Status Badges */
        .status-badge {
            display: inline-block;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .badge-completed {
            background: rgba(16, 185, 129, 0.18);
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .badge-available {
            background: rgba(59, 130, 246, 0.18);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.4);
        }

        .badge-locked {
            background: rgba(239, 68, 68, 0.18);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        .badge-progress {
            background: rgba(245, 158, 11, 0.18);
            color: #fde68a;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }

        /* Navigation Feature Cards */
        .nav-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 20px;
            height: 100%;
            transition: all 0.25s ease;
        }

        .nav-card:hover {
            border-color: rgba(59, 130, 246, 0.5);
            transform: translateY(-3px);
            box-shadow: 0 12px 24px -6px rgba(37, 99, 235, 0.3);
        }

        .nav-card-icon {
            font-size: 1.9rem;
            margin-bottom: 10px;
        }

        .nav-card-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 6px;
        }

        .nav-card-desc {
            font-size: 0.84rem;
            color: #94a3b8;
            line-height: 1.45;
            margin-bottom: 12px;
        }

        /* Streamlit Button Tweaks */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.45rem 1.15rem;
            transition: all 0.2s ease;
        }

        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb 0%, #059669 100%);
            border: none;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        }

        .stButton>button[kind="primary"]:hover {
            background: linear-gradient(135deg, #1d4ed8 0%, #047857 100%);
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.55);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070a13 0%, #0f172a 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }

        /* Progress Bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #2563eb 0%, #10b981 100%);
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_hero_banner(title: str, subtitle: str, badge_text: str = "⚡ Academic Pathway Advisor"):
    """Renders a clean, professional top banner."""
    st.markdown(
        f"""
        <div style="margin-bottom: 24px; padding-bottom: 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="display: inline-block; padding: 3px 12px; border-radius: 9999px; background: rgba(37, 99, 235, 0.15); border: 1px solid rgba(37, 99, 235, 0.35); color: #93c5fd; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 8px;">
                {badge_text}
            </div>
            <h1 style="font-size: 2.1rem; font-weight: 800; color: #f8fafc; margin: 0 0 6px 0; letter-spacing: -0.02em;">
                {title}
            </h1>
            <p style="font-size: 0.98rem; color: #94a3b8; margin: 0; line-height: 1.45;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_kpi_card(title: str, value: str, delta: str = "", delta_type: str = "success", icon: str = "📊"):
    """Renders a custom academic KPI tile."""
    delta_html = ""
    if delta:
        delta_html = f'<div class="kpi-delta delta-{delta_type}">{delta}</div>'
    
    st.markdown(
        f"""
        <div class="kpi-container">
            <div>
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                {delta_html}
            </div>
            <div style="font-size: 2rem; opacity: 0.9;">{icon}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar_student(student):
    """Renders a student profile card in the sidebar."""
    if not student:
        return
    pct = min(student.total_credits_earned / 120.0, 1.0)
    gpa_status = "Good Standing" if student.gpa >= 2.0 else "Probation Risk"
    gpa_color = "#34d399" if student.gpa >= 2.0 else "#f87171"
    minor_text = getattr(student, "minor", "Mathematics")
    expected_grad = getattr(student, "expected_graduation", "Spring 2026")

    st.sidebar.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px; margin-top: 8px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #2563eb 0%, #10b981 100%); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700; color: white;">
                    {student.name[0]}
                </div>
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{student.name}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">Major: {student.major}</div>
                    <div style="font-size: 0.72rem; color: #64748b;">Minor: {minor_text}</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 10px;">
                <div style="background: rgba(15, 23, 42, 0.6); padding: 6px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 0.68rem; color: #94a3b8; text-transform: uppercase;">GPA</div>
                    <div style="font-size: 1rem; font-weight: 700; color: {gpa_color};">{student.gpa:.2f}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 6px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 0.68rem; color: #94a3b8; text-transform: uppercase;">Expected Grad</div>
                    <div style="font-size: 0.85rem; font-weight: 700; color: #93c5fd;">{expected_grad}</div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: #94a3b8; margin-bottom: 4px;">
                <span>Degree Progress</span>
                <span style="font-weight: 700; color: #f8fafc;">{student.total_credits_earned}/120 cr ({int(pct*100)}%)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.progress(pct)

def render_help_tip(title: str, explanation: str, icon: str = "💡"):
    """Renders a concept explanation box."""
    st.markdown(
        f"""
        <div style="background: rgba(37, 99, 235, 0.08); border-left: 4px solid #2563eb; border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 10px 0;">
            <div style="font-weight: 700; color: #93c5fd; font-size: 0.88rem; margin-bottom: 2px;">{icon} {title}</div>
            <div style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.4;">{explanation}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_guide_box(steps: list[tuple[str, str, str]], title: str = "💡 Quick Start Guide for Students"):
    """Renders a friendly 3-step beginner guide."""
    step_items = ""
    for num, heading, desc in steps:
        step_items += f"""
        <div style="display: flex; gap: 12px; align-items: flex-start; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 12px; margin-bottom: 6px;">
            <div style="min-width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #2563eb 0%, #10b981 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.88rem; color: white;">
                {num}
            </div>
            <div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.9rem; margin-bottom: 1px;">{heading}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; line-height: 1.35;">{desc}</div>
            </div>
        </div>
        """
        
    st.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(37, 99, 235, 0.2); border-radius: 14px; padding: 16px; margin-bottom: 18px;">
            <div style="font-weight: 700; color: #93c5fd; font-size: 0.95rem; margin-bottom: 10px;">
                {title}
            </div>
            {step_items}
        </div>
        """,
        unsafe_allow_html=True
    )
