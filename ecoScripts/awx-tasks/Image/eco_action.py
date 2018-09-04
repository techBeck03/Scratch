"""
The purpose of this script is to call other scripts. There are no arguments to 
this script. An environment variable named ACTION defines which action should
be taken (which script to run).
"""

import subprocess
import os
import json
from pigeon import Pigeon

# Define pigeon messenger
PIGEON = Pigeon()

if os.getenv('ACTION'):
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Starting action ' + os.environ['ACTION'],
        'data' : {}
    })
    PIGEON.send()
    options = {
        'TEST_CONNECTIVITY': lambda : subprocess.call(["python", "test_connectivity.py"]),
        'RUN_INTEGRATION': lambda : subprocess.call(["python", "run-templates.py"]),
        'VALIDATE': lambda : subprocess.call(["python", "validate.py"]),
        'FETCH_ITEMS': lambda : subprocess.call(["python", "fetch-items.py"])
    }
    result = options[os.environ['ACTION']]()
else:
    PIGEON.note.update({
        'status_code': 404,
        'message' : 'Action: ' + os.getenv('ACTION') + 'not implemented',
        'data' : {}
    })
    PIGEON.send()

# print a message that the container has completed its work
PIGEON.note.update({
    'status_code': 100,
    'message' : 'Action complete',
    'data' : {}
})
PIGEON.send()
