import streamlit as st
import httpx
import json

# --- Config ---
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Job Search Lab & Demo", page_icon="🚀", layout="wide")

st.title("Job Automation Developer Demo 🤖")
st.markdown("Interactive lab to test job search, AI drafting, and inspect raw API JSON.")

# --- Functions ---
def get_users():
    try:
        response = httpx.get(f"{BASE_URL}/users/1")
        if response.status_code == 200:
            return [response.json()]
        return []
    except:
        return []

def create_user(payload):
    return httpx.post(f"{BASE_URL}/users/", json=payload)

def search_jobs(query, location, results):
    return httpx.post(f"{BASE_URL}/jobs/search", json={"query": query, "location": location, "results": results})

def generate_draft(user_id, job_id):
    return httpx.post(f"{BASE_URL}/mail/generate", json={"user_id": user_id, "job_id": job_id})

def send_mail(user_id, job_id, subject, body):
    return httpx.post(f"{BASE_URL}/mail/send", json={"user_id": user_id, "job_id": job_id, "subject": subject, "body": body})

# --- UI: User Profile Section ---
st.sidebar.header("👤 Applicant Context")
users = get_users()

if not users:
    st.sidebar.warning("No user found! Create a dev profile:")
    name = st.sidebar.text_input("Full Name", "Tanisha Pritha")
    email = st.sidebar.text_input("Receiver Email", "tpritha190304@gmail.com")
    role = st.sidebar.text_input("Current Title", "FastAPI Engineer")
    skills_raw = st.sidebar.text_area("Skills", "Python, FastAPI, SQL, Groq, Gmail API")
    target = st.sidebar.text_input("Target Role", "Senior Backend Developer")
    loc = st.sidebar.text_input("Location", "Remote")
    
    if st.sidebar.button("Register Developer Profile"):
        payload = {
            "name": name,
            "email": email,
            "experience_years": 5.0,
            "current_role": role,
            "skills": [s.strip() for s in skills_raw.split(",")],
            "target_role": target,
            "location": loc,
            "remote_preference": "Remote",
            "email_tone": "Professional"
        }
        res = create_user(payload)
        if res.status_code == 200:
            st.sidebar.success("Profile Created! JSON Received:")
            st.sidebar.json(res.json())
            st.rerun()
        else:
            st.sidebar.error(f"Error: {res.status_code}")
else:
    user = users[0]
    st.sidebar.success(f"Logged in as ID #{user['id']}: {user['name']}")
    with st.sidebar.expander("🛠 Raw User Model"):
        st.json(user)

# --- UI: Job Search ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🔍 Search Parameters")
    q = st.text_input("Job Keywords", value=user['target_role'] if users else "Senior Developer")
    l = st.text_input("Location Filter", value=user['location'] if users else "London")
    count = st.slider("Result Count", 5, 20, 10)
    
    if st.button("Search & Inspect", type="primary"):
        with st.spinner("Fetching Data..."):
            res = search_jobs(q, l, count)
            if res.status_code == 200:
                st.session_state['jobs'] = res.json()
                st.success(f"Response: 200 OK | {len(st.session_state['jobs'])} Jobs")
                with st.expander("🛠 Raw Search Interface Response", expanded=True):
                    st.markdown("`POST` `/jobs/search` 返回的 JSON:")
                    st.json(st.session_state['jobs'])
            else:
                st.error(f"API Error {res.status_code}")

# --- UI: Results & Drafting ---
with col2:
    st.header("✉️ AI Mail & Dispatch")
    if 'jobs' in st.session_state:
        # Display jobs in a selectbox
        job_options = {f"{j['title']} @ {j['company']}": j for j in st.session_state['jobs']}
        selected_job_title = st.selectbox("Select target position:", list(job_options.keys()))
        selected_job = job_options[selected_job_title]

        with st.container(border=True):
            st.markdown(f"**Target Company:** {selected_job['company']}")
            st.markdown(f"**URL:** [Apply Here]({selected_job['apply_url']})")
        
        if st.button("Generate AI Draft (Groq)"):
            if not users:
                st.error("Register profile in sidebar first.")
            else:
                with st.spinner("Llama 3 is writing..."):
                    draft_res = generate_draft(user['id'], selected_job['id'])
                    if draft_res.status_code == 200:
                        draft_data = draft_res.json()
                        st.session_state['current_draft'] = draft_data['body']
                        st.session_state['current_subject'] = f"Application for {selected_job['title']} at {selected_job['company']}"
                        
                        st.subheader("Final Draft Preview")
                        st.info(f"Receiver: {user['email']}")
                        st.code(f"Subject: {st.session_state['current_subject']}")
                        st.text_area("Body", st.session_state['current_draft'], height=250)
                        
                        with st.expander("🛠 Raw Generation Response", expanded=True):
                            st.markdown("`POST` `/mail/generate` payload:")
                            st.json(draft_data)
        
        if 'current_draft' in st.session_state:
            if st.button("🚀 Fire SMTP Signal (Live Send)"):
                with st.spinner("Connecting to Gmail..."):
                    send_res = send_mail(
                        user['id'], 
                        selected_job['id'], 
                        st.session_state['current_subject'], 
                        st.session_state['current_draft']
                    )
                    if send_res.status_code == 200:
                        st.balloons()
                        st.success("Mail Delivered! Inspecting API Log:")
                        st.json(send_res.json())
                    else:
                        st.error("SMTP Delivery Failed. Check Logs.")
    else:
        st.write("Perform a search to see options.")
