import streamlit as st
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config

# ───────────────────────────────────────────────
# Config
# ───────────────────────────────────────────────
st.set_page_config(page_title="Course Viewer", page_icon="📚", layout="wide")

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "Bpa25072020!")

DIFFICULTY_COLOR = {"easy": "🟢", "medium": "🟠", "hard": "🔴"}
RESOURCE_ICON = {"article": "📄", "video": "🎬", "pdf": "📕"}


@st.cache_resource
def get_driver():
    return GraphDatabase.driver(URI, auth=AUTH)


driver = get_driver()


# ───────────────────────────────────────────────
# Neo4j helpers
# ───────────────────────────────────────────────
def run_query(query, **params):
    with driver.session() as session:
        return session.run(query, **params).data()


def get_chapters():
    return [r["name"] for r in run_query(
        "MATCH (c:Chapter) RETURN c.name AS name ORDER BY name"
    )]


def get_subchapters(chapter):
    return [r["name"] for r in run_query("""
        MATCH (c:Chapter {name:$chapter})-[:HAS_SUBCHAPTER]->(sc:SubChapter)
        RETURN sc.name AS name ORDER BY name
    """, chapter=chapter)]


def get_subchapter_data(sub_name):
    res = run_query("""
        MATCH (sc:SubChapter {name:$name})
        OPTIONAL MATCH (sc)-[:HAS_RESOURCE]->(r:Resource)
        WITH sc, collect(DISTINCT r {.title, .url, .type}) AS resources
        OPTIONAL MATCH (c:Chapter)-[:HAS_SUBCHAPTER]->(sc)
        RETURN sc.name AS name, sc.content AS content, sc.summary AS summary,
               sc.difficulty AS difficulty, sc.duration AS duration,
               sc.video_url AS video_url, sc.keywords AS keywords,
               c.name AS chapter, resources AS resources
    """, name=sub_name)
    return res[0] if res else None


def get_graph_data():
    return run_query("""
        MATCH (c:Chapter)-[:HAS_SUBCHAPTER]->(sc:SubChapter)
        RETURN c.name AS chapter, sc.name AS sub
    """)


# ───────────────────────────────────────────────
# Session state
# ───────────────────────────────────────────────
if "selected_sub" not in st.session_state:
    st.session_state.selected_sub = None


# ───────────────────────────────────────────────
# SIDEBAR — Navigation
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗂️ Navigation")
    st.caption("Pick a chapter, then a lesson.")

    chapters = get_chapters()
    chapter = st.selectbox("📘 Chapter", chapters, key="chapter_select")

    st.markdown("### 📖 Sub-chapters")
    subs = get_subchapters(chapter) if chapter else []
    for sub in subs:
        is_selected = sub == st.session_state.selected_sub
        label = f"✅ {sub}" if is_selected else f"📄 {sub}"
        if st.button(label, key=f"btn_{sub}", use_container_width=True):
            st.session_state.selected_sub = sub
            st.rerun()

    if st.session_state.selected_sub:
        st.divider()
        if st.button("❌ Clear selection", use_container_width=True):
            st.session_state.selected_sub = None
            st.rerun()


# ───────────────────────────────────────────────
# MAIN — Header
# ───────────────────────────────────────────────
st.title("📚 Course Viewer")
st.caption("Browse the curriculum graph and read enriched lessons.")
st.divider()


# ───────────────────────────────────────────────
# MAIN — 2 colonnes : Graph (gauche) | Contenu (droite)
# ───────────────────────────────────────────────
col_graph, col_content = st.columns([1, 1.3], gap="large")

# --- Colonne gauche : Graph ---
with col_graph:
    st.markdown("### 🌐 Curriculum graph")

    graph_rows = get_graph_data()
    nodes_set = {}
    edges = []
    selected = st.session_state.selected_sub

    for row in graph_rows:
        c, s = row["chapter"], row["sub"]
        if c not in nodes_set:
            nodes_set[c] = Node(
                id=c, label=c, size=25, color="#1f77b4", shape="dot"
            )
        if s not in nodes_set:
            color = "#e74c3c" if s == selected else "#2ecc71"
            size = 22 if s == selected else 14
            nodes_set[s] = Node(
                id=s, label=s, size=size, color=color, shape="dot"
            )
        edges.append(Edge(source=c, target=s, color="#cccccc"))

    config = Config(
        width=550,
        height=600,
        directed=False,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False,
    )

    clicked = agraph(nodes=list(nodes_set.values()), edges=edges, config=config)

    if clicked and clicked != st.session_state.selected_sub:
        # On ne sélectionne que si c'est un sub-chapter
        if clicked in [r["sub"] for r in graph_rows]:
            st.session_state.selected_sub = clicked
            st.rerun()


# --- Colonne droite : Contenu ---
with col_content:
    if not st.session_state.selected_sub:
        st.info("👈 Select a sub-chapter in the sidebar or click a green node in the graph.")
    else:
        data = get_subchapter_data(st.session_state.selected_sub)

        if not data:
            st.error("No data found for this sub-chapter.")
        else:
            # Header
            st.markdown(f"### 📖 {data['name']}")
            st.caption(f"Chapter: **{data['chapter']}**")

            if data["summary"]:
                st.markdown(f"> *{data['summary']}*")

            # Métriques compactes
            m1, m2, m3 = st.columns(3)
            diff = data["difficulty"] or "?"
            m1.metric("Difficulty", f"{DIFFICULTY_COLOR.get(diff, '⚪')} {diff.capitalize()}")
            m2.metric("Duration", f"{data['duration'] or '?'} min")
            m3.metric("Resources", len(data["resources"] or []))

            # Keywords
            if data["keywords"]:
                st.markdown(" ".join([f"`#{k}`" for k in data["keywords"]]))

            st.divider()

            # Tabs
            tab_lesson, tab_video, tab_res = st.tabs(["📘 Lesson", "🎬 Video", "🔗 Resources"])

            with tab_lesson:
                if data["content"]:
                    st.markdown(data["content"])
                else:
                    st.info("No content available yet.")

                st.divider()
                st.download_button(
                    "📥 Download as Markdown",
                    data=data["content"] or "",
                    file_name=f"{data['name'].replace(' ', '_')}.md",
                    mime="text/markdown",
                    disabled=not data["content"],
                )

            with tab_video:
                if data["video_url"]:
                    st.video(data["video_url"])
                else:
                    st.info("No video available for this lesson.")

            with tab_res:
                if data["resources"]:
                    for r in data["resources"]:
                        icon = RESOURCE_ICON.get(r["type"], "🔗")
                        st.markdown(f"- {icon} [{r['title']}]({r['url']}) — *{r['type']}*")
                else:
                    st.info("No external resources yet.")
