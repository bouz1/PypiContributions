import numpy as np
import scipy.signal
import scipy.fft
from numba import jit
#import matplotlib.pyplot as plt

# =========================================================
# 1. Numba Accelerators (Fast Detectors)
# =========================================================
@jit(nopython=True)
def quasi_peak_filter(magnitude_signal, dt, tau_charge, tau_discharge):
    """
    Simulates the CISPR Quasi-Peak detector circuit (RC charge/discharge).
    """
    n_samples = len(magnitude_signal)
    output = np.zeros(n_samples, dtype=np.float64)
    
    # Pre-calculate exponential coefficients
    alpha_charge = 1.0 - np.exp(-dt / tau_charge)
    alpha_discharge = 1.0 - np.exp(-dt / tau_discharge)
    
    current_val = 0.0
    
    for i in range(n_samples):
        in_val = magnitude_signal[i]
        
        # Analog circuit emulation
        if in_val > current_val:
            current_val += alpha_charge * (in_val - current_val)
        else:
            current_val -= alpha_discharge * current_val
            
        output[i] = current_val
        
    return np.max(output)

@jit(nopython=True, parallel=True)
def run_detectors_parallel(spectrogram_mag, dt, tau_c, tau_d):
    """
    Parallel loop over all frequency bins to compute Peak, Avg, and QP.
    """
    n_time, n_freq = spectrogram_mag.shape
    
    res_peak = np.zeros(n_freq)
    res_avg = np.zeros(n_freq)
    res_qp = np.zeros(n_freq)
    
    for f in range(n_freq):
        time_trace = spectrogram_mag[:, f]
        
        # 1. Peak
        res_peak[f] = np.max(time_trace)
        
        # 2. Average
        res_avg[f] = np.mean(time_trace)
        
        # 3. Quasi-Peak
        res_qp[f] = quasi_peak_filter(time_trace, dt, tau_c, tau_d)
        
    return res_peak, res_avg, res_qp

# =========================================================
# 2. Main EMI Receiver Function
# =========================================================
def receiver(signal, fs, rbw=9000, step=2500, band='B'):
    """
    FFT-based EMI Receiver Emulation.
    
    Parameters:
    -----------
    signal : array_like
        Input signal (Volts)
    fs : float
        Sampling Frequency (Hz)
    rbw : float
        Resolution Bandwidth (Hz). Default 9 kHz.
    step : float
        Frequency Step size (Hz). Default 2500 Hz (2.5 kHz).
        The code will use Zero-Padding interpolation to achieve this exact step.
    band : str
        CISPR Band ('A' or 'B'). 'B' is 150kHz-30MHz.
        
    Returns:
    --------
    freqs, peak_dBuV, avg_dBuV, qp_dBuV
    """
    
    # --- A. Setup Constants ---
    if band == 'A': 
        tau_c, tau_d = 45e-3, 500e-3
    elif band == 'B': 
        tau_c, tau_d = 1e-3, 160e-3
    else: 
        tau_c, tau_d = 1e-3, 550e-3

    # --- B. Design the "RBW" Window ---
    # We need a Gaussian window where the 6dB bandwidth equals RBW.
    sigma_f = rbw / (2 * np.sqrt(2 * np.log(2)))
    sigma_t = 1.0 / (2 * np.pi * sigma_f)
    
    # Window length (Physical Filter Width)
    win_len_sec = 6 * sigma_t 
    nperseg = int(win_len_sec * fs)
    if nperseg % 2 == 0: nperseg += 1
    
    # --- C. Configure FFT Step Size ---
    # Formula: Step = Fs / Nfft
    # Therefore: Nfft = Fs / Step
    target_nfft = int(round(fs / step))
    
    # Validation: Nfft cannot be smaller than the window length
    if target_nfft < nperseg:
        print(f"Warning: Step {step}Hz is too large for RBW {rbw}Hz.")
        print(f"         Forcing natural resolution: {fs/nperseg:.2f} Hz")
        nfft = nperseg
    else:
        nfft = target_nfft

    # Generate Gaussian Window
    sigma_samples = sigma_t * fs
    window = scipy.signal.windows.gaussian(nperseg, std=sigma_samples)
    
    # Normalize Window Energy (Sum=1 ensures correct amplitude after FFT)
    window = window / np.sum(window) 
    
    # --- D. Overlap Configuration ---
    # 90% Overlap is standard for FFT-Scan to capture transient peaks
    overlap_ratio = 0.90 
    noverlap = int(nperseg * overlap_ratio)
    step_size = nperseg - noverlap
    
    # Detector Timing
    fs_detector = fs / step_size
    dt_detector = 1.0 / fs_detector
    
    # Debug Info
    actual_step = fs / nfft
    print(f"--------------------------------------------------")
    print(f"EMI Receiver Configuration:")
    print(f"  RBW           : {rbw} Hz")
    print(f"  Step Size     : {actual_step:.2f} Hz (Target: {step} Hz)")
    print(f"  Window Size   : {nperseg} samples")
    print(f"  FFT Size      : {nfft} samples (Zero-Padding: {nfft > nperseg})")
    print(f"  Detector Time : {dt_detector*1e3:.3f} ms")
    print(f"--------------------------------------------------")

    if dt_detector > tau_c:
        print("WARNING: Sample rate/Overlap too low for accurate QP detection!")

    # --- E. Perform STFT ---
    # padded=True allows signal to be handled at boundaries
    f_axis, t_axis, Zxx = scipy.signal.stft(
        signal, fs, 
        window=window, 
        nperseg=nperseg,    # Controls RBW Physics
        noverlap=noverlap, 
        nfft=nfft,          # Controls Frequency Step (Display)
        boundary='zeros',
        padded=True
    )

    # Convert to One-Sided Voltage Magnitude
    # Multiply by 2.0 to account for negative frequency energy
    mag_spectrogram = np.abs(Zxx) * 2.0
    mag_spectrogram_T = mag_spectrogram.T 

    # --- F. Run Detectors ---
    peak_v, avg_v, qp_v = run_detectors_parallel(mag_spectrogram_T, dt_detector, tau_c, tau_d)

    # --- G. Convert to dBµV ---
    def to_dbuv(v_array):
        # 1e-12 prevents log(0)
        return 20 * np.log10(np.maximum(v_array, 1e-12) * 1e6)

    return f_axis, to_dbuv(peak_v), to_dbuv(avg_v), to_dbuv(qp_v)
