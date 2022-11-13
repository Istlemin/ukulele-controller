import numpy as np
import pyaudio

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 44100//5 # samples for buffer (more samples = better freq resolution)
dev_index = 2 # device index found by p.get_device_info_by_index(ii)

# mic sensitivity correction and bit conversion
mic_sens_dBV = -47.0 # mic sensitivity in dBV + any gain
mic_sens_corr = np.power(10.0,mic_sens_dBV/20.0) # calculate mic sensitivity conversion factor

# compute FFT parameters
f_vec = samp_rate*np.arange(chunk/2)/chunk # frequency vector based on window size and sample rate
mic_low_freq = 100 # low frequency response of the mic (mine in this case is 100 Hz) TODO
low_freq_loc = np.argmin(np.abs(f_vec-mic_low_freq))

# some peak-finding and noise preallocations
peak_shift = 10
noise_len = 5
thresh = 0.0006