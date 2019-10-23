from ._version import get_versions
from .xav import Address, UpsCredentials, UpsXav, UpsXavBatch

__all__ = ["Address", "UpsCredentials", "UpsXav", "UpsXavBatch"]

__version__ = get_versions()["version"]
del get_versions
