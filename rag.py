import os
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

class InvoiceRAG:

    def __init__(self):

        self.embedder = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
        self.client = chromadb.PersistentClient(
            path=db_path
        )

        self.collection = self.client.get_or_create_collection(
            "invoices"
        )

        self.llm = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )



    def ask(self, question, history=None):

        standalone_question = question
        if history:
            history_text = ""
            for msg in history:
                history_text += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
            condense_prompt = f"""Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question that can be understood without the context of the conversation. Do not answer the question, just rephrase it or output it as is if it is already standalone.

Conversation History:
{history_text}

Follow-up Question:
{question}

Standalone Question:"""
            
            condense_response = self.llm.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": condense_prompt}]
            )
            standalone_question = condense_response.choices[0].message.content.strip()

        embedding = self.embedder.encode(
            standalone_question
        ).tolist()

        filenames = []
        try:
            count = self.collection.count()
            if count > 0:
                results = self.collection.query(
                    query_embeddings=[embedding],
                    n_results=min(5, count)
                )
                context = "\n\n".join(results["documents"][0])
                if results.get("metadatas") and results["metadatas"][0]:
                    filenames = [meta.get("filename") for meta in results["metadatas"][0] if meta and meta.get("filename")]
            else:
                context = ""
        except Exception:
            context = ""

        context_prompt = f"""You are an invoice assistant.

Answer ONLY using the provided Context.
Dont show your process run the process internally and for complex questions solve them and give a summarised answer of your response.
always answer in rs not dollars

Context:
{context}"""

        messages = [{"role": "system", "content": context_prompt}]
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": question})

        response = self.llm.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": sorted(list(set(filenames)))
        }