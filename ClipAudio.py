""" clips area before and after number is spoken
arg are the directory where wave files are located

Author: Merlin Carson
Date: 6/11/2019
"""
import os
import sys
import soundfile as sf
#import librosa
import numpy as np
import glob

# final sample rate for wave files
SAMPLERATE = 8000

def get_averages(samples, frameSize):
    averages = []
    for frame in range(0,len(samples), frameSize):
        averages.append(np.average(np.absolute(samples[frame:frame+frameSize])))

    return averages

def find_clusters(samples, averages, target, frameSize):
    startIdx = None
    endIdx = None
    clusters = []
    for idx, frame in enumerate(range(0,len(samples), frameSize)):
        if averages[idx] > target and not startIdx:
            startIdx = idx
        if startIdx and not endIdx:
            if averages[idx] < target:
                endIdx = idx
        if startIdx and endIdx:
            clusters.append((startIdx,endIdx))
            startIdx = None
            endIdx = None

    return clusters
            
def find_longest_cluster(clusters):
    longestCluster = 0
    longestClusterSize = 0
    for cluster in clusters:
        clusterSize = cluster[1]-cluster[0]
        if clusterSize > longestClusterSize:
            longestClusterSize = clusterSize
            longestCluster = cluster

    return longestCluster 
           
def clip_audio(samples):

    frameSize = 100
    averages = get_averages(samples, frameSize)
    target = np.average(averages)/2     # threshold, assume below this level is backround noise
   
    # find all audio clusters above target threshold 
    clusters = find_clusters(samples, averages, target, frameSize)

    # find longest audio cluster
    longestCluster = find_longest_cluster(clusters)

    return samples[longestCluster[0]*frameSize:longestCluster[1]*frameSize]

def clip_waves(rawAudioPath, clippedAudioPath):
    for fileName in glob.iglob(os.path.join(rawAudioPath, '*.wav')):
        print('File:', fileName)
        samples, sample_rate = sf.read(fileName )
        print("number of samples:", len(samples))
        
        # find largest cluster of audio and grab the samples
        clippedSamples = clip_audio(samples)

        # write clipped audio to file
        clippedFileName = os.path.join(clippedAudioPath, os.path.basename(fileName))
        sf.write(clippedFileName, clippedSamples, SAMPLERATE, subtype='PCM_16')
        print(f'{fileName} clipped and saved as {clippedFileName}')

def main():
    assert len(sys.argv) > 2, "Must include path to audio files and path for clipped audio files as arguments."

    rawAudioPath = sys.argv[1]      # location of waves to clip 
    clippedAudioPath = sys.argv[2]      # location to save clipped audio files

    # if output directory does not exist, create it    
    if not os.path.isdir(clippedAudioPath):
        os.makedirs(clippedAudioPath)

    print(f'Location of raw wave files: {rawAudioPath}')
    print(f'Location to save clipped wave files: {clippedAudioPath}')

    clip_waves(rawAudioPath, clippedAudioPath)

    print('Audio Clipping complete.')

if __name__ == "__main__":
    main()
