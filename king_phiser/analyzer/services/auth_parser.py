import re


def extract_auth_results(header_value):
    if not header_value:
        return {
            "raw": "",
            "spf": None,
            "dkim": None,
            "dmarc": None,
        }

    def find_result(label):
        match = re.search(rf"{label}\s*=\s*([a-zA-Z]+)", header_value, re.IGNORECASE)
        return match.group(1).lower() if match else None

    return {
        "raw": header_value,
        "spf": find_result("spf"),
        "dkim": find_result("dkim"),
        "dmarc": find_result("dmarc"),
    }
