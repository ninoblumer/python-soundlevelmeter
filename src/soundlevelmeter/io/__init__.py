"""Public API for slm.io — I/O controllers, reporter, and display helpers."""
from soundlevelmeter.io.controller import Controller
from soundlevelmeter.io.file_controller import FileController
from soundlevelmeter.io.realtime_controller import RealtimeController
from soundlevelmeter.io.reporter import Reporter
from soundlevelmeter.io.display import make_display_fn

try:
    from soundlevelmeter.io.sounddevice_controller import SounddeviceController
    _has_sounddevice = True
except ImportError:
    _has_sounddevice = False

__all__ = [
    "Controller",
    "FileController",
    "RealtimeController",
    "Reporter",
    "make_display_fn",
    *( ["SounddeviceController"] if _has_sounddevice else [] ),
]