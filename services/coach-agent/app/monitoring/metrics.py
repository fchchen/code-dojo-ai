from prometheus_client import Counter, Gauge, Histogram

SUBMISSIONS_TOTAL = Counter(
    "coach_submissions_total",
    "Total submissions processed by coach agent",
)

SUBMISSIONS_FAILED = Counter(
    "coach_submissions_failed_total",
    "Total submissions that failed",
)

SUBMISSION_DURATION = Histogram(
    "coach_submission_duration_seconds",
    "Submission processing duration in seconds",
)

ACTIVE_STREAMS = Gauge(
    "coach_active_streams",
    "Current number of active stream requests",
)
