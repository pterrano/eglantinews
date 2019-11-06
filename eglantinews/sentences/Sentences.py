class Sentences:
    """ Global """

    DEFAULT_PROMPT = "Que puis je faire ?"
    LAUNCH_PROMPT = "Bonjour c'est Eglantine, que puis-je faire ?"
    TOO_LONG = "Recherche en cours"
    UNKNOWN = "Je ne comprends pas"
    ERROR = "Une erreur s'est produite"
    ERROR_SERVICE = "Une erreur s'est produite dans le service %s"
    FORBIDDEN = "Accès non autorisé"
    BUSY = "Je suis déjà occupé"
    NOTHING = ""

    TURN_OFF_ALL = "Ok, j'éteins tout"

    """ TV """
    TURN_ON_TV = "Allumage de la télé"
    TURN_OFF_TV = "Extinction de la télé"

    PAUSE_TV = "Mise en pause"
    STOP_TV = "Arrêt du visionnage"
    RESUME_TV = "Reprise du visionnage"
    RETURN_TO_DIRECT = "Retour au direct"
    CHANGE_CHANNEL = "Je mets la chaine %s"

    TURN_ON = "Allumage de %s"
    TURN_OFF = "Arrêt de %s"

    """ Music """

    ALBUM_FOUND = "Ok, je mets l'album %s de %s %s"
    RADIO_FOUND = "Ok, je mets %s %s"
    ARTIST_FOUND = "Ok, je mets les titres de %s %s"
    TRACK_FOUND = "Ecoutons %s de %s %s"
    MOVIE_FOUND = "Visionnons %s"

    ALBUM_NOT_FOUND = "Je n'ai pas trouvé d'album %s"
    RADIO_NOT_FOUND = "Je n'ai pas trouvé la radio %s %s"
    ARTIST_NOT_FOUND = "Je n'ai pas trouvé de titre pour %s"
    TRACK_NOT_FOUND = "Je n'ai pas trouvé le titre %s"
    MOVIE_NOT_FOUND = "Je n'ai pas trouvé le film %s"

    MOVIE_ERROR_STARTED = "Une erreur s'est produite lors du démarrage du visionnage de %s"

    ENABLE_MULTIROOM = "Activation du multiroom"
    DISABLE_MULTIROOM = "Désactivation du multiroom"

    MUSIC_LOCATION = "dans %s"
    MUSIC_LOCATION_MULTIROOM = "de partout"

    NO_CURRENT_TRACK = "Aucun titre en cours"
    CURRENT_TRACK = "Nous écoutons actuellement le titre %s de %s"
    CURRENT_TRACK_WITH_ALBUM = "Nous écoutons actuellement le titre %s de %s dans l'album %s"

    PAUSE_MUSIC = "Pause de la musique %s"
    STOP_MUSIC = "Arrêt de la musique %s"
    RESUME_MUSIC = "Reprise de la musique %s"

    """ Volume """
    CURRENT_VOLUME = "Le volume est à %i dans %s."
    CURRENT_VOLUME_WITH_LOCATION = "Le volume est à %i dans %s. "

    VOLUME_RANGE = "Le volume maximum est de 100"
    VOLUME_MODIFICATION = "Modification du volume à %s"
    VOLUME_MODIFICATION_WITH_LOCATION = "Modification du volume à %s dans %s"


    NORMALISE_WORDS = [
        'les', 'des', 'aux', 'de', 'le', 'la', 'du', 'au', 'à', 'l\''
    ]

    @staticmethod
    def correct_prepositions(sentence: str) -> str:
        if sentence is None:
            return None
        return sentence \
            .replace(' de le ', ' du ') \
            .replace(' de les ', ' des ') \
            .replace(' à le ', ' au  ') \
            .replace(' à les ', ' aux ')

    @staticmethod
    def normalize_search(query: str) -> str:
        query = ' ' + query + ' '
        for word in Sentences.NORMALISE_WORDS:
            query = query.replace(' ' + word + ' ', ' ')
        return query.strip(' ')
