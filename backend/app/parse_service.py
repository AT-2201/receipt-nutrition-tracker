import re

SKIP_WORDS = [
    "subtotal", "sub total", "tax", "total", "balance", 
    "cash", "change", "visa", "mastercard", "debit", 
    "credit", "payment", "thank", "store", "supercenter"
]

# List of known units for receipts
UNITS = ["lb", "lbs", "oz", "kg", "g", "pk", "ct", "gal", "loaf"]

def fix_ocr_units(line: str) -> str:
    """
    Fix common OCR mistakes with units such as:
    'G AL' -> 'GAL', 'G A L' -> 'GAL', '6AL' -> 'GAL'
    """
    # Remove spaces inside units
    line = line.replace("G AL", "GAL")
    line = line.replace("G A L", "GAL")
    line = line.replace("GA L", "GAL")
    line = line.replace("GAl", "GAL")
    line = line.replace("6AL", "GAL")  # OCR often reads G as 6

    # Normalize lowercase
    line = line.lower()

    return line


def clean_text(text: str) -> list:
    """
    Clean raw OCR text and split into lines.
    Remove empty lines and spaces.
    """
    lines = text.split("\n")
    cleaned = [line.strip() for line in lines if line.strip()]
    return cleaned


def is_item_line(line: str) -> bool:
    """
    Determine if a line looks like an item line.
    Must contain a price AND should not be subtotal/tax/total/etc.
    """

    lower = line.lower()

    # Skip known non-item lines
    for word in SKIP_WORDS:
        if word in lower:
            return False

    # Must contain price pattern at end: e.g., 0.99, 12.55
    price_pattern = r"\d+\.\d{2}$"
    if not re.search(price_pattern, line):
        return False

    return True



def parse_line(line: str) -> dict:
    """
    Parse a single receipt line into structured fields.
    Example:
        'BANANAS 1.20 LB 0.68'
    """
    # PRICE = last float on the line
    price_match = re.search(r"(\d+\.\d{2})$", line)
    if not price_match:
        return None
    price = float(price_match.group(1))

    # Remove price from the line
    without_price = line[:price_match.start()].strip()

    # Quantity + unit pattern, e.g., "1.20 LB", "1 PK"
    qty_unit_pattern = r"(\d+(\.\d+)?)[\s]*(gal|lb|lbs|oz|kg|g|pk|ct|loaf)"
    qty_match = re.search(qty_unit_pattern, without_price, re.IGNORECASE)

    if qty_match:
        quantity = float(qty_match.group(1))
        unit = qty_match.group(3).lower()

        # Item name = everything before quantity
        item_name = without_price[:qty_match.start()].strip().lower()

    else:
        # If no quantity/unit: treat as 1 unit (typical for packaged items)
        quantity = 1.0
        unit = "unit"
        item_name = without_price.lower()
        
    if "milk" in item_name and unit == "g":
        unit = "gal"


    return {
        "item_name": item_name,
        "quantity": quantity,
        "unit": unit,
        "price": price
    }


def parse_receipt_text(raw_text: str) -> list:
    """
    Parse full OCR raw text into structured receipt items.
    """
    raw_lines = clean_text(raw_text)
    lines = [fix_ocr_units(line) for line in raw_lines]
    items = []

    for line in lines:
        if is_item_line(line):
            parsed = parse_line(line)
            if parsed:
                items.append(parsed)

    return items
