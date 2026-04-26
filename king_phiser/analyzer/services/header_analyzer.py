from email.parser import BytesHeaderParser
from email.policy import default

from .auth_parser import extract_auth_results
from .header_extractors import decode_mime_value, extract_address
from .provider_check import detect_provider


UNIVERSAL_SINGLE_HEADERS = [
    "From",
    "To",
    "Reply-To",
    "Return-Path",
    "Delivered-To",
    "Subject",
    "Message-ID",
    "Date",
]

UNIVERSAL_MULTI_HEADERS = [
    "Received",
    "Authentication-Results",
    "ARC-Authentication-Results",
    "DKIM-Signature",
    "Received-SPF",
]

PROVIDER_OPTIONAL_HEADERS = [
    "X-Received",
    "X-Google-Smtp-Source",
    "ARC-Seal",
    "ARC-Message-Signature",
    "X-Microsoft-Antispam",
    "X-MS-Exchange-Organization-AuthAs",
    "X-Apparently-To",
    "X-YahooForwarded",
]


def analyze_headers(raw_headers: str) -> dict:
    parser = BytesHeaderParser(policy=default)
    message = parser.parsebytes(raw_headers.encode("utf-8", errors="ignore"))

    provider = detect_provider(message)

    auth_results = message.get_all("Authentication-Results", [])
    arc_auth_results = message.get_all("ARC-Authentication-Results", [])
    received_headers = message.get_all("Received", [])

    raw_headers_map = {}

    for name in UNIVERSAL_SINGLE_HEADERS:
        raw_headers_map[name] = message.get_all(name, [])

    for name in UNIVERSAL_MULTI_HEADERS:
        raw_headers_map[name] = message.get_all(name, [])

    for name in PROVIDER_OPTIONAL_HEADERS:
        values = message.get_all(name, [])
        if values:
            raw_headers_map[name] = values

    return {
        "provider_hint": provider,
        "from": extract_address(message.get("From", "")),
        "to": extract_address(message.get("To", "")),
        "reply_to": extract_address(message.get("Reply-To", "")),
        "return_path": extract_address(message.get("Return-Path", "")),
        "delivered_to": message.get_all("Delivered-To", []),
        "subject": decode_mime_value(str(message.get("Subject", ""))),
        "message_id": str(message.get("Message-ID", "")),
        "date": str(message.get("Date", "")),
        "received_chain": received_headers,
        "received_count": len(received_headers),
        "authentication_results": [
            extract_auth_results(value) for value in auth_results
        ],
        "arc_authentication_results": [
            extract_auth_results(value) for value in arc_auth_results
        ],
        "provider_headers": {
            name: raw_headers_map.get(name, [])
            for name in PROVIDER_OPTIONAL_HEADERS
            if name in raw_headers_map
        },
        "raw_interesting_headers": raw_headers_map,
    }
