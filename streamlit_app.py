import streamlit as st
from pathlib import Path
from parser import parse_resume
from scoring import score_resume, assign_tier
from results import show_results

st.set_page_config(page_title="ReviewMyResume",layout="wide")

# css for app styling
st.markdown("""
<style>
    .stApp {
        background-color: #10232A;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    footer {
        visibility: hidden;
        height: 0;
    }
    [data-testid="stAppDeployButton"] {
        display: none;
    }
    h1 {
        color: #D3C3B9;
    }
</style>
""", unsafe_allow_html=True)

st.title("ReviewMyResume")


if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    left, right = st.columns([1, 1])
    with left:
        st.header("Is your resume good enough?")
        st.write("A free and fast resume reviewer to check and ensure your resume is ready for the job market.")

        st.subheader("Upload Your Resume")
        uploaded_file = st.file_uploader("Drop your resume here or choose a file", type=["pdf"])

        if uploaded_file and st.button("Analyze Resume"):
            temp_path = Path("temp_resume.pdf")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            parsed_data = parse_resume(str(temp_path))
            final_score, feedback, breakdown = score_resume(parsed_data)
            tier = assign_tier(final_score)

            st.session_state.final_score = final_score
            st.session_state.tier = tier
            st.session_state.breakdown = breakdown
            st.session_state.feedback = feedback

            st.session_state.page = "results"
            st.rerun()

    with right:
        resume_image_path = Path("static/Resume_Pic.jpg")
        if resume_image_path.exists():
            st.image(str(resume_image_path), use_column_width=True)

elif st.session_state.page == "results":
    show_results(
        st.session_state.final_score,
        st.session_state.tier,
        st.session_state.breakdown,
        st.session_state.feedback
    )
    if st.button("Analyze Another Resume"):
        st.session_state.page = "home"
        st.rerun()
