import streamlit as st
import pandas as pd

def show_results(final_score, tier, breakdown, feedback):
    st.header("Resume Analysis Results")
    st.subheader(f"Overall Score: {final_score}/100 (Tier {tier})")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔎Suggestions & Feedback")
        for f in feedback:
            st.markdown(f"- {f}")

    with col2:
        st.subheader("📄Section-wise Breakdown")
        df = pd.DataFrame(list(breakdown.items()), columns=["Section", "Score"])
        st.table(df)  
