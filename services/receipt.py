from io import BytesIO
from fpdf import FPDF
from services.tz import now_nigeria


class ReceiptPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "VendorIQ Receipt", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Generated {now_nigeria().strftime('%b %d, %Y %I:%M %p')}", align="C")


def generate_receipt(
    business_name: str,
    receipt_type: str,
    item: str,
    amount: int,
    quantity: int | None = None,
    customer: str | None = None,
    note: str | None = None,
    receipt_number: str | None = None,
) -> bytes:
    pdf = ReceiptPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, business_name, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 10)
    labels = [
        ("Receipt #", receipt_number or f"VIQ-{now_nigeria().strftime('%y%m%d%H%M%S')}"),
        ("Type", receipt_type.title()),
        ("Item", item),
    ]
    if quantity:
        labels.append(("Quantity", str(quantity)))
    if customer:
        labels.append(("Customer", customer))
    labels.append(("Amount", f"N{amount:,}"))
    if note:
        labels.append(("Note", note))

    for label, value in labels:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(40, 7, label, new_x="END")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, value, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Thank you for using VendorIQ!", align="C")

    return pdf.output()


def generate_combined_receipt(
    business_name: str,
    receipt_type: str,
    items: list,
    total: int,
    customer: str | None = None,
    receipt_number: str | None = None,
) -> bytes:
    pdf = ReceiptPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, business_name, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    labels = [
        ("Receipt #", receipt_number or f"VIQ-{now_nigeria().strftime('%y%m%d%H%M%S')}"),
        ("Type", receipt_type.title()),
    ]
    if customer:
        labels.append(("Customer", customer))

    for label, value in labels:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(40, 7, label, new_x="END")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, value, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "Items:", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for i, entry in enumerate(items, 1):
        line = f"  {i}. {entry.get('item', 'Goods')}"
        qty = entry.get("quantity")
        if qty:
            line += f" x{qty}"
        line += f" — N{entry['amount']:,}"
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, line, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"Total: N{total:,}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Thank you for using VendorIQ!", align="C")

    return pdf.output()
