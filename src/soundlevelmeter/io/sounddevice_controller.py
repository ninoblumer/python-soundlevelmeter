"""Real-time audio controller backed by sounddevice (PortAudio).

Works on Windows (WASAPI/MME/DirectSound/ASIO), macOS (CoreAudio),
and Linux (ALSA/PulseAudio/JACK) without any additional dependencies
beyond the ``sounddevice`` package.
"""
from __future__ import annotations

import queue
import threading

import numpy as np
try:
    import sounddevice as sd
except ImportError as _exc:
    raise ImportError(
        "Real-time audio requires the sounddevice package. "
        "Install it with: pip install sounddevice"
    ) from _exc

from slm.io.realtime_controller import RealtimeController


class SounddeviceController(RealtimeController):
    """Cross-platform real-time audio controller using PortAudio via sounddevice.

    The PortAudio callback runs on a dedicated OS audio thread and pushes
    blocks into a bounded :class:`queue.Queue`.  :meth:`read_block` blocks
    on the queue (with a short timeout) so the engine's main-thread loop
    stays responsive to :meth:`stop` and ``KeyboardInterrupt``.

    Parameters
    ----------
    device:
        PortAudio device index or substring of a device name.  ``None``
        uses the system default input device.
    samplerate:
        Sample rate in Hz (default 48 000).
    blocksize:
        Samples per block delivered to the engine (default 1 024).
    channels:
        Number of input channels (default 1).
    dtype:
        Sample format passed to sounddevice (default ``'float32'``).
    queue_maxsize:
        Maximum number of blocks buffered between the callback and
        :meth:`read_block`.  If the engine falls behind, excess blocks
        are dropped and :attr:`overruns` is incremented (default 4).
    """

    def __init__(
        self,
        device: int | str | None = None,
        samplerate: int = 48_000,
        blocksize: int = 1_024,
        channels: int = 1,
        dtype: str = "float32",
        queue_maxsize: int = 4,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._device = device
        self._samplerate = samplerate
        self._blocksize = blocksize
        self._channels = channels
        self._dtype = dtype
        self._sensitivity: float = 1.0
        self._queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=queue_maxsize)
        self._stop_event = threading.Event()
        self._stream: sd.InputStream | None = None
        self._overruns: int = 0

    # ------------------------------------------------------------------
    # RealtimeController interface
    # ------------------------------------------------------------------

    @staticmethod
    def list_devices() -> list[dict]:
        """Return all input-capable devices reported by PortAudio."""
        return [
            {
                "index": i,
                "name": d["name"],
                "max_input_channels": d["max_input_channels"],
                "default_samplerate": d["default_samplerate"],
            }
            for i, d in enumerate(sd.query_devices())
            if d["max_input_channels"] > 0
        ]

    def start(self) -> None:
        """Open and start the PortAudio input stream."""
        self._stop_event.clear()
        self._stream = sd.InputStream(
            device=self._device,
            samplerate=self._samplerate,
            blocksize=self._blocksize,
            channels=self._channels,
            dtype=self._dtype,
            callback=self._callback,
        )
        self._stream.start()

    # ------------------------------------------------------------------
    # Controller interface
    # ------------------------------------------------------------------

    @property
    def samplerate(self) -> int:
        return self._samplerate

    @property
    def blocksize(self) -> int:
        return self._blocksize

    @property
    def sensitivity(self) -> float:
        return self._sensitivity

    def read_block(self) -> tuple[np.ndarray, int]:
        """Block until the next audio block is available, then return it.

        Returns ``(block, index)`` where *block* has shape
        ``(blocksize, channels)`` — matching the :class:`FileController`
        convention so the engine's ``.transpose()`` call works unchanged.

        Raises :exc:`StopIteration` once :meth:`stop` has been called and
        the queue is drained.
        """
        while True:
            try:
                block = self._queue.get(timeout=0.5)
                return block, next(self._counter)
            except queue.Empty:
                if self._stop_event.is_set():
                    raise StopIteration

    def stop(self) -> None:
        """Signal the stream to stop and close the PortAudio device."""
        self._stop_event.set()
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def calibrate(self, target_spl: float = 94.0) -> None:
        """Derive and set sensitivity from a live calibrator tone.

        Starts the stream, runs :func:`~slm.calibration.calibrate_sensitivity`
        with stability detection, then stops the stream and stores the result.
        The stream is stopped automatically once the reading has converged.
        """
        from slm.calibration import calibrate_sensitivity

        self.set_sensitivity(1.0, unit="V")
        self.start()
        try:
            sens = calibrate_sensitivity(self, stability_window=10)
        finally:
            self.stop()
        self.set_sensitivity(sens, unit="V")

    # ------------------------------------------------------------------
    # Extra
    # ------------------------------------------------------------------

    @property
    def overruns(self) -> int:
        """Number of blocks dropped due to the engine processing too slowly."""
        return self._overruns

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            self._overruns += 1
        try:
            self._queue.put_nowait(indata.copy())
        except queue.Full:
            self._overruns += 1