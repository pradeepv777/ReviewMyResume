import streamlit as st
from pathlib import Path
from parser import parse_resume
from scoring import score_resume
from results import show_results
import time

st.set_page_config(page_title="Review My Resume", layout="wide")

# Load the styles.css  file
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("static/styles.css")

# Hide Streamlit header
st.markdown("""<style>[data-testid="stHeader"] {display: none;}</style>""", unsafe_allow_html=True)

st.markdown("""
<style>
.upload-card {
    background: transparent !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
    border: none !important;
}
div[data-testid="stFileUploader"] > div {
    background: transparent !important;
    border: none !important;
}
div[data-testid="stVerticalBlock"], 
div[data-testid="stHorizontalBlock"] {
    background: transparent !important;
}
.stContainer, .block-container {
    background: transparent !important;
}
div[class*="css-"] {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown('<div class="topbar">ReviewMyResume</div>', unsafe_allow_html=True)
st.markdown('<div class="content">', unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    left, right = st.columns([1, 1])
    with left:
        st.markdown("<h1 style='font-size: 2.8rem; font-weight: bold;'>Is your resume good enough?</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.2rem; line-height: 1.6;'>A free and fast resume reviewer to check and ensure your resume is ready for the job market.</p>", unsafe_allow_html=True)

        st.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.markdown("### Upload Your Resume")
        uploaded_file = st.file_uploader("Drop your resume here or choose a file", type=["pdf"], label_visibility="collapsed")
        st.markdown('<p>PDF only. Max 2MB file size.</p>', unsafe_allow_html=True)

        if uploaded_file:
            st.session_state["resume_file"] = uploaded_file
            if st.button("Analyze Resume"):
                # Show full-page centered loading spinner with blur
                loading_placeholder = st.empty()
                with loading_placeholder.container():
                    st.markdown("""
                    <div style='position: fixed; top: 0; left:0; width: 100vw; height: 100vh; 
                                display: flex; justify-content: center; align-items: center;
                                backdrop-filter: blur(6px); background: rgba(0,0,0,0.4); z-index: 10000;'>
                        <div style='display: flex; flex-direction: column; align-items: center; color:white;'>
                            <div class="loader" style="border: 6px solid rgba(255,255,255,0.2); 
                                 border-top: 6px solid #ff69b4; border-radius: 50%; 
                                 width: 60px; height: 60px; animation: spin 1s linear infinite;"></div>
                            <p style="font-size: 1.2rem; margin-top: 1rem;">Analyzing resume...</p>
                        </div>
                    </div>
                    <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    </style>
                    """, unsafe_allow_html=True)

                temp_path = Path("temp_resume.pdf")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                parsed_data = parse_resume(str(temp_path))
                final_score, feedback, breakdown = score_resume(parsed_data)

                # ✅ Calculate the tier of resume
                if final_score >= 85:
                    tier = "A"
                elif final_score >= 70:
                    tier = "B"
                elif final_score >= 50:
                    tier = "C"
                else:
                    tier = "D"

                st.session_state.final_score = final_score
                st.session_state.tier = tier
                st.session_state.breakdown = breakdown
                st.session_state.feedback = feedback

                loading_placeholder.empty()
                st.session_state.page = "results"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        resume_image_path = Path("static/Resume_Pic.jpg")
        if resume_image_path.exists():
            st.image(str(resume_image_path), use_column_width=True)

    st.markdown('<h2 style="text-align:center; margin-top:3rem; color:black;">How It Works</h2>', unsafe_allow_html=True)
    st.markdown('''
    <div class="steps-container">
        <div class="step">
            <h3>📄 Extract</h3>
            <p>Your PDF resume is scanned and parsed using NLP to extract clean text.</p>
        </div>
        <div class="step">
            <h3>🧠 Analyze</h3>
            <p>Skills and key data are extracted using rule-based NLP logic.</p>
        </div>
        <div class="step">
            <h3>📊 Score</h3>
            <p>We calculate a score based on how many strong signals your resume includes.</p>
        </div>
    </div>
    <div class="steps-container" style="margin-top:1rem;">
        <div class="step">
            <h3>🛠️ Suggest</h3>
            <p>Get suggestions to boost visibility, fix weak points, and increase hiring chances.</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

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

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="footer">© Review My Resume</div>', unsafe_allow_html=True)
