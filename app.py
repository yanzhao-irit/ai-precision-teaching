import streamlit as st

st.set_page_config(
    page_title="Student Analytics",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Student Analytics Platform")

st.markdown("""
Welcome to the **Student Analytics Platform**.

Use the sidebar to navigate between sections:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📊 Dashboard
    Explore student rankings, exam details, analytics
    and the global graph view.
    """)
    if st.button("Go to Dashboard →", use_container_width=True):
        st.switch_page("pages/Dashboard.py")

with col2:
    st.markdown("""
    ### 📚 Course Viewer
    Navigate the curriculum graph and access
    course content for each sub-chapter.
    """)
    if st.button("Go to Course Viewer →", use_container_width=True):
        st.switch_page("pages/Courses_Viewer.py")

st.markdown("---")
st.caption("Powered by Neo4j + Streamlit")
