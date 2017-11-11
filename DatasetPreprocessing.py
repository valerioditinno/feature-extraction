from pyAudioAnalysis import audioBasicIO
import xml.etree.ElementTree as et
import Event

class DatasetPreprocessing:
    '''
        This class implement segmentation with overlap on Mivia Audio Events Dataset.
        Labels are assigned according to metadata within the xml files provided with the dataset.


                                                [0 == glass, 1 == gunshots, 2 == screams, 3 ==  other]

                                       _________________
         ________________             |                 |               _____   _____       _____
        |______.wav______|---input--->|  preProcessing  |---output---> |_'3'_| |_'1'_| ... |_'0'_|
                                      |_________________|

        Example:

        frameSize = 0.300
        overlap = 0.150


            <--- ... ----background-------><----gun----------><--------background------ ... --->

                 ...
         '3'    |---------300ms---------|
         drop              |---------300ms---------|
         '1'                           |---------300ms---------|
         drop                          <-20%->     |---------300ms---------|
         '3'                                                   |---------300ms---------|
                            <---150ms--->                                        ....
    '''

    def __init__(self):
        self.frameSize = 0.300
        self.overlap = 0.150
        self.tolerance = 0.2

    def parseXml(self, filename):
        tree = et.parse(filename)
        root = tree.getroot()

        background = ""
        for j in root.findall("./background/item"):
            background = background + "+" + j.find('SUBCLASS').text
        background = background[1:]

        eventsList = []
        for i in root.findall("./events/item"):
            className = i.find('CLASS_NAME').text
            if(className.startswith("glass")):
                target = "0"
            elif(className.startswith("gunshots")):
                target = "1"
            else:
                target = "2"
            start = i.find('STARTSECOND').text
            stop = i.find('ENDSECOND').text

            event = Event.Event(className[:-4], target, start, stop, background)
            eventsList.append(event)

        return eventsList

    def segmentation(self, xml_filename, wav_filename):
        eventsList = self.parseXml(xml_filename)

        [self.Fs, x] = audioBasicIO.readAudioFile(wav_filename)

        segmentedFileList = []
        curPos = 0
        N = len(x)
        Win = int(self.Fs*self.frameSize)
        Step = int(self.Fs*self.overlap)
        index = 0

        while curPos + Win - 1 < N:
            curFrame = x[curPos:curPos + Win]

            curEvent = eventsList[index]
            start = float(curEvent.getStartSecond())*self.Fs
            stop = float(curEvent.getStopSecond())*self.Fs

            # debug print
            # print('start win ' + str(curPos))
            # print('start win +20% ' + str(curPos + self.tolerance*Win))
            # print('stop win ' + str(curPos + Win))
            # print('stop win -20% ' + str(curPos + Win - self.tolerance*Win))
            #
            # print('start event ' + str(start))
            # print('stop event ' + str(stop))

            if curPos + Win - self.tolerance*Win < start:
                target = "3"
                backgorundEvent = Event.Event("other" + wav_filename[-12:-4], target, None, None,
                                              curEvent.getBackground(), curFrame)
                segmentedFileList.append(backgorundEvent)
            elif curPos + self.tolerance*Win >= start and curPos + Win - self.tolerance*Win <= stop:
                relevantEvent = Event.Event(curEvent.getId(), curEvent.getTarget(),
                                            None, None,
                                            curEvent.getBackground(), curFrame)
                segmentedFileList.append(relevantEvent)
            elif curPos + self.tolerance*Win > stop:
                if index < len(eventsList)-1:
                    index += 1
                target = "3"
                backgorundEvent = Event.Event("other"+wav_filename[-12:-4], target, None, None,
                                              curEvent.getBackground(), curFrame)
                segmentedFileList.append(backgorundEvent)

            curPos = curPos + Step

        return segmentedFileList