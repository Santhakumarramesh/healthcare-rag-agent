"""
UI Helper Components for Healthcare AI Platform.

Provides reusable styling and layout components.
"""
import streamlit as st


def inject_global_styles() -> None:
    """Inject global CSS styles for clinical SaaS theme."""
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        .mode-card {
            border: 1px solid #D9E2EC;
            border-radius: 18px;
            background: #FFFFFF;
            padding: 18px 18px 14px 18px;
            min-height: 180px;
            box-shadow: 0 6px 18px rgba(16, 42, 67, 0.05);
        }

        .mode-title {
            color: #102A43;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .mode-desc {
            color: #486581;
            font-size: 0.92rem;
            line-height: 1.45;
            margin-bottom: 0.8rem;
        }

        .hero-card {
            border: 1px solid #D9E2EC;
            border-radius: 20px;
            background: linear-gradient(180deg, #FFFFFF 0%, #F9FBFD 100%);
            padding: 28px 28px 22px 28px;
            box-shadow: 0 10px 24px rgba(16, 42, 67, 0.05);
            margin-bottom: 1rem;
        }

        .hero-title {
            color: #0F4C81;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            color: #486581;
            font-size: 1rem;
            line-height: 1.55;
        }

        .section-title {
            color: #102A43;
            font-size: 1.2rem;
            font-weight: 700;
            margin-top: 1.2rem;
            margin-bottom: 0.7rem;
        }

        .status-card {
            border: 1px solid #D9E2EC;
            border-radius: 16px;
            background: #FFFFFF;
            padding: 14px 16px;
            box-shadow: 0 4px 14px rgba(16, 42, 67, 0.04);
        }

        .metric-label {
            color: #7B8794;
            font-size: 0.84rem;
            margin-bottom: 0.2rem;
        }

        .metric-value {
            color: #102A43;
            font-size: 1.15rem;
            font-weight: 700;
        }

        .risk-banner-high {
            border: 1px solid #F5C2C7;
            background: #FDECEC;
            color: #842029;
            border-radius: 16px;
            padding: 14px 16px;
            font-weight: 600;
            margin-bottom: 0.9rem;
        }

        .risk-banner-medium {
            border: 1px solid #F6D7A7;
            background: #FFF4E5;
            color: #8A5A00;
            border-radius: 16px;
            padding: 14px 16px;
            font-weight: 600;
            margin-bottom: 0.9rem;
        }

        .risk-banner-low {
            border: 1px solid #C8E6D1;
            background: #E6F4EA;
            color: #1E7E34;
            border-radius: 16px;
            padding: 14px 16px;
            font-weight: 600;
            margin-bottom: 0.9rem;
        }

        .panel-card {
            border: 1px solid #D9E2EC;
            border-radius: 18px;
            background: #FFFFFF;
            padding: 18px;
            box-shadow: 0 6px 18px rgba(16, 42, 67, 0.05);
            margin-bottom: 1rem;
        }

        .mini-heading {
            color: #102A43;
            font-size: 0.98rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .subtle-text {
            color: #486581;
            font-size: 0.92rem;
            line-height: 1.45;
        }

        .timeline-item {
            border-left: 3px solid #2CB1BC;
            padding-left: 12px;
            margin-bottom: 14px;
        }

        .timeline-date {
            color: #7B8794;
            font-size: 0.82rem;
            margin-bottom: 2px;
        }

        .timeline-title {
            color: #102A43;
            font-size: 0.95rem;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .timeline-body {
            color: #486581;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str) -> None:
    """Render hero section with title and subtitle."""
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_card(label: str, value: str) -> None:
    """Render a status card with label and value."""
    st.markdown(
        f"""
        <div class="status-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel_open():
    """Open a panel card container."""
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)


def render_panel_close():
    """Close a panel card container."""
    st.markdown("</div>", unsafe_allow_html=True)


def render_risk_banner(level: str, message: str) -> None:
    """
    Render a risk alert banner.
    
    Args:
        level: Risk level (high, medium, low)
        message: Alert message
    """
    level = level.lower().strip()
    klass = "risk-banner-low"
    if level == "high":
        klass = "risk-banner-high"
    elif level == "medium":
        klass = "risk-banner-medium"

    st.markdown(
        f'<div class="{klass}">{message}</div>',
        unsafe_allow_html=True,
    )
