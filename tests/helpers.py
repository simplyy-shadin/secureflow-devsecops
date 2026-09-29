def synthetic_password() -> str:
    """Return a deterministic test-only password without storing it as one literal."""
    return "-".join(("Correct", "Horse", "Battery", "Staple", "42"))
