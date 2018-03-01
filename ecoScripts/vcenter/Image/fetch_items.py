"""
This script is set up to fetch data, but at this time it only responds to
one fetch command: fetch datacenter names.
It returns that list in the 'data' portion of an ecohub pigeon message.

Author: Doron Chosnek, Cisco Systems, February 2018
"""

# pylint: disable=invalid-name

import os
import ssl
import json
from pyVim.connect import SmartConnect
from pyVmomi import vim

VC_HOST = os.environ['VCENTER_HOST']
VC_USER = os.environ['VCENTER_USER']
VC_PWD = os.environ['VCENTER_PWD']
TARGET_ITEM = os.environ['FETCH_TARGET']

# required workaround documented at:
# https://github.com/vmware/pyvmomi/commit/92c1de5056be7c5390ac2a28eb08ad939a4b7cdd
context = ssl._create_unverified_context()

vc = SmartConnect(host=VC_HOST, user=VC_USER, pwd=VC_PWD, sslContext=context)
content = vc.RetrieveContent()

# set up the structure for the message to be returned to ecohub
pigeon = {
        "status_code": 400,
        "data": [],
        "message": "Found {} Datacenters.".format(len(dcenters))
    }

# at this time, we only handle one fetch command
if TARGET_ITEM == 'DATACENTERS':

    # A list comprehension of all the root folder's first tier children...
    dcenters = [entity for entity in content.rootFolder.childEntity if hasattr(entity, 'vmFolder')]

    # if we found at least one datacenter, return it
    if len(dcenters) > 0:
        pigeon['status_code'] = 200
        pigeon['message'] = "Found {} Datacenters.".format(len(dcenters))
        pigeon['data'] = [{'label': dc.name, 'value': dc.name} for dc in dcenters]
    else:
        pigeon['status_code'] = 400
        pigeon['message'] = 'Could not find any datacenters.'

# if this code is executing, ecohub asked us to fetch something we don't 
# know how to fetch
else:
    pigeon['status_code'] = 400
    pigeon['message'] = 'I did not recognize that fetch command.'


# send the pigeon... if DEBUG is enabled, then send it with indentation;
# otherwise send it as minified JSON
if os.getenv('DEBUG'):
    print json.dumps(pigeon, indent=4)
else:
    print json.dumps(pigeon)
    