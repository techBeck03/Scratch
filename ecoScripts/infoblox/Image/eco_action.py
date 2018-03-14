"""
The purpose of this script is to call other scripts. There are no arguments to 
this script. An environment variable named ACTION defines which action should
be taken (which script to run).
"""

import subprocess
import os
import json
import helpers

# Define pigeon messenger
PIGEON = helpers.Pigeon()

def run_integration():
    subprocess.call(["python", "annotate-host.py"])
    if os.environ['AUTO_UPDATE'] is True:
        subprocess.call(["python", "create-inventory-filters.py"])

if os.getenv('ACTION'):
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Starting action ' + os.environ['ACTION'],
        'data' : {}
    })
    PIGEON.send()
    options = {
        'TEST_CONNECTIVITY': lambda : subprocess.call(["python", "test_connectivity.py"]),
        'RUN_INTEGRATION': run_integration,
        'CREATE_FILTERS': lambda : subprocess.call(["python", "create-inventory-filters.py"]),
        'FETCH_ITEMS': lambda: subprocess.call(["python", "fetch-items.py"])
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
