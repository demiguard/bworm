from typing import Any

def escape(value: Any) -> str:
  if isinstance(value, str):
    return f"\"{value}\""
  if isinstance(value, int):
    return str(value)

  raise Exception("NOT IMPLEMENTED!")
