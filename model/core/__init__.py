"""Core package exports."""

def __getattr__(name: str):
    if name == "Core":
        from .ticks import Core

        return Core
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
