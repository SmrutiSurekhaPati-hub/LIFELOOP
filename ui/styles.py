import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>

        /* =========================================
           GLOBAL
        ========================================= */

        .stApp {
            background: linear-gradient(
                135deg,
                #f8fafc 0%,
                #eef2ff 50%,
                #f8fafc 100%
            );
        }

        .main .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* =========================================
           HEADINGS
        ========================================= */

        h1 {
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            letter-spacing: -1px;
        }

        h2 {
            font-weight: 750 !important;
        }

        h3 {
            font-weight: 700 !important;
        }

        /* =========================================
           METRIC CARDS
        ========================================= */

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
        }

        div[data-testid="stMetricLabel"] {
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            font-weight: 800;
        }

        /* =========================================
           BUTTONS
        ========================================= */

        .stButton > button {
            border-radius: 10px;
            border: 1px solid rgba(99, 102, 241, 0.25);
            font-weight: 650;
            min-height: 42px;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 14px rgba(15, 23, 42, 0.12);
        }

        /* =========================================
           INPUTS
        ========================================= */

        div[data-baseweb="input"],
        div[data-baseweb="select"] {
            border-radius: 10px;
        }

        /* =========================================
           ALERT / INFO BOXES
        ========================================= */

        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* =========================================
           EXPANDERS
        ========================================= */

        div[data-testid="stExpander"] {
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.25);
            overflow: hidden;
        }

        /* =========================================
           SIDEBAR
        ========================================= */

        section[data-testid="stSidebar"] {
            background: rgba(248, 250, 252, 0.96);
            border-right: 1px solid rgba(148, 163, 184, 0.2);
        }

        section[data-testid="stSidebar"] h2 {
            font-size: 1.15rem !important;
        }

        /* =========================================
           CUSTOM HERO
        ========================================= */

        .lifeloop-hero {
            padding: 28px 30px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(99, 102, 241, 0.15);
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.07);
            margin-bottom: 24px;
        }

        .lifeloop-hero-title {
            font-size: 2.25rem;
            font-weight: 850;
            margin-bottom: 6px;
        }

        .lifeloop-hero-subtitle {
            font-size: 1.05rem;
            color: #475569;
            line-height: 1.6;
        }

        /* =========================================
           DECISION CARD
        ========================================= */

        .decision-card {
            padding: 24px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(34, 197, 94, 0.2);
            box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
            margin: 12px 0 20px 0;
        }

        .decision-label {
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .decision-title {
            font-size: 1.35rem;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .decision-reason {
            color: #475569;
            line-height: 1.6;
        }

        /* =========================================
           SECTION CARDS
        ========================================= */

        .section-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 18px;
        }

        /* =========================================
           STATUS BADGES
        ========================================= */

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 750;
            margin-right: 5px;
        }

        .badge-critical {
            background: #fee2e2;
            color: #991b1b;
        }

        .badge-high {
            background: #ffedd5;
            color: #9a3412;
        }

        .badge-medium {
            background: #fef9c3;
            color: #854d0e;
        }

        /* =========================================
           FOOTER
        ========================================= */

        .lifeloop-footer {
            text-align: center;
            padding: 28px 10px 10px 10px;
            color: #64748b;
            font-size: 0.9rem;
        }

        </style>
        """,
        unsafe_allow_html=True
    )