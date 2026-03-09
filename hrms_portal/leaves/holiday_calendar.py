"""Holiday calendar and leave-day calculation helpers."""

from datetime import date, timedelta

# Holidays that should not be counted for casual leave.
CASUAL_LEAVE_EXCLUDED_HOLIDAYS = {
    date(2026, 1, 23),
    date(2026, 4, 3),
    date(2026, 5, 27),
    date(2026, 7, 16),
    date(2026, 8, 15),
    date(2026, 9, 4),
    date(2026, 9, 14),
    date(2026, 10, 2),
    date(2026, 10, 19),
    date(2026, 10, 20),
    date(2026, 12, 25),
}


def get_chargeable_leave_days(start_date: date, end_date: date, leave_type: str) -> int:
    """Return leave days to charge after applying holiday rules."""
    if not start_date or not end_date or end_date < start_date:
        return 0

    total_days = (end_date - start_date).days + 1
    if leave_type != 'casual':
        return total_days

    excluded_days = 0
    current_day = start_date
    while current_day <= end_date:
        if current_day in CASUAL_LEAVE_EXCLUDED_HOLIDAYS:
            excluded_days += 1
        current_day += timedelta(days=1)

    return max(total_days - excluded_days, 0)


def get_excluded_holiday_strings() -> list[str]:
    """Return ISO date strings for templates/JS usage."""
    return sorted(d.isoformat() for d in CASUAL_LEAVE_EXCLUDED_HOLIDAYS)
