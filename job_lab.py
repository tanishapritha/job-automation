import streamlit as st
import requests
import pandas as pd

# Classic Minimalist Theme
st.set_page_config(page_title="Job Strategy Lab", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1, h2, h3 { font-family: 'Playfair Display', serif; color: #1e293b; }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏛 Job Strategy Lab")
st.caption("Simulator for Multi-Platform Scraper Testing")

# ── Sidebar: Search Parameters ─────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Search Parameters")
    query = st.text_input("Keywords (separate with ;)", "Python Backend; FastAPI")
    location = st.text_input("Locations", "London, UK; Remote")
    
    st.divider()
    
    results = st.slider("Max Results per Platform", 1, 30, 10)
    exp_level = st.selectbox("Experience Level", ["beginner", "mid", "senior"], index=1)
    remote_pref = st.radio("Remote Preference", ["hybrid", "remote", "onsite"], index=0)
    salary_min = st.number_input("Minimum Salary (₹/Year)", value=1000000, step=100000)

# ── Main Workspace ─────────────────────────────────────────────────────────
if st.button("Launch Multi-Platform Hunt"):
    with st.spinner("Scraping LinkedIn, Indeed, and Naukri..."):
        payload = {
            "query": query.replace(";", ","),
            "location": location.replace(";", ","),
            "results": results,
            "experience_level": exp_level,
            "remote_preference": remote_pref,
            "salary_min": salary_min
        }
        
        try:
            response = requests.post("http://localhost:8000/jobs/search", json=payload)
            if response.status_code == 200:
                jobs = response.json()
                
                if not jobs:
                    st.warning("No jobs found with these parameters in the last 48 hours.")
                else:
                    st.success(f"Found {len(jobs)} unique opportunities.")
                    
                    # Convert to DataFrame for a clean table view
                    df = pd.DataFrame(jobs)
                    # Cleaning up columns for display
                    display_df = df[['title', 'company', 'location', 'source', 'apply_url']]
                    st.table(display_df)
                    
                    # Interactive JSON view
                    with st.expander("View Raw JSON Response"):
                        st.json(jobs)
            else:
                st.error(f"Backend Error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection Failed: {e}. Is your FastAPI server running?")

st.divider()
st.caption("Job Strategy Lab v1.0 | Built for Strategic Precision")
