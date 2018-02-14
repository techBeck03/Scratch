"""
The purpose of this script is to call other scripts. There are no arguments to 
this script. An environment variable named ACTION defines which action should
be taken (which script to run).
"""

import subprocess
import os
import json

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

# flag determines if this script has to echo content back to the screen; in
# most cases the script that is called will do that so it's not required
flag = False

if os.getenv('ACTION'):

    if os.environ['ACTION'] == 'TEST_CONNECTIVITY':
        subprocess.call(["python", "test_connectivity.py"])
else:
    pigeon['message'] = "The ACTION environment variable is not defined."
    pigeon['status_code'] = 404
    print_message(pigeon)

# print a message that the container has completed its work
pigeon['message'] = "Container is stopping."
pigeon['status_code'] = 100
print_message(pigeon)
