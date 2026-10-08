from dataclasses import make_dataclass

import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, Sequence, Type, Tuple

from bworm import core

# Required imports
try:
  import sqlite3
except ImportError as e:
  raise ImportError("Missing Required package - sqlite3")

# Module code

### RAW Queries
SHOW_TABLE_QUERY = """
  SELECT name
  FROM sqlite_master
  WHERE
    type = 'table' AND
    name NOT LIKE 'sqlite_%';
"""

def map_sqlite_type(typename: str) -> Type:
  match typename:
    case "TEXT":
      return str
    case "INT":
      return int

  raise Exception("Unknown type!")

def DESCRIBE_TABLE_QUERY(table_name:str):
  return f"""PRAGMA table_info({table_name})"""

def extract_type(response_tuple: Tuple[int, str, str, int, Any, int]):
  return (response_tuple[1], map_sqlite_type(response_tuple[2]))

def read_table_from(conn: sqlite3.Connection, table_name: str):
  fields = [extract_type(res) for res in conn.execute(DESCRIBE_TABLE_QUERY(table_name))]

  return make_dataclass(
    table_name, fields
  )


class SQLiteLoader(Loader):
  def exec_module(self, module: ModuleType) -> None:
    if module.__spec__ is None or module.__spec__.origin is None:
      print("Spec is none!")
      raise ImportError("Module spec is None???")

    connection = sqlite3.connect(module.__spec__.origin)

    setattr(module, '__connection', connection)

    tables = [value for value, in connection.execute(SHOW_TABLE_QUERY)]

    for table_name in tables:
      setattr(module, table_name, read_table_from(connection, table_name))

    return None


class SQLiteFinder(MetaPathFinder):
  def find_spec(self, fullname: str, path: Sequence[str] | None, target: ModuleType | None = None) -> ModuleSpec | None:
    names = fullname.split('.')

    if len(names) != 3 or names[0] != "bworm" or names[1] != "sqlite":
      return None

    database_name = names[2]

    return ModuleSpec(
      name=fullname, loader=SQLiteLoader(), origin=f"{database_name}.sqlite"
    )

sys.meta_path.append(SQLiteFinder())