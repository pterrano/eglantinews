class EglantineConstants:
    CURRENT_SERVICE_CHANGED = "common.changed-service"
    CURRENT_SERVICE = "common.current-service"
    LAST_SERVICES = 'common.last-services'
    DEFAULT_SERVICE_TIMEOUT = 6

    OK_INTENT = 'OK'
    LAUNCH_INTENT = 'LaunchRequest'
    INTENT_REQUEST_TYPE = 'IntentRequest'
    END_SESSION_REQUEST_TYPE = 'SessionEndedRequest'


class QueryType:
    LISTEN_TRACK = 0
    LISTEN_ALBUM = 1
    LISTEN_ARTIST = 2
    LISTEN_RADIO = 3
