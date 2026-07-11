import re


class ItemParser:

    def parse(self, items_text):

        if not items_text:
            return []


        items_text = re.sub(
            r"No\.\s*Description.*?Gross worth",
            "",
            items_text,
            flags=re.DOTALL
        ).strip()


        blocks = re.split(r"\n(?=\d+\.)", items_text)

        items = []

        for block in blocks:

            block = block.strip()

            if not block:
                continue

            item = self.parse_item(block)

            if item:
                items.append(item)

        return items

    def parse_item(self, block):

        lines = [l.strip() for l in block.split("\n") if l.strip()]

        first = lines[0]

        m = re.match(r"(\d+)\.\s*(.*)", first)

        if not m:
            return None

        item_no = int(m.group(1))

        description = [m.group(2)]

        for line in lines[1:-1]:
            description.append(line)

        description = " ".join(description)

        numeric = lines[-1]

        tokens = numeric.split()

        qty = tokens[0]

        unit = tokens[1]

        vat_index = next(i for i, t in enumerate(tokens) if "%" in t)

        vat = tokens[vat_index]

        gross = " ".join(tokens[vat_index + 1:])

        net_price = " ".join(tokens[2:4])

        net_worth = " ".join(tokens[4:vat_index])

        return {
            "item_no": item_no,
            "description": description,
            "quantity": qty,
            "unit": unit,
            "net_price": net_price,
            "net_worth": net_worth,
            "vat": vat,
            "gross_worth": gross
        }