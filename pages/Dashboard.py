from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from neo4j import GraphDatabase

# =====================
# ⚙️ PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Student Tracking",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================
# 🎨 CUSTOM CSS
# =====================
st.markdown(
    """
<style>
    /* === GLOBAL BACKGROUND === */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }

    /* === GENERAL TEXT === */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
        color: #e8e8e8 !important;
    }

    /* === MAIN TITLE === */
    h1 {
        background: linear-gradient(90deg, #00d4ff, #00ff9f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* === SUBTITLES === */
    h2, h3 {
        color: #ffffff !important;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        padding-bottom: 8px;
    }

    /* === CAPTION / GREY SUBTITLE === */
    .stApp [data-testid="stCaptionContainer"],
    .stApp small {
        color: #b0b8d0 !important;
        opacity: 1 !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 25, 0.98) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] label {
        color: #00d4ff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* === TEXT INPUTS === */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    .stTextInput input::placeholder {
        color: #8892b0 !important;
    }
    .stTextInput input:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
    }

    /* === SELECTBOX === */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 8px !important;
    }
    .stSelectbox div[data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* === SLIDER === */
    .stSlider label {
        color: #00d4ff !important;
        font-weight: 600 !important;
    }
    .stSlider [data-baseweb="slider"] div {
        color: #ffffff !important;
    }

    /* === BUTTONS === */
    .stButton button {
        background: linear-gradient(90deg, #00d4ff, #0077ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4);
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 8px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #b0b8d0 !important;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00d4ff, #0077ff) !important;
        color: white !important;
    }
    .stTabs [aria-selected="true"] * {
        color: white !important;
    }

    /* === METRICS === */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(0, 212, 255, 0.3);
        padding: 20px;
        border-radius: 12px;
    }
    [data-testid="stMetric"] label {
        color: #00d4ff !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* === ALERTS === */
    .stAlert {
        background: rgba(255, 255, 255, 0.08) !important;
        border-left: 4px solid #00d4ff !important;
    }
    .stAlert * {
        color: #ffffff !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
    /* === FORCE ALL SIDEBAR INPUTS === */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] input[type="number"],
    section[data-testid="stSidebar"] input {
        background-color: #1a1a3e !important;
        background: #1a1a3e !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #00d4ff !important;
        border: 1px solid #00d4ff !important;
        border-radius: 8px !important;
    }

    /* Internal TextInput wrapper */
    section[data-testid="stSidebar"] div[data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="base-input"] {
        background-color: #1a1a3e !important;
        background: #1a1a3e !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="input"] *,
    section[data-testid="stSidebar"] div[data-baseweb="base-input"] * {
        background-color: transparent !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Placeholder */
    section[data-testid="stSidebar"] input::placeholder {
        color: #8892b0 !important;
        -webkit-text-fill-color: #8892b0 !important;
        opacity: 1 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =====================
# 🔗 URL PARAMS
# =====================
query_params = st.query_params
selected_type = query_params.get("type", None)
selected_value = query_params.get("value", None)

# =====================
# 📌 Pré-remplissage selon clic sur le graphe
# =====================
name_default = ""
chapter_default = ""
sub_chapter_default = ""

if selected_type == "chapter":
    chapter_default = selected_value
elif selected_type == "sub_chapter":
    sub_chapter_default = selected_value
elif selected_type == "student":
    name_default = selected_value

# =====================
# 📌 SIDEBAR FILTERS
# =====================
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    student_name = st.text_input("👤 Student", value=name_default).strip()
    chapter = st.text_input("📚 Chapter", value=chapter_default).strip()
    sub_chapter = st.text_input("📖 Sub-Chapter", value=sub_chapter_default).strip()
    teacher = st.text_input("👨‍🏫 Teacher").strip()

    st.markdown("---")
    st.markdown("### ⚙️ Options")

    sort_by = st.selectbox(
        "Sort by", ["score DESC", "score ASC", "student ASC", "student DESC"]
    )
    limit = st.slider("Number of results", 5, 100, 20)

    st.markdown("---")

    if st.button("🔄 Reset", use_container_width=True):
        st.query_params.clear()
        st.rerun()

    # Active filters indicator
    active_filters = sum([bool(student_name), bool(chapter), bool(teacher)])
    if active_filters > 0:
        st.success(f"✅ {active_filters} active filter(s)")

# =====================
# 🚀 HEADER
# =====================
st.title("Interactive Dashboard — Mathematics")
st.caption("A way to analyze your courses and track your progress.")

# =====================
# 🔌 DATABASE CONNECTION
# =====================
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Bpa25072020!"))

# Map English sort options
sort_map = {
    "score DESC": "score DESC",
    "score ASC": "score ASC",
    "student ASC": "student ASC",
    "student DESC": "student DESC",
}
cypher_sort = sort_map.get(sort_by, "score DESC")

param = {
    "student_name": student_name if student_name else None,
    "chapter_name": chapter if chapter else None,
    "sub_chapter_name": sub_chapter or None,
    "filter_type": selected_type,
    "teacher_name": teacher if teacher else None,
    "limit": limit,
}

# =====================
# 📑 TABS
# =====================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🏆 Rankings", "📋 Details", "📊 Analytics", "🌐 Graph"]
)

# ---------- TAB 1 : RANKINGS ----------
with tab1:
    st.subheader("🏆 Student Rankings")

    query_average = """
    MATCH (e:Student)-[r:TOOK]->(ex:Exam)-[:COVERS]->(sc:SubChapter)
    MATCH (sc)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
    WHERE r.score IS NOT NULL
      AND ($student_name     IS NULL OR e.name  CONTAINS $student_name)
      AND ($chapter_name     IS NULL OR c.name  CONTAINS $chapter_name)
      AND ($sub_chapter_name IS NULL OR sc.name CONTAINS $sub_chapter_name)
    WITH e, avg(r.score) AS average_score
    RETURN e.name AS student, round(average_score, 2) AS average
    ORDER BY average_score DESC
    LIMIT $limit
    """

    with driver.session() as session:
        data_average = [record.data() for record in session.run(query_average, param)]

    if data_average:
        df_rank = pd.DataFrame(data_average)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.dataframe(
                df_rank,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "student": "👤 Student",
                    "average": st.column_config.ProgressColumn(
                        "📊 Average",
                        format="%.2f",
                        min_value=0,
                        max_value=20,
                    ),
                },
            )

        with col2:
            fig = px.bar(
                df_rank.head(10),
                x="average",
                y="student",
                orientation="h",
                color="average",
                color_continuous_scale=["#ff0055", "#ffaa00", "#00ff9f"],
                title="Top 10 Students",
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8e8e8", size=13),
                title_font=dict(color="#ffffff", size=18),
                xaxis=dict(
                    gridcolor="rgba(255,255,255,0.1)",
                    color="#e8e8e8",
                    title="Average Score",
                    title_font=dict(color="#00d4ff"),
                ),
                yaxis=dict(
                    gridcolor="rgba(255,255,255,0.1)",
                    color="#e8e8e8",
                    title="Student",
                    title_font=dict(color="#00d4ff"),
                ),
                legend=dict(font=dict(color="#e8e8e8")),
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data found")

# ---------- TAB 2 : DETAILS ----------
with tab2:
    st.subheader("📋 Exam Details")

    query_details = f"""
    MATCH (e:Student)-[r:TOOK]->(ex:Exam)-[:COVERS]->(sc:SubChapter)
    MATCH (sc)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
    MATCH (c)-[:BELONGS_TO_SUBJECT]->(m:Subject)
    MATCH (e)-[:HAS_TEACHER]->(p:Teacher)
    WHERE
        ($student_name     IS NULL OR e.name  CONTAINS $student_name)
        AND ($teacher_name     IS NULL OR p.name  CONTAINS $teacher_name)
        AND ($chapter_name     IS NULL OR c.name  CONTAINS $chapter_name)
        AND ($sub_chapter_name IS NULL OR sc.name CONTAINS $sub_chapter_name)
    RETURN
        e.name AS student,
        ex.id  AS exam,
        r.score AS score,
        sc.name AS sub_chapter,
        c.name  AS chapter,
        m.name  AS subject,
        p.name  AS teacher
    ORDER BY {cypher_sort}
    {f"LIMIT {limit}" if not student_name else ""}
    """

    with driver.session() as session:
        data_details = [record.data() for record in session.run(query_details, param)]

    df_details = pd.DataFrame(data_details)

    if not df_details.empty:
        st.dataframe(
            df_details,
            use_container_width=True,
            hide_index=True,
            column_config={
                "student": "👤 Student",
                "exam": "📝 Exam",
                "score": st.column_config.ProgressColumn(
                    "🎯 Score",
                    format="%.2f",
                    min_value=0,
                    max_value=20,
                ),
                "sub_chapter": "📖 Sub-Chapter",
                "chapter": "📚 Chapter",
                "subject": "🔬 Subject",
                "teacher": "👨‍🏫 Teacher",
            },
        )
    else:
        st.warning("No results found")

# ---------- TAB 3 : ANALYTICS ----------
with tab3:
    if student_name or teacher:
        st.subheader("📊 Visual Analytics")

        query_stats = """
        MATCH (e:Student)-[r:TOOK]->(ex:Exam)-[:COVERS]->(sc:SubChapter)
        MATCH (sc)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
        MATCH (e)-[:HAS_TEACHER]->(p:Teacher)
        WHERE 
            ($student_name IS NULL OR e.name CONTAINS $student_name)
            AND ($teacher_name IS NULL OR p.name CONTAINS $teacher_name)
            AND ($chapter_name IS NULL OR c.name CONTAINS $chapter_name OR sc.name CONTAINS $chapter_name)
        RETURN 
            round(avg(r.score), 2) AS average,
            round(min(r.score), 2) AS minimum,
            round(max(r.score), 2) AS maximum,
            count(r) AS total_exams
        """

        with driver.session() as session:
            stats = session.run(query_stats, param).single()

        if stats:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📈 Average", f"{stats['average']}/20")
            c2.metric("📉 Min", f"{stats['minimum']}/20")
            c3.metric("📊 Max", f"{stats['maximum']}/20")
            c4.metric("🧮 Total Exams", stats["total_exams"])

        st.markdown("---")

        # Score distribution
        query_dist = """
        MATCH (e:Student)-[r:TOOK]->(ex:Exam)-[:COVERS]->(sc:SubChapter)
        MATCH (sc)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
        MATCH (e)-[:HAS_TEACHER]->(p:Teacher)
        WHERE 
            ($student_name     IS NULL OR e.name  CONTAINS $student_name)
            AND ($teacher_name     IS NULL OR p.name  CONTAINS $teacher_name)
            AND ($chapter_name     IS NULL OR c.name  CONTAINS $chapter_name)
            AND ($sub_chapter_name IS NULL OR sc.name CONTAINS $sub_chapter_name)
        RETURN r.score AS score
        """

        with driver.session() as session:
            scores = [record["score"] for record in session.run(query_dist, param)]

        if scores:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 📊 Score Distribution")
                df_scores = pd.DataFrame(scores, columns=["score"])
                df_scores["score_bin"] = (df_scores["score"] * 2).round() / 2

                fig = px.histogram(
                    df_scores,
                    x="score_bin",
                    nbins=40,
                    color_discrete_sequence=["#00ff9f"],
                    labels={"score_bin": "Score", "count": "Frequency"},
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    xaxis_title="Score",
                    yaxis_title="Frequency",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("##### 📈 Smoothed Progression")
                query_evolution = """
                MATCH (e:Student)-[r:TOOK]->(ex:Exam)-[:COVERS]->(sc:SubChapter)
                MATCH (sc)-[:BELONGS_TO_CHAPTER]->(c:Chapter)
                MATCH (e)-[:HAS_TEACHER]->(p:Teacher)
                WHERE 
                    ($student_name     IS NULL OR e.name  CONTAINS $student_name)
                    AND ($teacher_name     IS NULL OR p.name  CONTAINS $teacher_name)
                    AND ($chapter_name     IS NULL OR c.name  CONTAINS $chapter_name)
                    AND ($sub_chapter_name IS NULL OR sc.name CONTAINS $sub_chapter_name)
                RETURN ex.id AS exam, r.score AS score
                ORDER BY ex.id
                """
                with driver.session() as session:
                    data_evo = [r.data() for r in session.run(query_evolution, param)]

                if data_evo:
                    df_evo = pd.DataFrame(data_evo).sort_values("exam")
                    df_evo["smoothed_score"] = df_evo["score"].rolling(window=5).mean()

                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=df_evo["exam"],
                            y=df_evo["score"],
                            mode="markers",
                            name="Score",
                            marker=dict(color="#00aaff", size=6, opacity=0.5),
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=df_evo["exam"],
                            y=df_evo["smoothed_score"],
                            mode="lines",
                            name="Trend",
                            line=dict(color="#00ff9f", width=3),
                        )
                    )
                    fig.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="white",
                        xaxis_title="Exam",
                        yaxis_title="Score",
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Select a student or a teacher to view analytics.")

# ---------- TAB 4 : GRAPH ----------
with tab4:
    st.subheader("🌐 Mathematics Knowledge Graph")
    st.caption("Click on a node to filter results 👇")

    query_graph = """
    MATCH (m:Subject {name:"Mathematics"})-[:HAS_CHAPTER]->(c:Chapter)
    MATCH (c)-[:HAS_SUBCHAPTER]->(sc:SubChapter)
    OPTIONAL MATCH (e:Student {name:$student_name})-[r:TOOK]->(ex:Exam)-[:COVERS]->(sc)
    RETURN m.name AS subject, c.name AS chapter, sc.name AS sub_chapter, avg(r.score) AS score
    """

    with driver.session() as session:
        results = [record.data() for record in session.run(query_graph, param)]

    if results:
        import math

        # 🧮 Organiser les données par chapitre
        chapters_map = {}  # chapter_name -> list of (sub_name, score)
        subject_name = None

        for row in results:
            subject_name = row["subject"]
            c = row["chapter"]
            sc = row["sub_chapter"]
            score = row["score"]
            if not c or not sc:
                continue
            chapters_map.setdefault(c, []).append((sc, score))

        nodes, edges = [], []
        subject_id = f"subject::{subject_name}"

        # 🔴 SUBJECT au centre (fixe)
        nodes.append(
            Node(
                id=subject_id,
                label=subject_name,
                size=55,
                color="#ff0055",
                shape="dot",
                x=0,
                y=0,
                fixed=True,
                physics=False,
            )
        )

        # 🔵 CHAPITRES en cercle autour
        chapter_names = list(chapters_map.keys())
        n_chapters = len(chapter_names)
        chapter_radius = 450  # distance Subject -> Chapter

        for i, c_name in enumerate(chapter_names):
            angle = (2 * math.pi * i) / n_chapters
            cx = chapter_radius * math.cos(angle)
            cy = chapter_radius * math.sin(angle)
            chapter_id = f"chapter::{c_name}"

            nodes.append(
                Node(
                    id=chapter_id,
                    label=c_name,
                    size=35,
                    color="#00aaff",
                    shape="dot",
                    x=cx,
                    y=cy,
                    fixed=False,  # 👈 peut bouger
                    physics=True,
                )
            )
            edges.append(Edge(source=subject_id, target=chapter_id, color="#00d4ff"))

            # 🟢 SOUS-CHAPITRES autour de leur chapitre
            subs = chapters_map[c_name]
            n_subs = len(subs)
            sub_radius = 200  # distance Chapter -> SubChapter

            for j, (sc_name, score) in enumerate(subs):
                # angle réparti autour du chapitre (éventail vers l'extérieur)
                spread = math.pi  # demi-cercle
                if n_subs > 1:
                    sub_angle = angle - spread / 2 + (spread * j) / (n_subs - 1)
                else:
                    sub_angle = angle
                sx = cx + sub_radius * math.cos(sub_angle)
                sy = cy + sub_radius * math.sin(sub_angle)

                # Couleur selon score
                if score is None:
                    color, size_sc = "#555577", 18
                elif score >= 15:
                    color, size_sc = "#00ff9f", 24
                elif score >= 10:
                    color, size_sc = "#ffaa00", 24
                else:
                    color, size_sc = "#ff0055", 24

                sub_id = f"sub_chapter::{sc_name}"
                label_sub = sc_name + (
                    f"\n{round(score, 2)}/20" if score is not None else ""
                )

                nodes.append(
                    Node(
                        id=sub_id,
                        label=label_sub,
                        size=size_sc,
                        color=color,
                        shape="dot",
                        x=sx,
                        y=sy,
                        fixed=False,
                        physics=True,
                    )
                )
                edges.append(Edge(source=chapter_id, target=sub_id, color="#aaaaff"))

        # ⚙️ Config : PHYSIQUE DÉSACTIVÉE par défaut
        config = Config(
            width="100%",
            height=750,
            directed=False,
            physics=False,  # 👈 PAS de physique au démarrage
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#00ff9f",
            collapsible=False,
            backgroundColor="#1a1a2e",
            fit=True,  # 👈 fit naturel sur les positions calculées
        )

        clicked_node = agraph(nodes=nodes, edges=edges, config=config)

        # 🎯 JS : physique douce QUAND on drague un node
        st.components.v1.html(
            """
        <script>
            function setupGraph() {
                const iframes = window.parent.document.querySelectorAll('iframe');
                iframes.forEach(iframe => {
                    try {
                        const network = iframe.contentWindow?.network;
                        if (!network) return;

                        // Physique configurée mais désactivée
                        network.setOptions({
                            physics: {
                                enabled: false,
                                solver: "forceAtlas2Based",
                                forceAtlas2Based: {
                                    gravitationalConstant: -100,
                                    centralGravity: 0,        // 👈 PAS de gravité centrale
                                    springLength: 180,
                                    springConstant: 0.15,
                                    damping: 0.8,
                                    avoidOverlap: 1
                                }
                            },
                            interaction: { hover: true }
                        });

                        // 👉 Active la physique seulement pendant qu'on drague
                        network.on("dragStart", function() {
                            network.setOptions({ physics: { enabled: true } });
                        });
                        network.on("dragEnd", function() {
                            setTimeout(() => {
                                network.setOptions({ physics: { enabled: false } });
                            }, 800);
                        });

                    } catch(e) {}
                });
            }
            setTimeout(setupGraph, 800);
            setTimeout(setupGraph, 2000);
        </script>
        """,
            height=0,
        )

        st.markdown("""
        **Legend:**  
        🔴 Subject &nbsp;&nbsp; 🔵 Chapter &nbsp;&nbsp; 🟢 Score ≥ 15 &nbsp;&nbsp; 🟠 Score ≥ 10 &nbsp;&nbsp; 🔴 Score < 10 &nbsp;&nbsp; ⚫ No score
        """)

        # ✅ Click handler
        if "last_clicked" not in st.session_state:
            st.session_state.last_clicked = None

        if clicked_node and clicked_node != st.session_state.last_clicked:
            st.session_state.last_clicked = clicked_node
            if clicked_node.startswith("chapter::"):
                st.query_params["type"] = "chapter"
                st.query_params["value"] = clicked_node.replace("chapter::", "")
                st.rerun()
            elif clicked_node.startswith("sub_chapter::"):
                st.query_params["type"] = "sub_chapter"
                st.query_params["value"] = clicked_node.replace("sub_chapter::", "")
                st.rerun()
    else:
        st.warning("No graph data found")
