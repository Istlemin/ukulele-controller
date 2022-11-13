import pyaudio
import numpy as np
from notes import *
from params import *
from keyboard import strum_to_key
from ukulele import Tuning


class Device:
    def __init__(self):
        self.note = None
        self.amplitude = None
        self.tuning = Tuning()

    def write(self, note, amplitude):
        self.note = note
        self.amplitude = amplitude
        #print(strum_to_key(self.tuning.note_to_string(note)))

    def clear(self):
        self.state = None

    def get_state(self):
        return self.note, self.amplitude


class Microphone:
    def __init__(self):
        audio = pyaudio.PyAudio()
        self.stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input = True, \
                            frames_per_buffer=chunk)

        self.noise_fft_vec, self.noise_amp_vec = [],[]
        self.peak_data = []
        self.calibrate(noise_len)

    def calibrate(self, noise_len):
        for _ in range(noise_len):
            self.stream.start_stream()
            data = np.fromstring(self.stream.read(chunk),dtype=np.int16)
            data = ((data/np.power(2.0,15))*5.25)*(mic_sens_corr)
            self.stream.stop_stream()

            # compute FFT
            fft_data = (np.abs(np.fft.fft(data))[0:int(np.floor(chunk/2))])/chunk
            fft_data[1:] = 2*fft_data[1:]     

            self.noise_fft_vec.append(fft_data)
            self.noise_amp_vec.extend(data)
        self.noise_fft = np.max(self.noise_fft_vec,axis=0)
        self.noise_amp = np.mean(self.noise_amp_vec)

    def tick(self, device):
        self.stream.start_stream()
        data = np.fromstring(self.stream.read(chunk),dtype=np.int16)
        data = data-self.noise_amp
        data = ((data/np.power(2.0,15))*5.25)*(mic_sens_corr)
        self.stream.stop_stream()

        # compute FFT
        fft_data = (np.abs(np.fft.fft(data))[0:int(np.floor(chunk/2))])/chunk
        fft_data[1:] = 2*fft_data[1:]
        
        fft_data = np.subtract(fft_data,self.noise_fft) # subtract average spectral noise

        peak_data = 1.0*fft_data
        notes = []
        for _ in range(4):
            max_loc = np.argmax(peak_data[low_freq_loc:])
            peak_point = max_loc+low_freq_loc
            freq = f_vec[peak_point]
            amplitude = peak_data[peak_point]
            if amplitude>max(10*np.mean(self.noise_amp), thresh):
                note = freq_to_note(freq)
                notes.append((note, amplitude, freq))
                # zero-out old peaks so we dont find them again
                peak_data[peak_point-peak_shift:peak_point+peak_shift] = np.repeat(0,peak_shift*2)
        result = filter_notes(notes)
        if result:
            prim_n, prim_a, _ = result[0]
            device.write(prim_n, prim_a)
            print(notes)
            print(result)
        else:
            device.clear()

if __name__ == "__main__":
    mic = Microphone()
    device = Device()
    while True:
        mic.tick(device)