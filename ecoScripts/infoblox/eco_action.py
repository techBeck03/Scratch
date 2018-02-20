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

# flag determines if this script has to echo content back to the screen; in
# most cases the script that is called will do that so it's not required
flag = False

if os.getenv('ACTION'):
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Starting action ' + os.environ['ACTION'],
        'data' : {}
    })
    PIGEON.send()
    result = {
        'TEST_CONNECTIVITY': subprocess.call(["python", "test_connectivity.py"]),
        'RUN_INTEGRATION': subprocess.call(["python", "annotate-host.py"]),
        'CREATE_FILTERS': subprocess.call(["python", "create-inventory-filters.py"]),
        'FETCH_ITEMS': subprocess.call(["python", "fetch-items.py"]),
    }[os.environ['ACTION']]
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
    'message' : 'All actions completed',
    'data' : {}
})
PIGEON.send()
