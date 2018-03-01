"""
This script uploads annotations as a CSV file to Tetration. It assumes that
the annotations file already exists.
"""

# pylint: disable=invalid-name

import os
import json
import requests.packages.urllib3
import tetpyclient
from tetpyclient import RestClient

# this file is not persistent and contains only diffs from last time the
# script was run; it is non-persistent because it is saved to the local
# filesystem of the container and the container is deleted when it's done
ANNOTATIONS_DIFF_FILE = 'upload.csv'

# Helper function to send Pigeon messages back to ecohub
def print_message(message):
    '''
    prints a JSON object with indentation if the DEBUG environment variable
    is set and without indentation if it is not set
    '''
    if os.getenv('DEBUG'):
        print json.dumps(message, indent=4)
    else:
        print json.dumps(message)

# default message indicates the operation was successful
pigeon = {
    "status_code": 200,
    "data": {},
    "message": "Annotations posted successfully."
}

# upload the annotations file if it exists
if os.path.exists(ANNOTATIONS_DIFF_FILE):
    restclient = RestClient(
        os.environ['TETRATION_ENDPOINT'],
        api_key=os.environ['TETRATION_API_KEY'],
        api_secret=os.environ['TETRATION_API_SECRET'],
        verify=False
    )

    requests.packages.urllib3.disable_warnings()

    # this is taken from the sample code in the Tetration documentation
    file_path = '/<path_to_file>/user_annotations.csv'
    req_payload = [tetpyclient.MultiPartOption(key='X-Tetration-Oper', val='add')]
    resp = restclient.upload(ANNOTATIONS_DIFF_FILE, '/assets/cmdb/upload', req_payload)

    if resp.status_code == 200:
        print_message(pigeon)
    else:
        pigeon['status_code'] = resp.status_code
        pigeon['message'] = resp.text
        print_message(pigeon)

# if the annotations file doesn't exist, return an error
else:
    pigeon['status_code'] = 400
    pigeon['message'] = "Local copy of annotations file is missing."
    print_message(pigeon)
