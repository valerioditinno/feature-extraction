import sys
import time

import numpy as np

import DatasetPreprocessing as pre
import audioFeatureExtraction


class FeatureExtraction:
    '''
        This class implement features extraction using pyAudioAnalysis(a my extension to python3) on Mivia Audio Events Dataset.

        The data set:
        The MIVIA audio events data set is composed of a total of 6000 events for surveillance applications,
        namely glass breaking, gun shots and screams. The 6000 events are divided into a training set
        (composed of 4200 events) and a test set (composed of 1800 events).
        The data set is designed to provide each audio event at 6 different values of signal-to-noise ratio
        (namely 5dB, 10dB, 15dB, 20dB, 25dB and 30dB) and overimposed to different combinations of environmental
        sounds in order to simulate their occurrence in different ambiences.
        More details are reported on the web site http://mivia.unisa.it/datasets/audio-analysis/mivia-audio-events/.

        pyAudioAnalysis:
        pyAudioAnalysis is an open-source Python library that provides a wide range of audio analysis
        procedures including: feature extraction, classification of audio signals, supervised and unsupervised
        segmentation and content visualization. pyAudioAnalysis is licensed under the Apache License and is available
        at GitHub (https://github.com/tyiannak/pyAudioAnalysis/).

        For each frame the following features are computed:
            -Zero_Crossing_Rate_median, Zero_Crossing_Rate_median_absolute_deviation
            -Energy_median, Energy_median_absolute_deviation
            -Entropy_of_Energy_median, Entropy_of_Energy_median_absolute_deviation
            -Spectral_Centroid_median, Spectral_Centroid_median_absolute_deviation
            -Spectral_Spread_median, Spectral_Spread_median_absolute_deviation
            -Spectral_Entropy_median, Spectral_Entropy_median_absolute_deviation
            -Spectral_Flux_median, Spectral_Flux_median_absolute_deviation
            -Spectral_Rolloff_median, Spectral_Rolloff_median_absolute_deviation
            -MFCCs1_median, MFCCs1_median_absolute_deviation
            -MFCCs2_median, MFCCs2_median_absolute_deviation
            -MFCCs3_median, MFCCs3_median_absolute_deviation
            -MFCCs4_median, MFCCs4_median_absolute_deviation
            -MFCCs5_median, MFCCs5_median_absolute_deviation
            -MFCCs6_median, MFCCs6_median_absolute_deviation
            -MFCCs7_median, MFCCs7_median_absolute_deviation
            -MFCCs8_median, MFCCs8_median_absolute_deviation
            -MFCCs9_median, MFCCs9_median_absolute_deviation
            -MFCCs10_median, MFCCs10_median_absolute_deviation
            -MFCCs11_median, MFCCs11_median_absolute_deviation
            -MFCCs12_median, MFCCs12_median_absolute_deviation
            -MFCCs13_median, MFCCs13_median_absolute_deviation

        The method processTrainDataset() allows to process the training data of Mivia Audio Events Dataset.
        It parse the metadata within the xml files provided with the dataset in order to do the segmentation.

        In addition to the previuos ones, for each frame the following additinal "features" are computed:
            -target, [0 == glass, 1 == gunshots, 2 == screams, 3 ==  other]
            -frame, number of subframes
            -snr, snr in the range [1, 6]
            -id, id to easily recover the orginal file
            -background, background type [bells, crowd_claps, twistle, crowd, cars, household_app, rain, gaussian_noise]


                       |---------------------300ms--------------------|

                       |---------150ms---------|                        -------------> 1 sample, 42 features
                                   |---------150ms---------|
                                              |---------150ms---------|



    '''

    def __init__(self):
        self.dataPre = pre.DatasetPreprocessing()
        self.segmentation = 0.300
        self.frameSize = 0.150
        self.frameStep = 0.075  # 50% overlap
        self.discard = 21  # number of original features to retain
        self.label = ['Zero_Crossing_Rate_median', 'Zero_Crossing_Rate_median_absolute_deviation',
                      'Energy_median', 'Energy_median_absolute_deviation',
                      'Entropy_of_Energy_median', 'Entropy_of_Energy_median_absolute_deviation',
                      'Spectral_Centroid_median', 'Spectral_Centroid_median_absolute_deviation',
                      'Spectral_Spread_median',  'Spectral_Spread_median_absolute_deviation',
                      'Spectral_Entropy_median', 'Spectral_Entropy_median_absolute_deviation',
                      'Spectral_Flux_median', 'Spectral_Flux_median_absolute_deviation',
                      'Spectral_Rolloff_median',  'Spectral_Rolloff_median_absolute_deviation',
                      'MFCCs1_median', 'MFCCs1_median_absolute_deviation',
                      'MFCCs2_median', 'MFCCs2_median_absolute_deviation',
                      'MFCCs3_median', 'MFCCs3_median_absolute_deviation',
                      'MFCCs4_median', 'MFCCs4_median_absolute_deviation',
                      'MFCCs5_median', 'MFCCs5_median_absolute_deviation',
                      'MFCCs6_median', 'MFCCs6_median_absolute_deviation',
                      'MFCCs7_median', 'MFCCs7_median_absolute_deviation',
                      'MFCCs8_median', 'MFCCs8_median_absolute_deviation',
                      'MFCCs9_median', 'MFCCs9_median_absolute_deviation',
                      'MFCCs10_median', 'MFCCs10_median_absolute_deviation',
                      'MFCCs11_median', 'MFCCs11_median_absolute_deviation',
                      'MFCCs12_median', 'MFCCs12_median_absolute_deviation',
                      'MFCCs13_median', 'MFCCs13_median_absolute_deviation',
                      'target', 'frame', 'snr', 'id', 'background']

    def extractFeatures(self, eventsList, Fs, snr):
        feature = []
        for event in eventsList:
            frame = event.getData()

            F = audioFeatureExtraction.stFeatureExtraction(frame, Fs, self.frameSize * Fs, self.frameStep * Fs)
            raw_feature = F[:self.discard, :].T

            tmp = []
            for j in range(0, raw_feature.shape[1]):  # compute median and med for each columns
                feature_column = raw_feature[:, j]
                median = np.median(raw_feature[:, j])
                median_absolute_deviation = np.median(np.abs(feature_column - median))
                tmp.append(median)
                tmp.append(median_absolute_deviation)

            tmp.append(event.getTarget())  # add class label
            tmp.append(raw_feature.shape[0])  # add number of frame per signal
            tmp.append(snr)  # add snr
            tmp.append(event.getId())  # add id
            tmp.append(event.getBackground())  # add background type
            feature.append(tmp)

        return feature

    def update_progress(self, progress):
        barLength = 100  # Modify this to change the length of the progress bar
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(barLength * progress))
        text = "\rPercent: [{0}] {1}% {2}".format("#" * block + "-" * (barLength - block), int(round(progress*100)), status)
        sys.stdout.write(text)
        sys.stdout.flush()

    def writeToCSV(self, feature, numRow, numCol, file):
        tmp = []
        for row in feature:
            tmp.append(np.append(numRow, row))
            numRow[0] += 1

        fmt = '%s,' * numCol
        fmt = fmt[:-1]

        np.savetxt(file, tmp, delimiter=",", fmt=fmt)

    def processDataset(self, path, wavNum, snrRange, outputFile):
        file = open(outputFile, 'ab')

        header = ","
        for x in self.label:
            header += x + ","

        file.write((header[:len(header)-1]+'\n').encode('ascii'))  # write .csv header

        total = (wavNum-1)*float(snrRange)
        cont = [0]
        for i in range(1, wavNum):  # process all wav
            if i < 10:
                xml_path = path + '0000' + str(i) + '.xml'
                wav_base_path = path + 'sounds/0000' + str(i)
            else:
                xml_path = path + '000' + str(i) + '.xml'
                wav_base_path = path + 'sounds/000' + str(i)

            for j in range(1, snrRange+1):  # process differents snr  1=30db ... 6=5db
                eventsList = self.dataPre.segmentation(xml_path, wav_base_path + '_' + str(j) + '.wav')
                feature = self.extractFeatures(eventsList, self.dataPre.Fs, snr=j)

                self.writeToCSV(feature, cont, len(self.label)+1, file)

                progress = float(((i - 1) * (snrRange) + j) / total)
                self.update_progress(progress)  # display progressbar

# #############################################################
# ############IN ORDER TO CREATE TRAINING DATASET##############
# #############################################################

print("Pocessing training dataset...")
print("")
start_time = time.time()

fe = FeatureExtraction()
fe.processDataset(path='/home/valerio/Scrivania/stage/dataset/MIVIA_DB4_dist/training/',
                       wavNum=67, snrRange=6,
                       outputFile='out/validation3_training_dataset0300_overlap.csv')

elapsed_time = time.time()-start_time
print("")
print("Elapsed time: " + str(elapsed_time))

# #############################################################
# #############################################################
# #############################################################


#############################################################
############IN ORDER TO CREATE TESTING DATASET##############
#############################################################

# print("Pocessing testing dataset...")
# print("")
# start_time = time.time()
#
# fe = FeatureExtraction()
# fe.processDataset(path='/home/valerio/Scrivania/stage/dataset/MIVIA_DB4_dist/testing/',
#                        wavNum=30, snrRange=6,
#                        outputFile='out/validation3_testing_dataset0300_overlap.csv')
#
# elapsed_time = time.time()-start_time
# print("")
# print("Elapsed time: " + str(elapsed_time))


#############################################################
#############################################################
#############################################################