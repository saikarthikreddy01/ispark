import streamlit as st

def inject_custom_css():
    """Injects a modern, glassmorphic dark-indigo design system."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

        /* Global Typography & Background */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Gradient Text Utilities */
        .gradient-text {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            display: inline-block;
        }

        .gradient-text-blue {
            background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        .gradient-text-emerald {
            background: linear-gradient(135deg, #34d399 0%, #059669 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(30, 41, 59, 0.65);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card:hover {
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 20px 40px -15px rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }

        .glass-card-compact {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }

        /* KPI Metric Cards */
        .kpi-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid rgba(99, 102, 241, 0.15);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 15px;
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
            background: linear-gradient(180deg, #6366f1 0%, #a855f7 100%);
        }

        .kpi-title {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #94a3b8;
            margin-bottom: 4px;
            font-weight: 600;
        }

        .kpi-value {
            font-size: 1.75rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.2;
        }

        .kpi-delta {
            font-size: 0.78rem;
            padding: 3px 8px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-weight: 600;
            margin-top: 6px;
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
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        /* Status Badges */
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .badge-core {
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.4);
        }

        .badge-prereq-met {
            background: rgba(16, 185, 129, 0.18);
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .badge-bottleneck {
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        .badge-elective {
            background: rgba(168, 85, 247, 0.2);
            color: #d8b4fe;
            border: 1px solid rgba(168, 85, 247, 0.4);
        }

        /* Navigation Feature Cards */
        .nav-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            height: 100%;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .nav-card:hover {
            border-color: rgba(168, 85, 247, 0.5);
            transform: translateY(-4px);
            box-shadow: 0 16px 32px -8px rgba(168, 85, 247, 0.25);
        }

        .nav-card-icon {
            font-size: 2.2rem;
            margin-bottom: 12px;
            display: inline-block;
        }

        .nav-card-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 8px;
        }

        .nav-card-desc {
            font-size: 0.88rem;
            color: #94a3b8;
            line-height: 1.5;
            margin-bottom: 16px;
        }

        /* Streamlit UI Overrides */
        .stButton>button {
            border-radius: 12px;
            font-weight: 600;
            padding: 0.5rem 1.25rem;
            transition: all 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        /* Primary Button Glow */
        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border: none;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
        }

        .stButton>button[kind="primary"]:hover {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b0f19 0%, #0f172a 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }

        /* Progress Bar Styling */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            border-radius: 10px;
        }

        /* Chat Message Styling */
        [data-testid="stChatMessage"] {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_hero_banner(title: str, subtitle: str, badge_text: str = "⚡ Graph-RAG & Gemini 3.6 Flash"):
    """Renders a sleek top hero banner with badge and gradient title."""
    st.markdown(
        f"""
        <div style="margin-bottom: 28px; padding-bottom: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="display: inline-block; padding: 4px 14px; border-radius: 9999px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); color: #818cf8; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 12px;">
                {badge_text}
            </div>
            <h1 style="font-size: 2.3rem; font-weight: 800; color: #f8fafc; margin: 0 0 8px 0; letter-spacing: -0.02em;">
                {title}
            </h1>
            <p style="font-size: 1.05rem; color: #94a3b8; margin: 0; line-height: 1.5;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_kpi_card(title: str, value: str, delta: str = "", delta_type: str = "success", icon: str = "📊"):
    """Renders a custom glassmorphic KPI tile."""
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
            <div style="font-size: 2.2rem; opacity: 0.85;">{icon}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar_student(student):
    """Renders a rich student profile card in the sidebar."""
    if not student:
        return
    pct = min(student.total_credits_earned / 120.0, 1.0)
    gpa_status = "Good Standing" if student.gpa >= 2.0 else "Probation Risk"
    gpa_color = "#34d399" if student.gpa >= 2.0 else "#f87171"

    st.sidebar.markdown(
        f"""
        <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 16px; margin-top: 10px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); display: flex; align-items: center; justify-content: center; font-size: 1.3rem; font-weight: 700; color: white;">
                    {student.name[0]}
                </div>
                <div>
                    <div style="font-weight: 700; color: #f8fafc; font-size: 1rem;">{student.name}</div>
                    <div style="font-size: 0.78rem; color: #94a3b8;">{student.major}</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">GPA</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: {gpa_color};">{student.gpa:.2f}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 0.7rem; color: #94a3b8; text-transform: uppercase;">Standing</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #818cf8;">Year {student.current_year}</div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: #94a3b8; margin-bottom: 4px;">
                <span>Degree Progress</span>
                <span style="font-weight: 700; color: #f8fafc;">{student.total_credits_earned}/120 cr ({int(pct*100)}%)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.progress(pct)
