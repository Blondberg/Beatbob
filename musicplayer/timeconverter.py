def s_to_hhmmss(seconds: int = 0) -> str:
    """Converts seconds into HH:MM:SS

    Args:
        seconds (int, optional): Amount to seconds to convert. Defaults to 0.

    Returns:
        str: time representation
    """
    # get min and seconds first
    mm, ss = divmod(seconds, 60)
    # Get hours
    hh, mm = divmod(mm, 60)

    return f"{hh}:{mm}:{ss}" if hh > 0 else f"{mm}:{ss}"
