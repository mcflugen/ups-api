from ._version import get_versions
from .xav import Address, UpsXav

__all__ = ["Address", "UpsXav"]

__version__ = get_versions()["version"]
del get_versions
