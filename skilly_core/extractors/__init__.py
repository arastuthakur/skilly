"""
Extractors module for Skilly.
"""

from skilly_core.extractors.base import BaseExtractor
from skilly_core.extractors.manifest_extractor import ManifestExtractor
from skilly_core.extractors.python_extractor import PythonASTExtractor
from skilly_core.extractors.javascript_extractor import JavaScriptExtractor
from skilly_core.extractors.polyglot_extractor import PolyglotExtractor
from skilly_core.extractors.universal_engine import UniversalPolyglotExtractor

__all__ = [
    "BaseExtractor",
    "ManifestExtractor",
    "PythonASTExtractor",
    "JavaScriptExtractor",
    "PolyglotExtractor",
    "UniversalPolyglotExtractor",
]
