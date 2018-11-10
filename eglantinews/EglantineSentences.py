class EglantineSentences:

    DEFAULT_PROMPT = "Que puis je faire ?"
    LAUNCH_PROMPT = "Bonjour c'est Eglantine, que puis-je faire ?"
    TOO_LONG = "Je cherche toujours. Dîtes OK pour avoir ma réponse"
    UNKNOWN = "Je ne comprends pas"
    ERROR = "Une erreur s'est produite"
    ERROR_SERVICE = "Une erreur s'est produite dans le service %s"
    FORBIDDEN = "Accès non autorisé"
    BUSY = "Je suis déjà occupé. Peux-tu attendre un instant, s'il te plaît ?"

    @staticmethod
    def correct_prepositions(sentence: str):
        if sentence is None:
            return None
        return sentence \
            .replace(' de le ', ' du ') \
            .replace(' de les ', ' des ') \
            .replace(' à le ', ' au  ') \
            .replace(' à les ', ' aux ')
