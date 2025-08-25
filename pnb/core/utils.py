from datetime import datetime, timezone


def humanize_date(dt: datetime) -> str:
    return dt.strftime("%b %d, %Y at %I:%M %p")


def humanize_duration(seconds: int) -> str:
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)

    parts = []
    if hrs:
        parts.append(f"{hrs} hour{'s' if hrs > 1 else ''}")
    if mins:
        parts.append(f"{mins} minute{'s' if mins > 1 else ''}")
    if secs or not parts:
        parts.append(f"{secs} second{'s' if secs > 1 else ''}")

    return " ".join(parts)