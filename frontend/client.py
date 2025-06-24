import streamlit as st
import json
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.tool import ToolMessage
from backend.sales_agent.graph import graph  # Adjust your import based on your project structure

def display_chat_history():
    if not st.session_state.messages:
        st.markdown(
            """
            <div style='text-align: center; padding: 30px;'>
                <h1>👋 Welcome!</h1>
                <p>How can I assist you today?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    for message in st.session_state.messages:
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.write(message.content)

def process_events(event):
    seen_ids = set()
    if isinstance(event, dict) and "messages" in event:
        messages = event["messages"]
        last_message = messages[-1] if messages else None
        if isinstance(last_message, AIMessage):
            if last_message.id not in seen_ids and last_message.content:
                seen_ids.add(last_message.id)
                st.session_state.messages.append(last_message)
                with st.chat_message("assistant"):
                    st.write(last_message.content)
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return last_message.tool_calls[0]
    return None

def handle_tool_approval(snapshot, event):
    st.write("⚠️ The assistant wants to perform an action. Do you approve?")
    last_message = snapshot.values.get("messages", [])[-1]
    if (isinstance(last_message, AIMessage)
        and hasattr(last_message, "tool_calls")
        and last_message.tool_calls):
        tool_call = last_message.tool_calls[0]
        with st.chat_message("assistant"):
            st.markdown("#### 🔧 Proposed Action")
            with st.expander("View Function Details", expanded=True):
                st.info(f"Function: **{tool_call['name']}**")
                try:
                    args_formatted = json.dumps(tool_call["args"], indent=2)
                    st.code(f"Arguments:\n{args_formatted}", language="json")
                except:
                    st.code(f"Arguments:\n{tool_call['args']}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve"):
            with st.spinner("Processing..."):
                try:
                    result = graph.invoke(None, st.session_state.config)
                    process_events(result)
                    st.session_state.pending_approval = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing approval: {str(e)}")
    with col2:
        if st.button("❌ Deny"):
            st.session_state.show_reason_input = True
        if st.session_state.get("show_reason_input", False):
            reason = st.text_input("Please explain why you're denying this action:")
            submit = st.button("Submit Denial", key="submit_denial")
            if reason and submit:
                with st.spinner("Processing..."):
                    try:
                        result = graph.invoke(
                            {
                                "messages": [
                                    ToolMessage(
                                        tool_call_id=last_message.tool_calls[0]["id"],
                                        content=f"API call denied by user. Reasoning: '{reason}'. Continue assisting.",
                                    )
                                ]
                            },
                            st.session_state.config,
                        )
                        process_events(result)
                        st.session_state.pending_approval = None
                        st.session_state.show_reason_input = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing denial: {str(e)}")

def client_main():
    st.header("Chat with Sales Agent")
    display_chat_history()
    if st.session_state.pending_approval:
        handle_tool_approval(*st.session_state.pending_approval)
    if prompt := st.chat_input("What would you like to order?"):
        from langchain_core.messages import HumanMessage
        human_message = HumanMessage(content=prompt)
        st.session_state.messages.append(human_message)
        with st.chat_message("user"):
            st.write(prompt)
        try:
            with st.spinner("Thinking..."):
                events = list(
                    graph.stream(
                        {"messages": st.session_state.messages},
                        st.session_state.config,
                        stream_mode="values",
                    )
                )
                last_event = events[-1]
                tool_call = process_events(last_event)
                if tool_call:
                    snapshot = graph.get_state(st.session_state.config)
                    if snapshot.next:
                        for event in events:
                            st.session_state.pending_approval = (snapshot, event)
                            st.rerun()
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")