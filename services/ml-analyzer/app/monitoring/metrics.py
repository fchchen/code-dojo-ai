from prometheus_client import Counter, Histogram, Gauge

MODEL_LOAD_TIME = Histogram(
    "model_load_seconds",
    "Time to load a model",
    ["model_name"],
)

INFERENCE_DURATION = Histogram(
    "inference_duration_seconds",
    "Time for model inference",
    ["model_name", "endpoint"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

INFERENCE_REQUESTS = Counter(
    "inference_requests_total",
    "Total inference requests",
    ["model_name", "endpoint", "status"],
)

MODELS_LOADED = Gauge(
    "models_loaded",
    "Number of models currently loaded",
)
