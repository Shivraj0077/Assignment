import streamlit as st
import uuid
from rag import InvoiceRAG

st.set_page_config(page_title="Invoice Assistant", layout="centered")

st.title("Invoice Assistant")

@st.cache_resource
def load_rag():
    return InvoiceRAG()

rag = load_rag()

if "chats" not in st.session_state:
    first_chat_id = str(uuid.uuid4())
    st.session_state.chats = {first_chat_id: []}
    st.session_state.current_chat_id = first_chat_id

st.sidebar.title("Chats")
if st.sidebar.button("New Chat", use_container_width=True):
    new_chat_id = str(uuid.uuid4())
    st.session_state.chats[new_chat_id] = []
    st.session_state.current_chat_id = new_chat_id
    st.rerun()

chat_ids = list(st.session_state.chats.keys())
for idx, cid in enumerate(chat_ids, start=1):
    label = f"Chat {idx}"
    messages = st.session_state.chats[cid]
    if messages:
        first_question = messages[0]["content"]
        label = (first_question[:25] + "...") if len(first_question) > 25 else first_question
    
    if st.sidebar.button(label, key=cid, use_container_width=True):
        st.session_state.current_chat_id = cid
        st.rerun()

if st.sidebar.button("Clear All Chats", use_container_width=True):
    first_chat_id = str(uuid.uuid4())
    st.session_state.chats = {first_chat_id: []}
    st.session_state.current_chat_id = first_chat_id
    st.rerun()

current_messages = st.session_state.chats[st.session_state.current_chat_id]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your invoices..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    history = list(current_messages)
    current_messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Scanning vector store..."):
            result = rag.ask(prompt, history)
        response = result["answer"]
        sources = result["sources"]
        st.markdown(response)
        if sources:
            st.markdown(f"**Sources:** {', '.join(sources)}")
            response_to_save = f"{response}\n\n**Sources:** {', '.join(sources)}"
        else:
            response_to_save = response
    
    current_messages.append({"role": "assistant", "content": response_to_save})
    st.session_state.chats[st.session_state.current_chat_id] = current_messages