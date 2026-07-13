import streamlit as st
from rag import InvoiceRAG

st.set_page_config(page_title="Invoice Assistant", layout="centered")

st.title("Invoice Assistant")
st.write("Ask questions about your uploaded invoices, totals, seller details, line items, and payment terms.")

@st.cache_resource
def load_rag():
    return InvoiceRAG()

rag = load_rag()

question = st.text_input("Ask about your invoices")

if question:
    with st.spinner("Searching"):
        answer = rag.ask(question)
    st.write(answer)