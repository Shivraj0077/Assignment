import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        db_path = str(Path(__file__).parent.parent / "chroma_db")
        self.client = chromadb.PersistentClient(
            path=db_path
        )

        try:
            self.client.delete_collection("invoices")
        except:
            pass

        self.collection = self.client.create_collection(
            "invoices"
        )

    def generate(self, structured_folder):

        structured_folder = Path(structured_folder)

        doc_id = 0

        for file in structured_folder.glob("*.json"):

            with open(file, "r", encoding="utf-8") as f:

                invoice = json.load(f)


            text = json.dumps(
                invoice,
                indent=2,
                ensure_ascii=False
            )

            embedding = self.model.encode(
                text
            ).tolist()

            self.collection.add(

                ids=[str(doc_id)],

                documents=[text],

                embeddings=[embedding],

                metadatas=[

                    {

                        "invoice_number":
                        invoice["invoice_number"],

                        "filename":
                        invoice["filename"]

                    }

                ]

            )

            doc_id += 1

        print("Embedding Complete")