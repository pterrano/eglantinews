
class EglantineServiceResult:

    prompt:str

    sentence:str

    shouldEndSession:bool

    def __init__(self, sentence:str, shouldEndSession:bool=True, prompt:str=None):
        self.sentence=sentence
        self.shouldEndSession=shouldEndSession
        self.prompt=prompt

    def getSentence(self):
        return self.sentence

    def getPrompt(self):
        return self.prompt

    def isShouldEndSession(self):
        return self.shouldEndSession

    def setSentence(self, sentence:str):
        self.sentence=sentence

    def setShouldEndSession(self, shouldEndSession: bool):
        self.shouldEndSession=shouldEndSession

    def setPrompt(self, prompt:str):
        self.prompt=prompt



