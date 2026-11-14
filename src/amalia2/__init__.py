"""
Amalia 2.0
Modern Python SDK & CLI for Amália — Portugal's National LLM
"""

__version__ = "0.1.0-alpha"
__author__ = "Joshua Almeida"

from .client import AmaliaClient, StreamEvent
from .config import DEFAULT_BASE_URL, AmaliaConfig, load_config
from .errors import AmaliaAuthError, AmaliaError, AmaliaHTTPError

__all__ = [
    "DEFAULT_BASE_URL",
    "AmaliaAuthError",
    "AmaliaClient",
    "AmaliaConfig",
    "AmaliaError",
    "AmaliaHTTPError",
    "StreamEvent",
    "__version__",
    "load_config",
]
