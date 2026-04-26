from email.header import decode_header
from email.utils import parseaddr


def decode_mime_value(value):
    if not value:
        return ""

    decoded_parts = decode_header(value)
    result = []

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or "utf-8", errors="ignore"))
        else:
            result.append(part)

    return "".join(result)


def extract_address(value):
    if not value:
        return {
            "raw": "",
            "name": "",
            "email": "",
            "domain": "",
        }

    name, email_address = parseaddr(value)
    decoded_name = decode_mime_value(name)
    domain = email_address.split("@")[-1].lower() if "@" in email_address else ""

    return {
        "raw": value,
        "name": decoded_name,
        "email": email_address,
        "domain": domain,
    }
