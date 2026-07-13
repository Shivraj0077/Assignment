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

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.client.get_collection(
            "invoices"
        )

        self.llm = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )



    def ask(self, question):

        embedding = self.embedder.encode(
            question
        ).tolist()

        results = self.collection.query(

            query_embeddings=[embedding],

            n_results=5

        )

        context = "\n\n".join(
            results["documents"][0]
        )

        prompt = f"""
You are an invoice assistant.

Answer ONLY using the context.

Dont show your process run the process 
internally and for complex questions solve them and 
give a summarised answer of your response.
always answer in rs not dollars

Context:

{context}

Question:

{question}
"""

        response = self.llm.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=[

                {

                    "role":"user",

                    "content":prompt

                }

            ]

        )

        

        return response.choices[0].message.content