from pathlib import Path
from pypdf import PdfReader
import json


class PDFParser:

    def __init__(self, output_folder):

        self.input_folder = Path("pdfs")
        self.output_folder = Path(output_folder)

        self.output_folder.mkdir(exist_ok=True)

    def parse_all(self):

        for pdf in self.input_folder.glob("*.pdf"):
            self.parse_pdf(pdf)

    def parse_pdf(self, pdf_path):

        reader = PdfReader(pdf_path)

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):

            pages.append({
                "page": page_number,
                "text": page.extract_text() or ""
            })

        parsed_document = {

            "filename": pdf_path.name,

            "num_pages": len(reader.pages),

            "pages": pages
        }

        output_file = self.output_folder / f"{pdf_path.stem}.json"

        with open(output_file, "w", encoding="utf-8") as f:

            json.dump(
                parsed_document,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"Parsed {pdf_path.name}")