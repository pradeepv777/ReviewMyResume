import streamlit as st

def show_results(final_score, tier, breakdown, feedback):
    st.header("📊 Resume Analysis Results")

    # Overall Score 
    st.subheader(f"🎯 Overall Score: {final_score}/100 (Tier {tier})")

    st.subheader("Category-wise Breakdown")
    st.table(breakdown)

    # Feedback / Suggestions
    st.subheader("💡 Suggestions & Feedback")
    for f in feedback:
        st.markdown(f"- {f}")
