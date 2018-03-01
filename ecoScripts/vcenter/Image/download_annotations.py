
"""
Script used for testing only. This just downloads the annotations file.
During debug, it's easier to download the annotations via script than
through the GUI.
"""

# pylint: disable=invalid-name

import os
import requests.packages.urllib3
from tetpyclient import RestClient

restclient = RestClient(
    os.environ['TETRATION_ENDPOINT'],
    api_key=os.environ['TETRATION_API_KEY'],
    api_secret=os.environ['TETRATION_API_SECRET'],
    verify=False
)

requests.packages.urllib3.disable_warnings()

file_path = 'output.csv'
restclient.download(file_path, '/assets/cmdb/download')
