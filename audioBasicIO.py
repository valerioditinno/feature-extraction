import numpy
from pydub import AudioSegment

import sys

if sys.version_info >= (3, 0):
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

def readAudioFile(path):
    '''
    This function returns a numpy array that stores the audio samples of a specified WAV file
    '''
    try:
        audiofile = AudioSegment.from_file(path)

        if audiofile.sample_width == 2:
            data = numpy.fromstring(audiofile._data, numpy.int16)
        elif audiofile.sample_width == 4:
            data = numpy.fromstring(audiofile._data, numpy.int32)
        else:
            return (-1, -1)
        Fs = audiofile.frame_rate
        x = []
        for chn in xrange(audiofile.channels):
            x.append(data[chn::audiofile.channels])
        x = numpy.array(x).T

    except IOError: 
        print("Error: file not found or other I/O error.")
        return (-1,-1)

    if x.ndim == 2:
        if x.shape[1] == 1:
            x = x.flatten()

    return (Fs, x)