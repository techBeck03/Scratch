"""
This script originally tested connectivity to both Cisco Tetration and
Infoblox endpoints, but the Tetration test has been moved to another part of
the ecohub project. This code now only tests Infoblox connectivity.
The bulk of the work is handling all of the errors that might arise.
Author: Doron Chosnek, Cisco Systems, February 2018
"""

# pylint: disable=invalid-name

import json
import os
import helpers

# needed for Infoblox
from infoblox_client import connector
from infoblox_client import exceptions as ib_e

# ============================================================================
# Global Variables
# ----------------------------------------------------------------------------
PIGEON = helpers.Pigeon()

# ============================================================================
# Functions
# ----------------------------------------------------------------------------

def test_infoblox():
    '''
    Function attempts to connect to Infoblox. Arguments are retrieved from
    environment variables. The bulk of the work in this function is error
    handling. It returns a tuple that has a status code and an error message
    (which will be an empty string if there are no errors)
    '''

    # defaults are document here:
    # https://github.com/infobloxopen/infoblox-client/blob/master/infoblox_client/connector.py
    infoblox_opts = {
        'host': os.environ['INFOBLOX_HOST'],
        'username': os.environ['INFOBLOX_USER'],
        'password': os.environ['INFOBLOX_PWD'],
        'ssl_verify': False,
        'silent_ssl_warnings': True, # change from default
        'http_request_timeout': 3,   # change from default
        'http_pool_connections': 10,
        'http_pool_maxsize': 10,
        'max_retries': 2,            # change from default
        'wapi_version': '2.2',
        'max_results': 2,            # change from default
        'log_api_calls_as_info': False,
        'paging': False
    }

    status = 200
    return_msg = "Infoblox connectivity verified."
    infoblox = helpers.Infoblox_Helper(infoblox_opts)

    try:
        result = infoblox.client.get_object('networkview')
    except ib_e.InfobloxBadWAPICredential:
        return_msg = "Infoblox: invalid credentials"
        status = 400
    except ib_e.InfobloxTimeoutError:
        return_msg = "Infoblox: timeout"
        status = 400
    except:
        return_msg = "Infoblox: unknown error connecting to Infoblox"
        status = 400
    else:
        # if the result is None then we've hit a valid IP that is not an
        # Infoblox instance
        if result is None:
            return_msg = "Infoblox: Invalid endpoint. Check IB IP address."
            status = 400
        # if the result is not a list, we have some kind of invalid result
        elif type(result) is not list:
            return_msg = "Infoblox: " + str(result)
            status = 400

    return (status, return_msg)


# ============================================================================
# Main
# ----------------------------------------------------------------------------

def main():
    result = test_infoblox()
    PIGEON.note.update({
        "status_code": result[0],
        "data": {},
        "message": result[1]
    })
    PIGEON.send()

if __name__ == "__main__":
    main()