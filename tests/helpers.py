def synthetic_password() -> str:
    """Return a deterministic test-only password without storing it as one literal."""
    parts = ("Correct", "Horse", "Battery", "Staple", "42")
    return "-".join(parts)
