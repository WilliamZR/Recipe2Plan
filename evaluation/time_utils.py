# time_utils.py
"""Time formatting and parsing utilities."""

def format_time_stamp(time_seconds: float) -> str:
    """
    Format seconds into an HH:MM:SS string.

    Args:
        time_seconds: Time in seconds.

    Returns:
        Formatted time string.
    """
    hour = int(time_seconds // 3600)
    minute = int((time_seconds % 3600) // 60)
    second = int(time_seconds % 60)
    return f'{hour:02}:{minute:02}:{second:02}'

def format_execution_time(time_seconds: float) -> str:
    """
    Choose the most appropriate time unit (hours, minutes, seconds) to represent the time.

    Args:
        time_seconds: Time in seconds.

    Returns:
        Formatted time string.
    """
    if time_seconds >= 3600:
        return f'{time_seconds // 3600:.0f} hour(s)'
    elif time_seconds >= 60:
        return f'{time_seconds // 60:.0f} min'
    elif time_seconds > 0:
        return f'{time_seconds:.0f} sec'
    else:
        return '0 sec'