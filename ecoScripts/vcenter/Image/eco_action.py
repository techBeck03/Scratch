"""
The purpose of this script is to call other scripts. There are no arguments to
this script. An environment variable named ACTION defines which action should
be taken (which script to run).

Author: Doron Chosnek, Cisco Systems, January 2018
"""

import subprocess
import os
import json
import glob

def print_message(message):
    '''
    prints a JSON object with indentation if the DEBUG environment variable
    is set and without indentation if it is not set
    '''
    if os.getenv('DEBUG'):
        print json.dumps(message, indent=4)
    else:
        print json.dumps(message)

# return a message that the container has started
pigeon = {
    "status_code": 100,
    "data": {},
    "message": "Container has started."
}
print_message(pigeon)

if os.getenv('ACTION'):

    if os.environ['ACTION'] == 'TEST_CONNECTIVITY':
        subprocess.call(["python", "test_connectivity.py"])
    elif os.environ['ACTION'] == 'RUN_INTEGRATION':
        subprocess.call(["pwsh", "Get-Inventory.ps1"])
        subprocess.call(["python", "upload_annotations.py"])
    elif os.environ['ACTION'] == 'CLEAR_CACHE':
        for file in glob.glob("/private/*.txt"):
            os.remove(file)
        for file in glob.glob("/private/*.csv"):
            os.remove(file)
        pigeon['message'] = "Local cache of annotations deleted."
        pigeon['status_code'] = 200
        print_message(pigeon)
    elif os.environ['ACTION'] == 'FETCH_ITEMS':
        subprocess.call(["python", "fetch_items.py"])
    elif os.environ['ACTION'] == 'CUSTOM':
        pigeon['message'] = "Requested action CUSTOM not implemented."
        pigeon['status_code'] = 400
        print_message(pigeon)
    else:
        pigeon['message'] = "Requested action not recognized."
        pigeon['status_code'] = 404
        print_message(pigeon)
else:
    pigeon['message'] = "The ACTION environment variable is not defined."
    pigeon['status_code'] = 404
    print_message(pigeon)

# print a message that the container has completed its work
pigeon['message'] = "Container is stopping."
pigeon['status_code'] = 100
print_message(pigeon)
