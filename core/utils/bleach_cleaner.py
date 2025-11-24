import bleach

SAFE_TAGS = []
SAFE_ATTRS = {}
SAFE_PROTOCOLS = ["http", "https"]

def sanitize_input(value: str):
    """Cleans a string using bleach, returns tuple(clean_text, is_safe)."""
    cleaned = bleach.clean(
        value,
        tags=SAFE_TAGS,
        attributes=SAFE_ATTRS,
        protocols=SAFE_PROTOCOLS,
        strip=True
    )

    # If cleaned version is different → user entered unsafe HTML/JS
    is_safe = (cleaned == value)
    return cleaned, is_safe
