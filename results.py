import streamlit as st
import pandas as pd

def show_results(final_score, tier, breakdown, feedback):
    st.header("Resume Analysis Results")
    st.subheader(f"Overall Score: {final_score}/100 (Tier {tier})")
    
    col1, col2 = st.columns([1, 1])# two columns [1,1] for size of columns (equal)
    
    with col1:  # specify what to be done in col1 -left
        st.subheader("🔎Suggestions & Feedback")
        for f in feedback:
            st.write(f"• {f}")

    with col2: # specify what to be done in col2 -right
        st.subheader("📄Section-wise Breakdown")
        df = pd.DataFrame(list(breakdown.items()), columns=["Section", "Score"])
        df.index = df.index + 1  # started table index with 1 
        st.table(df)  
