import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import time
from notes import *
from params import *

PLOT = True

audio = pyaudio.PyAudio() # create pyaudio instantiation

# prepare plot for live updating
if PLOT:
    plt.style.use('ggplot')
    plt.ion()
    fig = plt.figure(figsize=(12,5))
    ax = fig.add_subplot(111)
    annot = ax.text(np.exp(np.log((0.8*f_vec[-1]))/2),0,"Measuring Noise...",\
                    fontsize=30,horizontalalignment='center')
    y = np.zeros((int(np.floor(chunk/2)),1))
    line1, = ax.plot(f_vec,y)
    plt.xlabel('Frequency [Hz]',fontsize=22)
    plt.ylabel('Amplitude [Pa]',fontsize=22)
    plt.grid(True)
    plt.annotate(r'$\Delta f_{max}$: %2.1f Hz' % (samp_rate/(2*chunk)),xy=(0.7,0.9),xycoords='figure fraction',fontsize=16)
    ax.set_xscale('log')
    ax.set_xlim([1,0.8*samp_rate])
    plt.pause(0.0001)

# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input = True, \
                    frames_per_buffer=chunk)

# some peak-finding and noise preallocations
noise_fft_vec,noise_amp_vec = [],[]
peak_data = []
ii = 0

if PLOT:
    annot_array,annot_locs = [],[]
    annot_array.append(annot)


# loop through stream and look for dominant peaks while also subtracting noise
while True:

    # read stream and convert data from bits to Pascals
    stream.start_stream()
    data = np.fromstring(stream.read(chunk),dtype=np.int16)
    if ii==noise_len:
        data = data-noise_amp
    data = ((data/np.power(2.0,15))*5.25)*(mic_sens_corr)
    stream.stop_stream()

    # compute FFT
    fft_data = (np.abs(np.fft.fft(data))[0:int(np.floor(chunk/2))])/chunk
    fft_data[1:] = 2*fft_data[1:]

    # calculate and subtract average spectral noise
    if ii<noise_len:
        if ii==0:
            print("Stay Quiet, Measuring Noise...")        
        noise_fft_vec.append(fft_data)
        noise_amp_vec.extend(data)
        print(".")
        if ii==noise_len-1:
            noise_fft = np.max(noise_fft_vec,axis=0)
            noise_amp = np.mean(noise_amp_vec)
            print("Now Recording")
        ii+=1
        continue
    
    fft_data = np.subtract(fft_data,noise_fft) # subtract average spectral noise

    # plot the new data and adjust y-axis (if needed)
    if PLOT:
        line1.set_ydata(fft_data)
        if np.max(fft_data)>(ax.get_ylim())[1] or np.max(fft_data)<0.5*((ax.get_ylim())[1]):
            ax.set_ylim([0,1.2*np.max(fft_data)])

        try:
            for annots in annot_array:
                annots.remove()
        except:
            pass
        # annotate peak frequencies (6 largest peaks, max width of 10 Hz [can be controlled by peak_shift above])
        annot_array = []
    peak_data = 1.0*fft_data
    peaks = []
    notes = []
    for jj in range(4):
        max_loc = np.argmax(peak_data[low_freq_loc:])
        peak_point = max_loc+low_freq_loc
        freq = f_vec[peak_point]
        amplitude = peak_data[peak_point]
        if amplitude>max(10*np.mean(noise_amp), thresh):
            peaks.append(freq)
            note = to_note(freq)
            notes.append((note, amplitude, freq))

            if PLOT:
                annot = ax.annotate(f'{freq}: {note}',\
                                xy=(freq,amplitude),\
                                xycoords='data',xytext=(-30,30),textcoords='offset points',\
                                arrowprops=dict(arrowstyle="->",color='k'),ha='center',va='bottom')
                    
                annot_locs.append(annot.get_position())
                annot_array.append(annot)

            # zero-out old peaks so we dont find them again
            peak_data[peak_point-peak_shift:peak_point+peak_shift] = np.repeat(0,peak_shift*2)
    # print(peaks)
    # print(notes)
    result = filter_notes(notes)
    if result:
        print(result[0])


    # print(fft_data)
    # plt.show()
    if PLOT:
        plt.pause(0.001)    
    # wait for user to okay the next loop (comment out to have continuous loop)
    # imp = input("Input 0 to Continue, or 1 to save figure ")
    # if PLOT and imp=='1':
    #     file_name = input("Please input filename for figure ")
    #     plt.savefig(file_name+'.png',dpi=300,facecolor='#FCFCFC')