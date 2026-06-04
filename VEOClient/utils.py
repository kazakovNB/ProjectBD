import ast
from typing import Any, List

def safe_parse_list(value: Any) -> List[Any]:
    """Accept a Python list or a string representation of a list and return a list.

    This keeps backward compatibility with server responses that used to send lists as strings.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        try:
            parsed = ast.literal_eval(s)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []
