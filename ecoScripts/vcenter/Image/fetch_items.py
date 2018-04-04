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

import requests.packages.urllib3
from tetpyclient import RestClient

# Disable warnings
requests.packages.urllib3.disable_warnings()

VC_HOST = os.environ['VCENTER_HOST']
VC_USER = os.environ['VCENTER_USER']
VC_PWD = os.environ['VCENTER_PWD']
TARGET_ITEM = os.environ['FETCH_TARGET']

# =============================================================================
# Functions
# -----------------------------------------------------------------------------

def tet_connect():
    ''' Connects to Tetration using params stored in environment variables. '''
    return RestClient(
            os.environ['TETRATION_ENDPOINT'],
            api_key=os.environ['TETRATION_API_KEY'],
            api_secret=os.environ['TETRATION_API_SECRET'],
            verify=False
        )

def tet_get_vrfs(exclusions):
    ''' Returns list of all VRFs (except exclusions) '''
    restclient = tet_connect()
    resp = restclient.get('/openapi/v1/vrfs')
    return [x for x in resp.json() if x['name'] not in exclusions]

def tet_get_scopes():
    restclient = tet_connect()
    vrf_list = tet_get_vrfs(exclusions=[])
    vrf_id = 1
    for v in vrf_list:
        if v['name'] == os.environ['TENANT_VRF']:
            vrf_id = v['vrf_id']
            break
    resp = restclient.get('/openapi/v1/app_scopes')
    return [x['name'] for x in resp.json() if x['vrf_id'] == vrf_id]


# =============================================================================
# Main
# -----------------------------------------------------------------------------

# set up the structure for the message to be returned to ecohub
pigeon = {
        "status_code": 400,
        "data": [],
        "message": ""
    }

# at this time, we only handle one fetch command
if TARGET_ITEM == 'DATACENTERS':

    # required workaround documented at:
    # https://github.com/vmware/pyvmomi/commit/92c1de5056be7c5390ac2a28eb08ad939a4b7cdd
    context = ssl._create_unverified_context()

    vc = SmartConnect(host=VC_HOST, user=VC_USER, pwd=VC_PWD, sslContext=context)

    content = vc.RetrieveContent()
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

elif TARGET_ITEM == 'VRFS':

    vrfs = tet_get_vrfs(exclusions=['Unknown', 'Tetration'])

    if len(vrfs) > 0:
        pigeon['status_code'] = 200
        pigeon['message'] = "Found {} tenant VRFs.".format(len(vrfs))
        pigeon['data'] = [{'name': x['name'], 'value': x['name']} for x in vrfs]
    else:
        pigeon['status_code'] = 400
        pigeon['message'] = 'Could not find any tenant VRFs.'

elif TARGET_ITEM == 'SCOPES':

    scopes = tet_get_scopes()
    if len(scopes) > 0:
        pigeon['status_code'] = 200
        pigeon['message'] = "Found {} scopes.".format(len(scopes))
        pigeon['data'] = [{'name': x, 'value': x} for x in scopes]
    else:
        pigeon['status_code'] = 400
        pigeon['message'] = 'Could not find any scopes.'


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
    