"""cx_Oracle compatibility shim using oracledb (thin mode).

Presents oracledb as cx_Oracle for SQLAlchemy 1.4 compatibility.
No Oracle Instant Client needed - uses oracledb thin mode.
"""
import types as _types

try:
    import oracledb as _odb
except ImportError:
    raise ImportError("oracledb is required. Install with: pip install oracledb")

# Re-export everything from oracledb
from oracledb import *  # noqa: F401,F403

for _a in dir(_odb):
    if not _a.startswith('_'):
        globals()[_a] = getattr(_odb, _a)

# cx_Oracle.__future__ module (required by SQLAlchemy cx_oracle dialect)
_future = _types.ModuleType('cx_Oracle.__future__')
_future.dml_ret_array_val = True
__future__ = _future

# Version that passes SQLAlchemy's check (>= 5.2)
__version__ = '8.3.0'
version = '8.3.0'

_oracledb = _odb
