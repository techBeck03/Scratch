import os
from helpers import Pigeon
KNOWN_SUBNETS_CSV = '/private/known_subnets.csv'

# Pigeon Messenger
PIGEON = Pigeon()

PIGEON.note.update({
    'status_code': 100,
    'message': 'Starting tasks for clear inventory filters cache',
    'data': {}
})
PIGEON.send()
try:
    os.remove(KNOWN_SUBNETS_CSV)
    PIGEON.note.update({
        'status_code': 200,
        'message': 'Starting tasks for clear inventory filters cache',
        'data': {}
    })
    PIGEON.send()
except:
    PIGEON.note.update({
        'status_code': 404,
        'message': 'An error occurred while deleting inventory filter cache file',
        'data': {
            'messages': ['An error occurred while deleting inventory filter cache file']
        }
    })
    PIGEON.send()
