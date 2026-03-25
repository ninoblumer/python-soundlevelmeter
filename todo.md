# Todo

## Open
- [ ] #27 **Streamline Engine construction** — `Engine.__init__` should accept `Reporter` directly (or `reporter_kwargs`) so callers don't need to manually create a `Reporter` and assign `engine.reporter = reporter` as a second step; update `run_measurement`/`run_realtime_measurement` and README accordingly.
- [ ] #26 **Support arbitrary octave divisions in the CLI/metric syntax** — extend `parse_metric` regex and `MetricSpec` to accept any `N/M` fraction (e.g. `1/6`, `1/12`, `2/3`) in the `:bands:` suffix, not just `1/3`; update `build_chain` and README accordingly.

## Optional
- [ ] #17 **FFT-based A-weighting (optional improvement)** — replace the bilinear-transform IIR in `PluginAWeighting` with a frequency-domain analytical A-weighting to reduce broadband LAeq error from −0.17 dB to ±0.05 dB vs XL2. Requires overlap-add block processing; incompatible with current real-time time-weighted plugins (LASmax etc.) on the same bus without a parallel path. Pre-requisite: split the bus into a Leq-only FFT path and a time-weighting IIR path.
- [ ] #23 **use different filter for frequency-weighting** - use different design method (pre-warping, impulse invariance or so)
- [ ] #25 **Discoverable output device** — make the SLM appear as a connectable audio sink so other software can route audio to it without a hardware loopback. On Linux/macOS: `JackController` (JACK client with named input ports; works transparently with PipeWire on modern Linux). On Windows: not reliably feasible without a third-party virtual audio cable driver.

## Done
- [x] #5 **README.md** — full rewrite: installation, usage, metric syntax, calibration, architecture, Python API; `pip install --user git+…` hint added.
- [x] #6 **LICENSE** — replaced acoustic-toolbox BSD with GPL v3 + copyright header; added NOTICE with reproduced BSD/MIT notices for numpy, scipy, soundfile, sounddevice; GPL notice in SLMShell intro.
- [x] #20 **Add `__init__.py` re-exports for `slm/io/`, `slm/app/`, and `slm/`** — flat public API; `sounddevice` made optional with graceful degradation; 529 tests pass.
- [x] #2 **Real-time audio controller** — `RealtimeController` ABC + `SounddeviceController` (PortAudio, cross-platform); stability-detection calibration; `--device`/`--list-devices`/`--samplerate` CLI flags; 15 unit tests.
- [x] #21 **Redo calibration routine** — `PluginBandpass` added; core `slm/calibration.py` is controller-agnostic; `calibrate_from_file` in `slm/app/cli.py`; `--cal-freq` CLI flag; 2 new unit tests.
- [x] #24 **conformance tests should record how "well" they passed** — `report=True` pattern on all conformance test methods; `scripts/conformance_report.py` calls them directly and prints margin tables
- [x] #22 **tidy up tests/ folder** - add sub folders and group tests together
- [x] #18 **Test conformance with standards IEC 61260 and IEC 61672** — requirements summarized in `notes/SLM_Conformance_Test_Report.md`
- [x] #4 **XL2 parser: missing Time section** — `_SectionTime` added to `util/xl2.py`; parses `Start`/`End` as `datetime` objects in all file types that carry `# Time` (123_Log, RTA_3rd_Log, RTA_3rd_Report, RTA_Oct_Log, RTA_Oct_Report); 6 new tests in `tests/test_xl2_parser.py`; 190 tests pass.
- [x] #19 **Implement LE** (exposure level) — `LEAccumulator` + `LEMovingMeter` in `slm/meter.py`; parser/builder extended in `slm/assembly.py` (`LAE`, `LCE`, `LZE`, window/band variants); engine end-of-file snapshot fix; 184 tests pass.
- [x] #1 **Declarative measurement configuration** — `slm/assembly.py` (`parse_metric`, `build_chain`), `slm/config.py` (`SLMConfig` + TOML I/O), `slm/cli.py` (sensitivity helpers, calibration, `run_measurement`, `SLMShell`), `slm/__main__.py` (`python -m slm`). 154 tests pass.
- [x] #16 **Calibration routine** — `calibrate_sensitivity(wav_path, cal_level)` in `slm/cli.py`; also available as `python -m slm --calibrate --file ... --cal-level 94`.
- [x] #3 **Tighten broadband test tolerance below 0.18 dB** — Root cause identified: bilinear-transform IIR A-weighting (pyoctaveband) over-attenuates above 5 kHz (−0.54 dB at 8 kHz, −6.43 dB at 16 kHz); for broadband signals this causes −0.22 dB systematic LAeq error. FFT-based analytical computation confirms filter is sole culprit (gives ±0.07 dB vs XL2). `TOLERANCE_DB = 0.18` is the practical limit of the current IIR architecture at fs=48 kHz. Root cause documented in `tests/test_xl2_broadband.py`. FFT-based fix tracked in #17.
- [x] #7 Fit XL2 AC-coupling HPF cutoff `fc` — broadband Z scan: `PluginHPF(fc=5.0, order=1)` reduces LZeq error from ~0.27 dB → 0.009 dB; Z tests switched to `_PluginXL2Z = partial(PluginHPF, fc=5.0)`; tolerance unified to ±0.2 dB
- [x] #8 Switch to official `pyoctaveband==1.2.1` from PyPI
- [x] #9 `PluginHPF` added to `slm/frequency_weighting.py` (Butterworth HPF, parametrized fc/order)
- [x] #10 `test_xl2_rta.py` — octave band LZeq per-band vs XL2 RTA log (SLM_005), ±0.5 dB
- [x] #11 Time weighting decay rates: Fast=34.7 dB/s, Slow=4.3 dB/s (IEC 61672-1 §5.8)
- [x] #12 Reporter redesign: broadband/band-split split, 4 CSV files, console printing
- [x] #13 Nominal mid-band frequencies (IEC 61260-1 Annex E) via pyoctaveband fork
- [x] #14 Remove dead code: PluginTimeAveraging, ReadMode, commented blocks
- [x] #15 Structured Engine output — Reporter now retrieves and writes results
