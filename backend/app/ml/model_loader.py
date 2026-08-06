import os
import pickle
from pathlib import Path
from typing import Any

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "trained_model.pkl"
MODEL_PATH_ENV = "ML_MODEL_PATH"

_model: Any | None = None
_model_loaded = False
_model_error: str | None = None


class ModelLoadError(RuntimeError):
    """Raised when the trained machine-learning model cannot be loaded."""


def get_model_path() -> Path:
    """Return the configured trained-model path."""
    configured_path = os.getenv(MODEL_PATH_ENV)
    if configured_path:
        return Path(configured_path)
    return DEFAULT_MODEL_PATH


def load_model() -> Any | None:
    """Load and cache the trained model once for the current process."""
    global _model, _model_loaded, _model_error

    if _model_loaded:
        return _model

    model_path = get_model_path()
    try:
        with model_path.open("rb") as model_file:
            _model = pickle.load(model_file)
        _model_error = None
    except FileNotFoundError:
        _model = None
        _model_error = f"ML model file not found: {model_path}"
    except (OSError, pickle.PickleError, EOFError, AttributeError, ImportError) as error:
        _model = None
        _model_error = f"Unable to load ML model from {model_path}: {error}"

    _model_loaded = True
    return _model


def get_model() -> Any:
    """Return the cached model or raise a clear model-loading error."""
    model = load_model()
    if model is None:
        raise ModelLoadError(_model_error or "ML model is not available")
    return model


def get_model_load_error() -> str | None:
    """Return the latest model-loading error, if one occurred."""
    load_model()
    return _model_error


def is_model_available() -> bool:
    """Return whether the trained model is available for inference."""
    return load_model() is not None


def reset_model_cache() -> None:
    """Clear the cached model state, primarily for tests and reload workflows."""
    global _model, _model_loaded, _model_error
    _model = None
    _model_loaded = False
    _model_error = None
