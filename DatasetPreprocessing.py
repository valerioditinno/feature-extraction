from pyAudioAnalysis import audioBasicIO
import xml.etree.ElementTree as et
import Event

class DatasetPreprocessing:
    '''
        This class implement prepocessing on Mivia Audio Events Dataset
        in order to locate and extract relevant events within the wav files
        provided into the dataset thanks to the metadata inside the xml files.
        Event's label:
            - glass --> "0"
            - gunshots --> "1"
            - screams --> "2"
            - other --> "3"
    '''

    def __init__(self):
        self.inter_events_distance = 0.5
        self.min_event_duration = 0.5
        self.avgLen = 0.0
        self.totalCont = 0
        self.avgEvent0Len = 0.0
        self.type0Cont = 0
        self.type0Under = 0
        self.avgEvent1Len = 0.0
        self.type1Cont = 0
        self.type1Under = 0
        self.avgEvent2Len = 0.0
        self.type2Cont = 0
        self.type2Under = 0
        self.avgEvent3Len = 0.0
        self.type3Cont = 0
        self.type3Under = 0
        self.min = 1000.0
        self.max = 0.0
        self.threshold = 0.3

    def updateStat(self, event):
        self.totalCont += 1
        eventStart = float(event.getStartSecond())
        eventStop = float(event.getStopSecond())
        eventType = event.getTarget()

        eventLen = eventStop - eventStart

        self.avgLen += eventLen
        if eventLen < self.min:
            self.min = eventLen
        if eventLen > self.max:
            self.max = eventLen

        if eventType == '0':
            self.avgEvent0Len += eventLen
            self.type0Cont += 1
            if eventLen < self.threshold:
                self.type0Under += 1
        elif eventType == '1':
            self.avgEvent1Len += eventLen
            self.type1Cont += 1
            if eventLen < self.threshold:
                self.type1Under += 1
        elif eventType == '2':
            self.avgEvent2Len += eventLen
            self.type2Cont += 1
            if eventLen < self.threshold:
                self.type2Under += 1
        elif eventType == '3':
            self.avgEvent3Len += eventLen
            self.type3Cont += 1
            if eventLen < self.threshold:
                self.type3Under += 1

    def showStat(self):
        print('Events stat...\n')

        print('Total events cont: ' + str(self.totalCont))
        print('Type 0 cont: ' + str(self.type0Cont))
        print('Type 1 events cont: ' + str(self.type1Cont))
        print('Type 2 events cont: ' + str(self.type2Cont) +'\n')

        print('Min: ' + str(self.min))
        print('Max: ' + str(self.max) + '\n')

        print('Event 0 avg length: ' + str(self.avgEvent0Len / self.type0Cont))
        print('Under: ' + str(self.type0Under))
        print('Event 1 avg length: ' + str(self.avgEvent1Len / self.type1Cont))
        print('Under: ' + str(self.type1Under))
        print('Event 2 avg length: ' + str(self.avgEvent2Len / self.type2Cont))
        print('Under: ' + str(self.type2Under))
        print('Event 3 avg length: ' + str(self.avgEvent3Len / self.type3Cont))
        print('Under: ' + str(self.type3Under))

        print('Total avg length: ' + str(self.avgLen / self.totalCont))

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

            event = Event(className[:-4], target, start, stop, background)
            eventsList.append(event)
            self.updateStat(event)

        return eventsList

    def extractRelevantEvents(self, Fs, data, eventsList):
        audioSamplesList = data.tolist()

        i = 0
        for event in eventsList:
            start = event.getStartSecond()
            stop = event.getStopSecond()

            tmp = []
            while i*(1.0 / Fs) < float(stop):
                if i*(1.0 / Fs) > float(start) and i*(1.0 / Fs) < float(stop):
                    tmp.append(audioSamplesList[i])
                i += 1

            event.setData(tmp)

        return eventsList

    def preProcessWav(self, xml_filename, wav_filename):
        eventsList = self.parseXml(xml_filename)

        [self.Fs, x] = audioBasicIO.readAudioFile(wav_filename)

        eventsList = self.extractRelevantEvents(self.Fs, x, eventsList)  # extract relevant events

        backgroundEventsList = []
        background = eventsList[0].getBackground()
        cont = 0
        for i in range(0, len(eventsList)-1):  # create metadata for background events
            if(i == 0):
                if(float(eventsList[i].getStartSecond())-2*self.inter_events_distance >= self.min_event_duration ):
                    target = "3"
                    start = 0 + self.inter_events_distance
                    stop = float(eventsList[i + 1].getStartSecond()) - self.inter_events_distance
                else:
                    continue
            else:
                if(float(eventsList[i + 1].getStartSecond()) - float(eventsList[i - 1].getStopSecond()) - 2*self.inter_events_distance >= self.min_event_duration ):
                    target = "3"
                    start = float(eventsList[i - 1].getStopSecond())+self.inter_events_distance
                    stop = float(eventsList[i + 1].getStartSecond())-self.inter_events_distance
                else:
                    continue
            backgroundEvent = Event("other"+wav_filename[-12:-4]+"_"+str(cont), target, start, stop, background)
            backgroundEventsList.append(backgroundEvent)
            cont += 1
            self.updateStat(backgroundEvent)

        backgroundEventsList = self.extractRelevantEvents(self.Fs, x, backgroundEventsList) # extract background events
        eventsList = eventsList + backgroundEventsList

        return eventsList