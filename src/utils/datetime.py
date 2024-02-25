from datetime import date


def today_is_workday() -> bool:
    if date.today().weekday() > 4:
        return False
    return True
