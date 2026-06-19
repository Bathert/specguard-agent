```python
"""URL slug implementation generated from the URL slug feature contract."""
from __future__ import annotations

import re


# Traces to: Scenario "Normalize a title into a slug", "Collapse repeated separators", "Reject an empty title"
def slugify(value: str) -> str:
    """Return a normalized URL slug or raise ValueError for an empty title."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("title must be a non-empty string")
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return normalized.strip("-")
```
