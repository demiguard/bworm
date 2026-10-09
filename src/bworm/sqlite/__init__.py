from dataclasses import make_dataclass, is_dataclass, fields, Field, dataclass
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

class BwormDataclass:
  _connection: sqlite3.Connection

  @classmethod
  def select(cls):
    return [cls(*res) for res in cls._connection.execute(f"SELECT * FROM {cls.__name__}")]

  def save(self):
    field_names = []
    field_values = []

    for field in fields(self): #type: ignore
      field_names.append(field.name)
      field_values.append(core.escape(self.__getattribute__(field.name)))

    self._connection.execute(f"INSERT INTO {self.__class__.__name__}({', '.join(field_names)}) VALUES ({', '.join(field_values)})")
    self._connection.commit()

def map_from_sqlite_type(typename: str) -> Type:
  match typename:
    case "TEXT":
      return str
    case "INT":
      return int
  raise Exception("Unknown type!")

def map_to_sqlite_type(type_: type | str) -> str:
  if type_ is str:
    return "TEXT"
  if type_ is int:
    return "INT"

  raise Exception("Unknown Type!")

def describe_table_query(table_name:str):
  return f"""PRAGMA table_info({table_name})"""

def extract_type(response_tuple: Tuple[int, str, str, int, Any, int]):
  return (response_tuple[1], map_from_sqlite_type(response_tuple[2]))

def map_field_to_sqlite(field: Field) -> str:
  return f"{field.name} {map_to_sqlite_type(field.type)}"

def read_table_from(conn: sqlite3.Connection, table_name: str):
  fields = [extract_type(res) for res in conn.execute(describe_table_query(table_name))]

  return make_dataclass(
    table_name, fields, bases=(BwormDataclass,), namespace={'_connection' : conn}
  )

def create_table_query(dataclass_type: Type):
  return (
    f"""
CREATE TABLE IF NOT EXISTS {dataclass_type.__name__}(
  {',\n'.join([map_field_to_sqlite(field) for field in fields(dataclass_type)])}
)"""
)

class DatabaseModuleType(ModuleType):
  def __setattr__(self, name: str, value: Any) -> None:
    if name.startswith('__'):
      return super().__setattr__(name, value)

    if not is_dataclass(value):
      error_message = f"key {name} - Value {value} is not a dataclass"
      raise TypeError(error_message)

    if not isinstance(value, type):
      raise TypeError(f"Value is an instance of a dataclass, not the type!")

    if not issubclass(value, BwormDataclass):
      value = make_dataclass(
        value.__name__,
        [(f.name, f.type) for f in fields(value)],
        bases=(BwormDataclass,),
        namespace={"_connection" : self.__connection}
      )
    else:
      value._connection = self.__connection

    self.__connection.execute(create_table_query(value))

    return super().__setattr__(name, value)


class SQLiteLoader(Loader):
  def create_module(self, spec: ModuleSpec) -> ModuleType | None:
    return DatabaseModuleType(spec.name)

  def exec_module(self, module: ModuleType) -> None:
    if module.__spec__ is None or module.__spec__.origin is None:
      print("Spec is none!")
      raise ImportError("Module spec is None???")

    connection = sqlite3.connect(module.__spec__.origin)

    # we set the attribute directly because the modules __setattr__ have been
    # overwritten
    module.__dict__['_DatabaseModuleType__connection'] = connection

    tables = [value for value, in connection.execute(SHOW_TABLE_QUERY)]

    for table_name in tables:
      module.__dict__[table_name] = read_table_from(connection, table_name)

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
