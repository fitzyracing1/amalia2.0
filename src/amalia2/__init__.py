"""
Amalia 2.0
Modern Python SDK & CLI for Amália — Portugal's National LLM
"""

__version__ = "0.1.0-alpha"
__author__ = "Joshua Almeida"

from .client import AmaliaClient

__all__ = ["AmaliaClient", "__version__"]