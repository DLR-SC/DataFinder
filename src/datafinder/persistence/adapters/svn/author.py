class AuthorProperty(object):

    def __init__(self, argsDict):
        self.argsDict = argsDict

    def validate(self, propertyName):
        pass

    def helpText(self, propertyName):
        return u"Hilfe"

    def displayName(self, propertyName):
        pass
          
    def defaultValue(self, propertyName):
        pass