"""Simple progress indicator using stdlib only."""

import sys
from datetime import datetime


def print_progress(
    turn: int, total: int, interviewer: str, interviewee: str, start_time: datetime
):
    """Print single-line progress indicator that updates in place."""
    elapsed = datetime.now() - start_time
    minutes, seconds = divmod(int(elapsed.total_seconds()), 60)
    time_str = f"{minutes}m {seconds:02d}s" if minutes > 0 else f"{seconds}s"

    line = f"\r\U0001f916 Turn {turn}/{total} | {interviewer} \u2194 {interviewee} | {time_str}"
    sys.stdout.write(line)
    sys.stdout.flush()


def clear_progress():
    """Clear the progress line."""
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
