import streamlit as st
from services.llm_service import generate_email

# Classic Minimalist Theme Styling
st.set_page_config(page_title="Mail Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #2563eb; color: white; border: none; padding: 10px; font-weight: 600; }
    .stTextArea textarea { border-radius: 8px; border: 1px solid #e2e8f0; }
    .sidebar .sidebar-content { background-color: #ffffff; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; font-weight: 700; color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

st.title("🏛 Mail Strategy Lab")
st.caption("Refining the AI Outreach Persona for Automated Hunts")

# ── Sidebar: Candidate & Job Seeds ─────────────────────────────────────────
with st.sidebar:
    st.header("👤 Candidate Seed")
    name = st.text_input("Full Name", "Tanisha Pritha")
    current_role = st.text_input("Current Position", "Junior Backend Developer")
    exp_years = st.slider("Years of Experience", 0.0, 15.0, 2.5)
    skills = st.text_area("Skills (Semicolon separated)", "Python; FastAPI; SQLite; Next.js; AI Prompt Engineering")
    target_role = st.text_input("Target Position", "Senior Backend Engineer")
    
    st.divider()
    
    st.header("💼 Job Context Seed")
    job_title = st.text_input("Job Title", "Python Backend Developer")
    company = st.text_input("Company", "TechStream Systems")
    description = st.text_area("Job Description", "We are looking for a Python developer experienced in building high-performance APIs using FastAPI. Strong SQL and cloud knowledge required.")

# ── Main Workspace ─────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🖋 Prompt Blueprint")
    st.info("System instruction transparency.")
    
    # Exposing the internal prompt logic
    system_prompt = f"Tone: Professional. Mapping '{skills}' -> '{job_title}'."
    user_prompt = f"Action: Pitch {name} to {company} for {job_title}."
    
    st.code(f"{system_prompt}\n\n{user_prompt}", language="markdown")
    
    if st.button("Generate Strategy Preview"):
        with st.spinner("Refining draft..."):
            # Mocking the object structure for internal service
            class Mock: pass
            u = Mock()
            u.name = name
            u.skills = [s.strip() for s in skills.split(";")]
            u.target_role = target_role
            u.current_role = current_role
            u.experience_years = exp_years
            u.email_tone = "Professional"
            
            j = Mock()
            j.title = job_title
            j.company = company
            j.description = description
            
            output = generate_email(u, j)
            st.session_state.last_mail = output
            st.success("Draft Analysis Complete")

with col2:
    st.subheader("✉️ Outreach Preview")
    if "last_mail" in st.session_state:
        st.markdown(f"***")
        st.markdown(st.session_state.last_mail)
        st.markdown(f"***")
        
        st.caption("Verification Checklist:")
        st.checkbox("Icon-free classic text", value=True)
        st.checkbox("Overlaps are highlighted", value=True)
    else:
        st.warning("Awaiting generation launch...")

st.divider()
st.caption("Mail Strategy Lab v1.1 | Standardized for Strategic Deployment")
