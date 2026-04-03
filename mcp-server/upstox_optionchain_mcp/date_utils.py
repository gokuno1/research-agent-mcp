"""Mirrors com.tradebot.upstox.common.DateUtils.getThursdayDateStringFormat (uses TUESDAY)."""

from __future__ import annotations

from datetime import date, timedelta


def get_expiry_string_like_java() -> str:
    """
    Same logic as DateUtils.getThursdayDateStringFormat():
    next calendar Tuesday on or after today (variable name in Java says Thursday but code uses TUESDAY).
    """
    today = date.today()
    # Monday=0 .. Sunday=6 in Python; Java DayOfWeek: MONDAY=1 .. SUNDAY=7
    # Java TUESDAY.getValue() == 2
    current_iso = today.weekday() + 1  # 1=Mon .. 7=Sun
    days_to_tuesday = 2 - current_iso
    if days_to_tuesday < 0:
        days_to_tuesday += 7
    desired = today + timedelta(days=days_to_tuesday)
    return desired.isoformat()
