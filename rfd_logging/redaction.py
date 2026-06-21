from __future__ import annotations

REDACT_FIELDS: frozenset[str] = frozenset({
    "password", "passwd", "pwd",
    "token", "api_key", "apikey", "api_token",
    "secret", "secret_key",
    "authorization", "auth",
    "private_key",
    "credential", "credentials",
    "access_token", "refresh_token",
})

_REDACTED = "[REDACTED]"


def redact(
    extra: dict,
    fields: frozenset[str] | None = None,
) -> dict:
    """
    Return a copy of extra with sensitive field values replaced by '[REDACTED]'.

    Matching is case-insensitive. Input dict is never mutated.
    Nested dicts inside values are not recursed — only top-level keys are redacted.

    Args:
        extra:  Dict to redact. Nested dicts are not recursed.
        fields: Field names to redact. Defaults to REDACT_FIELDS.

    Usage:
        safe = redact({"api_key": "abc123", "service": "github"})
        # → {"api_key": "[REDACTED]", "service": "github"}
    """
    target = fields if fields is not None else REDACT_FIELDS
    return {
        k: _REDACTED if k.lower() in target else v
        for k, v in extra.items()
    }
