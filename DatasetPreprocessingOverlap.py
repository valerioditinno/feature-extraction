from pyAudioAnalysis import audioBasicIO
import xml.etree.ElementTree as et
import Event

class DatasetPreprocessingOverlap:
    '''
        This class implement stream prepocessing segmentation on Mivia Audio Events Dataset
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

            # print('start win ' + str(curPos))
            # print('start win +20% ' + str(curPos + self.tolerance*Win))
            # print('stop win ' + str(curPos + Win))
            # print('stop win -20% ' + str(curPos + Win - self.tolerance*Win))
            #
            # print('start event ' + str(start))
            # print('stop event ' + str(stop))

            if curPos + Win - self.tolerance*Win < start:
                # print(1)
                target = "3"
                backgorundEvent = Event.Event("other" + wav_filename[-12:-4], target, None, None,
                                              curEvent.getBackground(), curFrame)
                segmentedFileList.append(backgorundEvent)
            elif curPos + self.tolerance*Win >= start and curPos + Win - self.tolerance*Win <= stop:
                # print(2)
                relevantEvent = Event.Event(curEvent.getId(), curEvent.getTarget(),
                                            None, None,
                                            curEvent.getBackground(), curFrame)
                segmentedFileList.append(relevantEvent)
            elif curPos + self.tolerance*Win > stop:
                # print(3)
                if index < len(eventsList)-1:
                    # print(4)
                    index += 1
                target = "3"
                backgorundEvent = Event.Event("other"+wav_filename[-12:-4], target, None, None,
                                              curEvent.getBackground(), curFrame)
                segmentedFileList.append(backgorundEvent)
            # else:  # else drop curFrame
                # print(5)

            curPos = curPos + Step

        return segmentedFileList