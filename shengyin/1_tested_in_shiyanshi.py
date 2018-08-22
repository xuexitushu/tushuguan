#!usr/bin/env python

import numpy as np
import sounddevice as sd
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--ip", help="ip address of the target", required=True)
parser.add_argument("-p", "--port", help="port of the target", default=8000)
parser.add_argument("-t", "--threshold", help="audio time threshold", default=200, required=True)
args = parser.parse_args()
URL = "http://" + args.ip + ":" + str(args.port) + "/audio_level_high"

THRESHOLD = float(args.threshold)
duration_seconds = 10
lock = False

SAMPLE_RATE = 44100
BLOCKSIZE = 4410 * 5
FEATURE_RATE = 100
AGGR_DETECTION_WINDOWLENGTH_IN_SECONDS = 0.50
MIN_AMOUNT_ABOVE_THRESHOLD = 0.30


def smooth(x, window_len=11, window='hanning'):
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is none of 'flat','hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len -1:-1]]

    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')

    return y[int(window_len / 2 -1):(-int(window_len/2) - 1)]



def audio_callback(indata, frames, time, status):
    global lock

    indata = indata.flatten()
    print('no smoothing max frame value:', max(abs(indata)))

    smoothed_wave = smooth(indata)

    #hald rectify
    smoothed_wave = abs(smoothed_wave)

    #reduce feature rate by averaging amplitude
    feature_rate = 100 #in the end, 1s corresponds to 10 features
    numFrames = int(len(smoothed_wave) * 1.0 / SAMPLE_RATE * FEATURE_RATE)

    downsample_averaged_wave = np.zeros(numFrames)

    for i in range(numFrames):
        num_samples_per_feature = SAMPLE_RATE / FEATURE_RATE
        begin = int(i * num_samples_per_feature)
        end = (int)(i+1)*num_samples_per_feature
        downsample_averaged_wave[i] = sum(smoothed_wave[begin:end]) / num_samples_per_feature

    print(max(abs(downsample_averaged_wave)))

    print('*', THRESHOLD)

    if(np.any(downsample_averaged_wave > THRESHOLD)) and not lock:
        lock = True
    req = requests.get(URL, stream=True)
    print(req)
    print(max(downsample_averaged_wave))

    index = np.arange(len(downsample_averaged_wave))
    index_above_thresh = index[downsample_averaged_wave > THRESHOLD]
    value_above_thresh = downsample_averaged_wave[index_above_thresh]
    indices_boolean = (downsample_averaged_wave > THRESHOLD).astype(int)

    print('frame aggresion1:', index_above_thresh)

    #additional window
    num_points_min_amount = AGGR_DETECTION_WINDOWLENGTH_IN_SECONDS * MIN_AMOUNT_ABOVE_THRESHOLD * FEATURE_RATE
    aggression = []
    half_aggr_window_length = int(AGGR_DETECTION_WINDOWLENGTH_IN_SECONDS * FEATURE_RATE / 2)

    for i in index_above_thresh:
        window_begin = max(0, i - half_aggr_window_length)
        window_end = min(len(downsample_averaged_wave), i + half_aggr_window_length)

        if sum(indices_boolean[window_begin:window_end]) > num_points_min_amount:
            #print('start:', window_begin, 'end:', window_end)
            aggression.append(i)

    if len(aggression) > 0:
        aggr_indices = np.array(aggression).tolist()
        aggression_values = downsample_averaged_wave[aggr_indices]
        print('frame aggression2 -------:',aggr_indices)
        print('points selected in aggression window that are same as before:', set(index_above_thresh) == set(aggr_indices))

    lock = False

print('place2')


while True:
    stream = sd.InputStream(samplerate=SAMPLE_RATE,blocksize=BLOCKSIZE,
                            channels=1,callback=audio_callback) #default dtype='float32'

    with stream:
        sd.sleep(1000*duration_seconds)

print('place3')