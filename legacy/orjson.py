import json

def dumps(obj, *args, **kwargs):
    return json.dumps(obj).encode()

def loads(obj, *args, **kwargs):
    return json.loads(obj)

class JSONDecodeError(Exception):
    pass
