# -*- coding: utf-8 -*-
"""Watchlist weakness alert based on 55-day analysis history."""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from src.storage import DatabaseManager

logger = logging.getLogger(__name__)

# 55 trading days ≈ 80 calendar days (with weekends/holidays buffer)
LOOKBACK_CALENDAR_DAYS = 80
MIN_DATA_POINTS = 10
WEAK_SCORE_THRESHOLD = 40


def check_weak_stocks(
    stock_codes: List[str],
    storage: Optional[DatabaseManager] = None,
) -> List[Tuple[str, float, List[int]]]:
    """Check which stocks have avg score below threshold over ~55 trading days.

    Returns:
        List of (code, avg_score, recent_scores) for weak stocks.
    """
    if storage is None:
        storage = DatabaseManager()

    weak = []
    for code in stock_codes:
        records = storage.get_analysis_history(
            code=code,
            days=LOOKBACK_CALENDAR_DAYS,
            limit=55,
        )
        scores = [
            r.sentiment_score
            for r in records
            if r.sentiment_score is not None
        ]
        if len(scores) < MIN_DATA_POINTS:
            continue

        avg = sum(scores) / len(scores)
        if avg < WEAK_SCORE_THRESHOLD:
            recent_5 = scores[:5]
            weak.append((code, round(avg, 1), recent_5))

    return weak


def format_weak_alert(weak_stocks: List[Tuple[str, float, List[int]]]) -> str:
    """Format weakness alert message for notification."""
    lines = [
        "## ⚠️ 汰弱观察名单",
        "",
        f"> 以下标的近 55 个交易日平均评分低于 {WEAK_SCORE_THRESHOLD}，建议评估是否替换。",
        "",
    ]
    for code, avg, recent in weak_stocks:
        recent_str = ", ".join(str(s) for s in recent)
        lines.append(f"**{code}** — 55 日均分 **{avg}** （近期: {recent_str}）")

    return "\n".join(lines)
