class Event:
    '''
           Support class to store info about the event
    '''

    def __init__(self, id, target, start, stop, background, data=None):
        self.id = id
        self.target = target
        self.startSecond = start
        self.stopSecond = stop
        self.background = background
        self.data = data

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data

    def getId(self):
        return self.id

    def getTarget(self):
        return self.target

    def getStartSecond(self):
        return self.startSecond

    def getStopSecond(self):
        return self.stopSecond

    def getBackground(self):
        return self.background

    def debug(self):
        print(self.getData())
        print(self.getId())
        print(self.getTarget())
        print(self.getStartSecond())
        print(self.getStopSecond())
        print(self.getBackground())