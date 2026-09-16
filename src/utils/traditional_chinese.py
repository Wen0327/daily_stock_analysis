# -*- coding: utf-8 -*-
"""Simplified-to-Traditional Chinese conversion for notification content."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

_TRADITIONAL_LANGUAGES = frozenset({"zh-tw", "zh_tw", "zh-hant", "zh_hant"})


@lru_cache(maxsize=1)
def _get_converter():
    try:
        from opencc import OpenCC
        return OpenCC("s2t")
    except ImportError:
        logger.warning("opencc-python-reimplemented not installed, skipping traditional conversion")
        return None


def _is_traditional_configured() -> bool:
    lang = os.getenv("REPORT_LANGUAGE", "").strip().lower()
    return lang in _TRADITIONAL_LANGUAGES


def maybe_convert_traditional(text: Optional[str]) -> str:
    """Convert simplified Chinese to traditional if REPORT_LANGUAGE is zh-tw."""
    if not text or not _is_traditional_configured():
        return text or ""
    converter = _get_converter()
    if converter is None:
        return text
    return converter.convert(text)
