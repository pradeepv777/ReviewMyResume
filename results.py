import streamlit as st

def show_results(final_score, tier, breakdown, feedback):
    st.header("Resume Analysis Results")

    # Tier and overall score
    st.subheader(f"Tier: {tier} • Score: {final_score}/100")

    # Category breakdown table
    st.subheader("Category-wise Breakdown")
    st.table(breakdown)

    # Feedback / Suggestions
    st.subheader("Suggestions & Feedback")
    for f in feedback:
        st.markdown(f"- {f}")
