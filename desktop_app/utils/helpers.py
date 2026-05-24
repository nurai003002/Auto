"""
AutoTrack — Helper utilities.
"""
import platform


def app_font_family() -> str:
    """Return the best available font family for the current platform."""
    system = platform.system()
    if system == "Windows":
        return "Segoe UI"
    elif system == "Darwin":
        return "SF Pro Display"
    else:
        return "Arial"
