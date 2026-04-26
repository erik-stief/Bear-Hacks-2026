def detect_provider(message) -> str:
    header_names = {key.lower() for key in message.keys()}

    if "x-google-smtp-source" in header_names or "x-received" in header_names:
        return "gmail"

    if "x-microsoft-antispam" in header_names or "x-ms-exchange-organization-authas" in header_names:
        return "microsoft"

    if "x-yahooforwarded" in header_names or "x-apparently-to" in header_names:
        return "yahoo"

    return "unknown"
