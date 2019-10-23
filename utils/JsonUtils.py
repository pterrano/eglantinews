import datetime
import json


def __default_serialize(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

def json_serialize(d):
    return json_serialize_dict(vars(d))


def json_serialize_dict(d: dict):
    return json.dumps(
        d,
        sort_keys=True,
        indent=1,
        default=__default_serialize
    )
