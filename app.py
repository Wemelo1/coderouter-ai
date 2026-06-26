import streamlit as st
from workflow import coderouter
from cost_tracker import get_session_stats

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CodeRouter AI",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ CodeRouter AI")
st.caption("Cost-aware coding assistant — routes tasks intelligently between local and remote models")

# ─── Layout: Chat | Stats ─────────────────────────────────────────────────────

chat_col, stats_col = st.columns([2, 1])

# ─── Chat Column ──────────────────────────────────────────────────────────────

with chat_col:
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

    # User input
    if query := st.chat_input("Ask a coding question..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Routing your query..."):
                result = coderouter.invoke({"query": query})

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

# ─── Stats Column ─────────────────────────────────────────────────────────────

with stats_col:
    st.subheader("📊 Session Stats")
    stats = get_session_stats()

    st.metric("Total Queries", stats["total_queries"])
    st.metric("🟢 Handled Locally", stats["local_queries"])
    st.metric("🔴 Handled Remotely", stats["remote_queries"])
    st.metric("💰 Total Saved", f"${stats['total_saved']:.6f}")
    st.metric("💸 Total Spent", f"${stats['total_spent']:.6f}")

    if stats["total_queries"] > 0:
        pct = round((stats["local_queries"] / stats["total_queries"]) * 100)
        st.progress(pct / 100, text=f"{pct}% handled locally")

    st.divider()
    st.caption("🟢 Local = Ollama (free)\n🔴 Remote = Fireworks AI (credits)")
