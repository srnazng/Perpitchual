from __future__ import division
import math

from pyaudio import PyAudio # sudo apt-get install python{,3}-pyaudio

try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range

# Read in a WAV and find the freq's
import pyaudio
import wave
import numpy as np

chunk = 2048

L=[]

# open up a wave
wf = wave.open('C4.wav', 'rb')
swidth = wf.getsampwidth()
RATE = wf.getframerate()
# use a Blackman window
window = np.blackman(chunk)
# open stream
p = pyaudio.PyAudio()
stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = RATE,
                output = True)

# read some data
data = wf.readframes(chunk)
# find the frequency of each chunk
while len(data) == chunk*swidth:
    # write data out to the audio stream
    stream.write(data)
    # unpack the data and times by the hamming window
    indata = np.array(wave.struct.unpack("%dh"%(len(data)/swidth),\
                                         data))*window
    # Take the fft and square each value
    fftData=abs(np.fft.rfft(indata))**2
    # find the maximum
    which = fftData[1:].argmax() + 1
    # use quadratic interpolation around the max
    if which != len(fftData)-1:
        y0,y1,y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which+x1)*RATE/chunk
        #print ("The freq is %f Hz." % (thefreq))
        L.append(thefreq)
    else:
        thefreq = which*RATE/chunk
        #print ("The freq is %f Hz." % (thefreq))
    # read some more data
    data = wf.readframes(chunk)
if data:
    stream.write(data)
stream.close()
p.terminate()

#find the average frequency of wav file
average = sum(L) / len(L)
print('The frequency of the starting note is: ', average)

#find the increase in semitones
ogKey = input('Enter your current key (use # to represent sharps and b to represent flats): ')
endKey = input('Enter the desired key: ')

thisdict = {
    "A" : 1,
    "A#" : 2,
    "Bb" : 2,
    "B" : 3,
    "C" : 4,
    "C#" : 5,
    "Db" : 5,
    "D" : 6,
    "D#" : 7,
    "Eb" : 7,
    "E" : 8,
    "F" : 9,
    "F#" : 10,
    "Gb" : 10,
    "G" : 11,
    "G#" : 12,
    "Ab" : 12
}

ogKeyNum = thisdict[ogKey]
endKeyNum = thisdict[endKey]

count = endKeyNum - ogKeyNum

#calculate the frequency of the transposed note
finalFreq = average * (1.059463094359 ** count)
print('The frequency of the transposed note is: ', finalFreq)

#play the transposed note
def sine_tone(frequency, duration, volume=1, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1), # 8bita
                    channels=1, # mono
                    rate=sample_rate,
                    output=True)
    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    samples = (int(s(t) * 0x7f + 0x80) for t in xrange(n_samples))
    for buf in izip(*[samples]*sample_rate): # write several samples at a time
        stream.write(bytes(bytearray(buf)))

    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()

sine_tone(
    # see http://www.phy.mtu.edu/~suits/notefreqs.html
    frequency=finalFreq, # Hz, waves per second A4
    duration=3.21, # seconds to play sound
    volume=1, # 0..1 how loud it is
    # see http://en.wikipedia.org/wiki/Bit_rate#Audio
    sample_rate=22050 # number of samples per second
)
