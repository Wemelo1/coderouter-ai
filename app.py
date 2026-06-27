import streamlit as st
from workflow import coderouter
from cost_tracker import (
    get_session_stats, 
    register_user, 
    authenticate_user, 
    get_query_history
)

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CodeRouter AI",
    page_icon="⚡",
    layout="wide"
)

# ─── Authentication View ──────────────────────────────────────────────────────

if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.messages = []

if st.session_state.user_id is None:
    st.title("⚡ CodeRouter AI")
    st.caption("Cost-aware coding assistant — routes tasks intelligently between local and remote models")
    
    # Centered container for login / registration
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                if submitted:
                    user_id = authenticate_user(username, password)
                    if user_id is not None:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.session_state.messages = []
                        st.success(f"Logged in as {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("New Username")
                new_password = st.text_input("New Password", type="password")
                submitted = st.form_submit_button("Register", use_container_width=True)
                if submitted:
                    if not new_username.strip() or not new_password:
                        st.error("Username and password cannot be empty")
                    elif register_user(new_username, new_password):
                        st.success("Registration successful! You can now log in.")
                    else:
                        st.error("Username already exists")
    st.stop()

# ─── Main App Header ─────────────────────────────────────────────────────────

st.title("⚡ CodeRouter AI")
st.caption(f"Logged in as **{st.session_state.username}** — Cost-aware coding assistant")

# ─── Sidebar Account Management ──────────────────────────────────────────────

with st.sidebar:
    st.subheader(f"👤 Account: {st.session_state.username}")
    if st.button("Logout", key="logout_btn", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("🟢 Local = Ollama (free)\n🔴 Remote = Fireworks AI (credits)")

# ─── Layout: Chat | Stats & History ──────────────────────────────────────────

chat_col, stats_col = st.columns([2, 1])

# ─── Chat Column ──────────────────────────────────────────────────────────────

with chat_col:
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "meta" in msg:
                meta = msg["meta"]
                badge = "🟢 Local" if meta["model_choice"] == "local" else "🔴 Remote"
                st.caption(
                    f"{badge} | Complexity: {meta['complexity']}/5 | "
                    f"Tokens: {meta['tokens']} | "
                    f"Saved: ${meta['cost_saved']:.6f} | "
                    f"Spent: ${meta['cost_incurred']:.6f}"
                )

    # Function to run queries in workflow
    def run_query(q):
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)

        with st.chat_message("assistant"):
            with st.spinner("Routing your query..."):
                result = coderouter.invoke({"query": q, "user_id": st.session_state.user_id})

            st.markdown(result["response"])

            badge = "🟢 Local" if result["model_choice"] == "local" else "🔴 Remote"
            st.caption(
                f"{badge} | Complexity: {result['complexity_score']}/5 | "
                f"Tokens: {result['tokens']} | "
                f"Saved: ${result['cost_saved']:.6f} | "
                f"Spent: ${result['cost_incurred']:.6f}"
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": result["response"],
                "meta": {
                    "model_choice": result["model_choice"],
                    "complexity": result["complexity_score"],
                    "tokens": result["tokens"],
                    "cost_saved": result["cost_saved"],
                    "cost_incurred": result["cost_incurred"]
                }
            })
            st.rerun()

    # Check for reused query
    prefilled = st.session_state.pop("prefilled_query", "")
    if prefilled:
        run_query(prefilled)

    # User input
    if query := st.chat_input("Ask a coding question..."):
        run_query(query)

# ─── Stats & History Column ───────────────────────────────────────────────────

with stats_col:
    # 📊 Session Stats
    st.subheader("📊 Session Stats")
    stats = get_session_stats(st.session_state.user_id)

    st.metric("Total Queries", stats["total_queries"])
    st.metric("🟢 Handled Locally", stats["local_queries"])
    st.metric("🔴 Handled Remotely", stats["remote_queries"])
    st.metric("💰 Total Saved", f"${stats['total_saved']:.6f}")
    st.metric("💸 Total Spent", f"${stats['total_spent']:.6f}")

    if stats["total_queries"] > 0:
        pct = round((stats["local_queries"] / stats["total_queries"]) * 100)
        st.progress(pct / 100, text=f"{pct}% handled locally")

    st.divider()

    # 📜 Query History
    st.subheader("📜 Query History")
    history = get_query_history(st.session_state.user_id)
    if not history:
        st.info("No queries logged yet.")
    else:
        for idx, item in enumerate(history):
            badge = "🟢" if "local" in item["routed_to"] else "🔴"
            with st.expander(f"{badge} {item['timestamp']} - {item['query'][:25]}"):
                st.markdown(f"**Query:** {item['query']}")
                st.markdown(f"**Routed:** {item['routed_to']} ({item['model_used']})")
                st.markdown(
                    f"Complexity: {item['complexity']}/5 | Tokens: {item['tokens']}\n\n"
                    f"Saved: ${item['cost_saved']:.6f} | Spent: ${item['cost_incurred']:.6f}"
                )
                if st.button("Reuse Query", key=f"reuse_{idx}", use_container_width=True):
                    st.session_state.prefilled_query = item['query']
                    st.rerun()
