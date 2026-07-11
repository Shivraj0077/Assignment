import json
import re
from pathlib import Path
from item_parserer.item_parser import ItemParser

class InvoiceStructurer:

    def __init__(self, parsed_folder, structured_folder):

        self.parsed_folder = Path(parsed_folder)
        self.structured_folder = Path(structured_folder)

        self.structured_folder.mkdir(exist_ok=True)

    def structure_all(self):

        for file in self.parsed_folder.glob("*.json"):
            self.structure_invoice(file)

    def structure_invoice(self, file_path):

        with open(file_path, "r", encoding="utf-8") as f:
            parsed = json.load(f)

        text = "\n".join(
            page["text"] for page in parsed["pages"]
        )

        invoice = {
            "filename": parsed["filename"],
            "invoice_number": self.find(r"Invoice no:\s*(.*)", text),
            "invoice_date": self.find(r"Date of issue:(.*)", text),
            "due_date": self.find(r"Due date:\s*(.*)", text),
            "po_number": self.find(r"PO number:\s*(.*)", text),
            "payment_terms": self.find(r"Payment terms:(.*)", text),

            "seller": self.extract_between(
                text,
                "Seller:",
                "Client:"
            ),

            "client": self.extract_between(
                text,
                "Client:",
                "ITEMS"
            ),

            "items": self.extract_between(
                text,
                "ITEMS",
                "SUMMARY"
            ),

            "summary": self.extract_between(
                text,
                "SUMMARY",
                "Notes:"
            )
        }

        item_parser = ItemParser()

        invoice["items"] = item_parser.parse(invoice["items"])

        out = self.structured_folder / file_path.name

        with open(out, "w", encoding="utf-8") as f:
            json.dump(invoice, f, indent=4, ensure_ascii=False)

        print(f"Structured {file_path.name}")

    def find(self, pattern, text):

        m = re.search(pattern, text)

        return m.group(1).strip() if m else ""

    def extract_between(self, text, start, end):

        m = re.search(
            rf"{re.escape(start)}(.*?){re.escape(end)}",
            text,
            re.DOTALL
        )

        return m.group(1).strip() if m else ""

