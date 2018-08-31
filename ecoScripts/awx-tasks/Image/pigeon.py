import json

class Pigeon(object):
    def __init__(self):
        self.note = {
            "status_code" : 0,
            "message" : "",
            "data" : {}
        }

    def send(self):
        print json.dumps(self.note)