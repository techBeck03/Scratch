"""

******************** WARNING: TEST CODE! DO NOT USE ********************

Script tests for connectivity to both Cisco Tetration and Infoblox
endpoints. The bulk of the work in this script is handling all of the
errors that might arise.

Author: Doron Chosnek, Cisco Systems, February 2018
"""

# pylint: disable=invalid-name

import json
import os
import requests.packages.urllib3

# needed for Tetration
from tetpyclient import RestClient

# format for return messages
pigeon = {
    "status_code": 100,
    "data": {},
    "message": ""
}

# ============================================================================
# Functions
# ----------------------------------------------------------------------------
def test_tetration():
    '''
    Function attempts to connect to Tetration. Arguments are retrieved from
    environment variables. The bulk of the work in this function is error
    handling. It returns a tuple that has a status code and an error message
    (which will be an empty string if there are no errors)
    '''
    status = 200
    return_msg = "Tetration connectivity verified."

    restclient = RestClient(
        os.environ['TETRATION_ENDPOINT'],
        api_key=os.environ['TETRATION_API_KEY'],
        api_secret=os.environ['TETRATION_API_SECRET'],
        verify=False
    )

    requests.packages.urllib3.disable_warnings()

    try:
        resp = restclient.get('/openapi/v1/filters/inventories')

    # most likely a DNS issue
    except requests.exceptions.ConnectionError as c_error:
        status = 404
        return_msg = "Error connecting to Tetration endpoint"
    except:
        status = 400
        return_msg = "Unknown error connecting to Tetration"
    else:
        status = resp.status_code
        # this doesn't work if the Tetration endpoint is specified as a valid
        # website (but not a TA endpoint) because it returns all of the HTML
        # for the whole website 
        if resp.status_code >= 400:
            return_msg = "Tetration " + str(resp.text).rstrip()

    return (status, return_msg)

# ============================================================================
# Main
# ----------------------------------------------------------------------------

result = {
    "status_code": 0,
    "data": {},
    "message": ""
}

handle_target = {
    'tetration': test_tetration()
}[os.environ['TARGET_TYPE']]

result['status_code'] = handle_target[0]
result['message'] = handle_target[1]
print json.dumps(result)
