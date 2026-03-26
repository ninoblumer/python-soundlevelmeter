"""Abstract base class for real-time audio controllers."""
from __future__ import annotations

from abc import abstractmethod

from soundlevelmeter.io.controller import Controller


class RealtimeController(Controller):
    """Extension of Controller for live audio streams.

    Adds explicit stream lifecycle (``start`` / ``stop``) and device
    enumeration on top of the pull-based ``read_block`` contract defined
    by :class:`~slm.io.controller.Controller`.

    Subclasses must implement :meth:`list_devices`, :meth:`start`, and the
    abstract methods inherited from :class:`~slm.io.controller.Controller`
    (``read_block``, ``stop``, ``calibrate``).
    """

    @staticmethod
    @abstractmethod
    def list_devices() -> list[dict]:
        """Return all available input devices.

        Each entry is a dict with at minimum:

        * ``'index'`` – device index accepted by ``__init__``
        * ``'name'`` – human-readable device name
        * ``'max_input_channels'`` – number of input channels
        * ``'default_samplerate'`` – device default sample rate (float)
        """
        ...

    @abstractmethod
    def start(self) -> None:
        """Arm the audio stream.

        Must be called before the first :meth:`read_block` call.
        Idempotent implementations are encouraged but not required.
        """
        ...
