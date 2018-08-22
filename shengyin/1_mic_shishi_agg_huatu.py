import pyaudio
import numpy as np
import time
import wave
import matplotlib.pyplot as plt

#open stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECORD_SECONDS = 30
fs = 44100
CHUNK = 4410

#for aggr detect
FEATURE_RATE = 1000 # in the post processing, 1s corresponds to 1000 features

#
THRESHOLD = 1000
AGGRESSION_DETECTION_WINDOWLENGTH_SECONDS = 0.10
MIN_AMOUNT_ABOVE_THRESHOLD = 0.05


#https://github.com/scipy/scipy-cookbook/blob/master/ipython/SignalSmooth.ipynb

def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    #return y
    return y[int(window_len / 2 - 1):(-int(window_len / 2) -1)]

def soundPlot(stream):
    t1=time.time()
    data = stream.read(CHUNK, exception_on_overflow=False)
    waveData = wave.struct.unpack("%db"%(CHUNK), data)
    np_arrayData = np.array(waveData)
    print(max(np_arrayData), min(np_arrayData))


    #smoothing signal
    feature_rate = 100 #in the end, 1s corresponds to 10 features

    numframes = int(len(smoothed_wave) / fs * FEATURE_RATE)

    y_downsample_averaged = np.zeros(numframes)
    for i in range(numframes):
        num_samples_per_feature = fs / FEATURE_RATE
        begin = int(i*num_samples_per_feature)
        end = int(i+1)*num_samples_per_feature

        y_downsample_averaged[i] = sum(smoothed_wave[begin:end]) / num_samples_per_feature

    print(max(abs(y_downsample_averaged)))

    #plot time domain
    ax1.cla()
    ax1.plot(y_downsample_averaged)
    ax1.grid()
    ax1.axis([0,len(y_downsample_averaged),-5000,5000])

    #plot single feature that is above threshold
    if(np.any(y_downsample_averaged > THRESHOLD)):
        index = np.arange(len(y_downsample_averaged))
        index_above_thresh = y_downsample_averaged[index_above_thresh]
        indices_boolean = (y_downsample_averaged > THRESHOLD).astype(int)

        ax1.plot(index_above_thresh, value_above_thresh, 'yo')
        print('frame aggression1:', index_above_thresh)

        #additional aggression window
        num_points_min = AGGRESSION_DETECTION_WINDOWLENGTH_SECONDS * MIN_AMOUNT_ABOVE_THRESHOLD * FEATURE_RATE
        aggression = []
        half_agg_window_len = int(AGGRESSION_DETECTION_WINDOWLENGTH_SECONDS * FEATURE_RATE / 2)

        for i in index_above_thresh:
            window_begin = max(0, i - half_agg_window_len)
            window_end = min(len(y_downsample_averaged), i + half_agg_window_len)

            if sum(indices_boolean[window_begin:window_end]) > num_points_min:
                print('start:',window_begin, 'end:', window_end)
                print(i)
                print(num_points_min)
                aggression.append(i)

        if len(aggression) > 0:
            aggression_indices = np.array(aggression).tolist()
            aggression_values = y_downsample_averaged(aggression_indices)
            print('frame aggression2:',aggression_indices)
            print('points selected in aggression window, same as before:', set(index_above_threshold) == set(aggression_indices))

        plt.pause(0.00005)
        print("took %.2f ms"%((time.time()-t1)*1000))

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=fs, input=True, frame_per_buffer=CHUNK)

    plt.ion()
    print('test')
    for i in range(0,int(fs / CHUNK * RECORD_SECONDS)):
        soundPlot(stream)

    stream.stop_stream()
    stream.close()
    p.terminate()