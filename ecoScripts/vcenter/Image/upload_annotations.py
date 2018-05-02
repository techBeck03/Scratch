"""
upload_annotations.py uploads an annotations CSV file to Tetration. The CSV
should be located in local storage.

Keyword environment variables:
--MULTITENANT: on/off to indicate if the file should be uploaded to a VRF
--TENANT_VRF: name of the VRF to which we upload the CSV; if not in multi-
    tenant mode, then this variable is ignored
--TETRATION_ENDPOINT: URL of the Tetration UI
--TETRATION_API_KEY: key for Tetration API access
--TETRATION_API_SECRET: secret for the above key

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

# ============================================================================
# Globals
# ----------------------------------------------------------------------------

# this file is not persistent and contains only diffs from last time the
# script was run; it is non-persistent because it is saved to the local
# filesystem of the container and the container is deleted when it's done
ANNOTATIONS_DIFF_FILE = 'upload.csv'
DISPLAY_ON_TEXT = ['on', 'true', 'yes', '1', 'okay']

if os.environ['MULTITENANT'].lower() in DISPLAY_ON_TEXT:
    APPSCOPE = '/' + os.environ['TENANT_VRF']
else:
    APPSCOPE = ''

# ============================================================================
# Main
# ----------------------------------------------------------------------------

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

    # This is taken from the sample code in the Tetration documentation. The
    # URL is very important. There cannot be a slash (/) at the end of the URL.
    # That is why we add the slash to to the beginning of the APPSCOPE global.
    # When not in multitenant mode, APPSCOPE is just an empty string and the
    # URL will still end without a slash.
    file_path = '/<path_to_file>/user_annotations.csv'
    req_payload = [tetpyclient.MultiPartOption(key='X-Tetration-Oper', val='add')]
    resp = restclient.upload(ANNOTATIONS_DIFF_FILE, '/assets/cmdb/upload' + APPSCOPE, req_payload)

    # if we get an error from Tetration, pass that through to ecohub
    if resp.status_code != 200:
        pigeon['status_code'] = resp.status_code
        pigeon['message'] = resp.text

# if the annotations file doesn't exist, there is nothing to do
else:
    pigeon['message'] = "Nothing to upload."

# send results to ecohub
print json.dumps(pigeon)
