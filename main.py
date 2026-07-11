from embeddings.embedding import EmbeddingGenerator
from rag import InvoiceRAG


generator = EmbeddingGenerator()
generator.generate("structured")


rag = InvoiceRAG()

while True:

    q = input("Ask: ")

    if q == "exit":
        break

    print(rag.ask(q))