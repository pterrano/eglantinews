class EglantineServiceResult:
    prompt: str = None

    sentence: str = None

    should_end_session: bool = None

    def __init__(self, sentence: str = None, should_end_session: bool = True, prompt: str = None):
        self.sentence = sentence
        self.should_end_session = should_end_session
        self.prompt = prompt

    def get_sentence(self) -> str:
        return self.sentence

    def get_prompt(self) -> str:
        return self.prompt

    def is_should_end_session(self) -> bool:
        return self.should_end_session

    def set_sentence(self, sentence: str):
        self.sentence = sentence

    def set_should_end_session(self, should_end_session: bool):
        self.should_end_session = should_end_session

    def set_prompt(self, prompt: str):
        self.prompt = prompt
