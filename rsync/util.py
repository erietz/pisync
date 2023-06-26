from datetime import datetime


def get_time_stamp() -> str:
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d-%H-%M-%S")
    return str(stamp)
