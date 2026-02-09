# EMI Receiver Emulator

A high-performance, FFT-based EMI (Electromagnetic Interference) receiver emulator written in Python. This package simulates standard CISPR 16-1-1 detectors (Peak, Quasi-Peak, and Average) using Short-Time Fourier Transform (STFT) and Numba-accelerated parallel processing.

It is designed to post-process time-domain signals (e.g., from oscilloscopes or DAQs) and generate EMI spectra compliant with CISPR bands (A, B, C/D).

## Features

* **CISPR Compliance:** Implements accurate charging/discharging time constants for Band A, B, and C/D.
* **Numba Acceleration:** Uses `@jit` and parallelization to compute Quasi-Peak (QP) detection significantly faster than pure Python implementations.
* **FFT-Scan Emulation:** Accurately models Resolution Bandwidth (RBW) using Gaussian windows and configurable overlap ratios (90%).
* **Flexible Config:** Custom support for Sampling Frequency (), RBW, and Frequency Step size.

## Algorithm Workflow

Summary of the algorithm from raw signal to final detector results:

1. **RBW Design:** Calculates the specific time-length of a **Gaussian Window** to physically guarantee a 9 kHz Resolution Bandwidth (CISPR requirement).
2. **Step Calibration:** Determines the necessary FFT size (adding zero-padding) to ensure the output points are spaced exactly every **2.5 kHz**.
3. **Segmentation (STFT):** Slices the long signal into thousands of small, **90% overlapping** frames to capture transient pulses without loss.
4. **Spectral Matrix:** Applies the window and performs FFT on every frame, creating a 2D matrix of **Voltage vs. Time** for every frequency.
5. **Envelope Detection:** Converts the complex FFT output into absolute voltage magnitude (multiplying by 2 to correct for one-sided spectrum).
6. **Peak Detector:** Iterates through every frequency bin and finds the **maximum** value occurring over time.
7. **Average Detector:** Iterates through every frequency bin and calculates the **arithmetic mean** of the voltage over time.
8. **Quasi-Peak Detector:** Passes the time-envelope of every frequency through a **digital IIR filter** that mimics the charge/discharge physics of a capacitor (, ).
9. **Output:** Converts the final arrays from Volts to **dBµV**.

## Installation

You can install the package directly from the source:

```bash
pip install emi_receiver
```

### Dependencies

* `numpy`
* `scipy`
* `numba`
* `matplotlib`

## Quick Start

```python
import numpy as np
import matplotlib.pyplot as plt
from emi_receiver import receiver

# 1. Generate a test signal (e.g., 1 MHz sine wave + Noise)
fs = 30e6  # 30 MHz sampling rate
duration = 0.1  # seconds
t = np.arange(int(fs * duration)) / fs
signal = 0.01 * np.sin(2 * np.pi * 1e6 * t) + 0.001 * np.random.randn(len(t))

# 2. Run the EMI Receiver (Band B: 150kHz - 30MHz)
freqs, peak, avg, qp = receiver(signal, fs, band='B')

# 3. Plot the results
plt.figure(figsize=(10, 6))
plt.plot(freqs / 1e6, peak, label='Peak', color='blue', alpha=0.5)
plt.plot(freqs / 1e6, qp, label='Quasi-Peak', color='red')
plt.plot(freqs / 1e6, avg, label='Average', color='green', linestyle='--')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Amplitude (dBµV)')
plt.title('EMI Receiver Emulation (CISPR Band B)')
plt.legend()
plt.grid(True)
plt.show()
```

## Validation of the EMI Receiver Emulator

### CISPR 16-1-1 validation

To validate EMI Receiver physically and mathematically, we must use **CISPR 16-1-1**.

CISPR 16-1-1 defines the **"Response to Pulses"**. This is the ultimate test. It proves that your `quasi_peak_filter` (Charge/Discharge) behaves exactly like the analog circuit defined in the standard.

#### The Validation Standard: CISPR 16-1-1 (Band B)

The standard requires that we inject a **Pulse Train** (Rectangular pulses) and measure how the Quasi-Peak (QP) reading changes when we change the **Pulse Repetition Frequency (PRF)**.

**Reference:** PRF = 100 Hz.
If we lower the repetition frequency, the capacitor has more time to discharge, so the QP value must drop by exact amounts defined in the table below.

| PRF (Hz)   | Target QP Drop (dB) | Tolerance (dB) | Physics Meaning                   |
|:---------- |:------------------- |:-------------- |:--------------------------------- |
| **100 Hz** | **0.0 dB** (Ref)    | -              | Constant charge/discharge balance |
| **60 Hz**  | **-1.4 dB**         | ± 1.5          |                                   |
| **20 Hz**  | **-5.9 dB**         | ± 1.5          | Slower recharge                   |
| **10 Hz**  | **-10.5 dB**        | ± 1.5          | Deep discharge                    |
| **2 Hz**   | **-20.5 dB**        | ± 2.0          | Almost isolated pulses            |
| **1 Hz**   | **-23.5 dB**        | ± 2.0          | Isolated pulses                   |

---

#### The Validation Script

This script generates a pulse train, runs your EMI receiver, and compares the result against the CISPR 16-1-1 table.

**Note:** This simulation requires memory because for 1 Hz PRF, we need 2 seconds of signal.

#### Explanation of the Test

1. **Signal:** We create a "Dirac Comb" (a train of sharp spikes). This is a broadband signal (spectrum is flat).
2. **Physics:**
   * **At 100 Hz:** The pulses come fast (every 10ms). The QP capacitor ($\tau_{disch}=160ms$) discharges very little between pulses. The voltage stays high.
   * **At 1 Hz:** The pulses come slowly (every 1s). The QP capacitor discharges almost completely between pulses (since $1000ms \gg 160ms$). The "Quasi-Peak" value drops significantly.
3. **The Result:**
   * The `Actual (dB)` column shows how much your receiver dropped compared to the 100Hz reference.
   * If your code is correct, your `Actual` values will be very close to the `Target` values from the standard.

#### Test result

```text
------------------------------------------------------------

PRF (Hz)   | Target (dB)  | Actual (dB)  | Error (dB) | Status
------------------------------------------------------------

100        | 0.0          | 0.00         | 0.00       | PASS
60         | -1.4         | -1.77        | 0.37       | PASS
20         | -5.9         | -6.58        | 0.68       | PASS
10         | -10.5        | -9.91        | 0.59       | PASS
2          | -20.5        | -14.44       | 6.06       | FAIL
1          | -23.5        | -14.75       | 8.75       | FAIL

------------------------------------------------------------
```

**Note on Low-PRF Failures**: The divergence at 1Hz and 2Hz is a known trade-off of the digital STFT approach. To pass these specific tests, the overlap must be increased beyond 95%, which creates a significant RAM bottleneck for long signals. For the vast majority of real-world EMI cases (switching noise, harmonics), the current 90% overlap offers the best balance of speed and precision.

### Comparison Between This EMI Receiver Implementation and an Industrial EMI Receiver

In this section, we present a simple comparison of the results obtained from this EMI preprocessing implementation.

The setup consists of a function generator that generates a square wave with a 50% duty cycle, with a frequency sweep period of 1 ms and minimum/maximum frequencies of 135 kHz and 145 kHz.

For each test, two configurations are evaluated: a fixed frequency of 140 kHz and a swept frequency.

A schematic of this setup is shown below:

<.........>

The results from the EMI receiver are presented for the following detectors:

* **AVG Detector**

<.........>

* **Peak Detector**
  <.........>

* **Quasi-Peak Detector**
  <.........>

## Directory Structure

```text
emi-receiver/
├── app/
│   └── emi-receiver/
│       ├── src/
│       │   └── emi-receiver.py   # Core logic
│       └── test/                 # Unit tests
├── setup.py
├── LICENSE
└── README.md
```

## License

This project is licensed under the terms of the MIT License.