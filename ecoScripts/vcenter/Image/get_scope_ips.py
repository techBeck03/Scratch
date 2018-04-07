"""
This script retrieves all of the IP addresses found in the specified scope and
saves them to a JSON file for the next script. This integration only provides
annotations for IP addresses that exist in the specified scope, so this script
creates that list of IP addresses.

Keyword environment variables:
--APPSCOPE_NAME: name of scope from which we want to retrieve all IP addresses
--TETRATION_ENDPOINT: URL of the Tetration UI
--TETRATION_API_KEY: key for Tetration API access
--TETRATION_API_SECRET: secret for the above key
--DEBUG: determines if Pigeons are displayed minimized or with indentation to
    make them more readable

The user must supply either a credentials file *OR* the key and secret as
arguments, but not both.

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

import os
import json
import requests.packages.urllib3
import tetpyclient
from tetpyclient import RestClient

# number of records retrieved per API call to Tetration
LIMIT = 100

# This file is used to pass a list of IP addresses from the given scope to the
# Powershell script that reads from vCenter. The file is not persistent because
# it is saved to the local filesystem of the container and the container is 
# deleted when it's done
IP_FILENAME = 'ip.json'

# Disable warnings
requests.packages.urllib3.disable_warnings()


# ============================================================================
# Main
# ----------------------------------------------------------------------------

restclient = RestClient(
    os.environ['TETRATION_ENDPOINT'],
    api_key=os.environ['TETRATION_API_KEY'],
    api_secret=os.environ['TETRATION_API_SECRET'],
    verify=False
)

# Payload specifies every IPV4 address in the given scope.
req_payload = {
    "filter": {"type": "and",
        "filters": [
            {"type": "eq", "field": "address_type", "value": "IPV4"}
        ]
    },
    "scopeName": os.environ['APPSCOPE_NAME'],
    "limit": LIMIT,
    "offset": ""
}

# this block of code gets LIMIT number of IP addresses at a time from Tetration
# and repeats as long as there are more addresses to retrieve
ip_list = []
while True:
    resp = restclient.post('/openapi/v1/inventory/search', json_body=json.dumps(req_payload))

    if resp.status_code == 200:
        parsed_resp = json.loads(resp.content)
        for item in parsed_resp["results"]:
            ip_list.append(item["ip"])

        if "offset" in parsed_resp:
            req_payload["offset"] = parsed_resp["offset"]
        else:
            break
    else:
        break

# save the results to a file
with open(IP_FILENAME, 'w') as outfile:
    json.dump(ip_list, outfile)

pigeon = {
    "status_code": 100,
    "data": {},
    "message": "Found {} IP addresses in the Tetration scope.".format(len(ip_list))
}

# send the pigeon... if DEBUG is enabled, then send it with indentation;
# otherwise send it as minified JSON
if os.getenv('DEBUG'):
    print json.dumps(pigeon, indent=4)
else:
    print json.dumps(pigeon)