"""
This script originally tested connectivity to both Cisco Tetration and VMware
vCenter endpoints, but the Tetration test has been moved to another part of
the ecohub project. This code now only tests vCenter connectivity.
The bulk of the work is handling all of the errors that might arise.

Keyword environment variables:
--VCENTER_HOST: hostname or IP address for vCenter
--VCENTER_USER: username with proper capabilities in vCenter
--VCENTER_PWD: password for vCenter
--DEBUG: determines if Pigeons are displayed minimized or with indentation to
    make them more readable

Copyright (c) 2018 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Doron Chosnek"
__copyright__ = "Copyright (c) 2018 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"


# pylint: disable=invalid-name

import json
import os

# needed for Tetration
# import requests.packages.urllib3
# from tetpyclient import RestClient

# needed for vCenter
import ssl
import sys
import socket
from pyVim.connect import SmartConnect
from pyVmomi import vmodl

# ============================================================================
# Functions
# ----------------------------------------------------------------------------

def test_vcenter():
    '''
    Function attempts to connect to vCenter. Arguments are retrieved from
    environment variables. The bulk of the work in this function is error
    handling. It returns a tuple that has a status code and an error message
    (which will be an empty string if there are no errors)
    '''
    status = 200
    return_msg = "vCenter connectivity verified."
    VC_HOST = os.environ['VCENTER_HOST']
    VC_USER = os.environ['VCENTER_USER']
    VC_PWD = os.environ['VCENTER_PWD']

    # required workaround documented at:
    # https://github.com/vmware/pyvmomi/commit/92c1de5056be7c5390ac2a28eb08ad939a4b7cdd
    context = ssl._create_unverified_context()

    try:
        vc = SmartConnect(host=VC_HOST, user=VC_USER, pwd=VC_PWD, sslContext=context)
    except vmodl.MethodFault as error:
        return_msg = "VCENTER " + error.msg
        status = 400
    # this exception handles the case of an invalid DNS name and we have to replace
    # any apostrophes in the error message
    except socket.error as error:
        return_msg = "VCENTER " + str(error).replace("'", "")
        status = 400
    # this is a catch-all except statement that is required because of the way
    # pyvmomi raises some of its exceptions
    except:
        return_msg = "VCENTER " + str(sys.exc_info()[1])
        status = 400

    # now make sure the Datacenter name exists
    DCENTER = os.environ['VCENTER_DATACENTER']
    if status == 200 and len(DCENTER):
        try:
            if DCENTER not in [dc.name for dc in vc.content.rootFolder.childEntity]:
                return (400, "VCENTER datacenter '{}' not found".format(DCENTER))
        except:
            return (400, "Error retrieving list of datacenters from VCENTER")

    return (status, return_msg)

# def test_tetration():
#     '''
#     Function attempts to connect to Tetration. Arguments are retrieved from
#     environment variables. The bulk of the work in this function is error
#     handling. It returns a tuple that has a status code and an error message
#     (which will be an empty string if there are no errors)
#     '''
#     status = 100
#     return_msg = "Tetration connectivity verified."

#     restclient = RestClient(
#         os.environ['TETRATION_ENDPOINT'],
#         api_key=os.environ['TETRATION_API_KEY'],
#         api_secret=os.environ['TETRATION_API_SECRET'],
#         verify=False
#     )

#     requests.packages.urllib3.disable_warnings()

#     try:
#         resp = restclient.get('/openapi/v1/filters/inventories')

#     # most likely a DNS issue
#     except requests.exceptions.ConnectionError as c_error:
#         status = 404
#         return_msg = "Error connecting to Tetration endpoint"
#     except:
#         status = 400
#         return_msg = "Unknown error connecting to Tetration"
#     else:
#         # this doesn't work if the Tetration endpoint is specified as a valid
#         # website (but not a TA endpoint) because it returns all of the HTML
#         # for the whole website and it takes a long time to timeout
#         if resp.status_code == 200:
#             status = 100
#         if resp.status_code >= 400:
#             status = resp.status_code
#             return_msg = "Tetration " + str(resp.text).rstrip()

#     return (status, return_msg)

# ============================================================================
# Main
# ----------------------------------------------------------------------------

if __name__ == "__main__":

    pigeon = {
        "status_code": 0,
        "data": {},
        "message": ""
    }

    pigeon['status_code'], pigeon['message'] = test_vcenter()

    if os.getenv('DEBUG'):
        print json.dumps(pigeon, indent=4)
    else:
        print json.dumps(pigeon)
