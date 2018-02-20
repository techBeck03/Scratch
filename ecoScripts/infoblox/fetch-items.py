import os 
from infoblox_client import connector
import json
from helpers import *
import sys
import os
import netaddr
import time
import csv

# ====================================================================================
# GLOBALS
# ------------------------------------------------------------------------------------
QUERY_LIMIT = 10
# Read in environment variables
TARGET_ITEM = os.getenv('FETCH_TARGET')

# Tetration
TETRATION_ENDPOINT = os.getenv('TETRATION_ENDPOINT')
TETRATION_API_KEY = os.getenv('TETRATION_API_KEY')
TETRATION_API_SECRET = os.getenv('TETRATION_API_SECRET')
TETRATION_OPTS = {
    'limit': QUERY_LIMIT
}

# Infoblox
INFOBLOX_OPTS = {
    'host': os.getenv('INFOBLOX_HOST'),
    'username': os.getenv('INFOBLOX_USER'),
    'password': os.getenv('INFOBLOX_PWD'),
    'ssl_verify': False,
    'silent_ssl_warnings': True, # change from default
    'http_request_timeout': 3,   # change from default
    'http_pool_connections': 10,
    'http_pool_maxsize': 10,
    'max_retries': 2,            # change from default
    'wapi_version': '2.5',
    'max_results': QUERY_LIMIT,            # change from default
    'log_api_calls_as_info': False,
    'paging': False
}

# Pigeon Messenger
PIGEON = Pigeon()
# Connect to infoblox
infoblox = Infoblox_Helper(opts=INFOBLOX_OPTS,pigeon=PIGEON)
# Connect to tetration   
tetration = Tetration_Helper(TETRATION_ENDPOINT, TETRATION_API_KEY, TETRATION_API_SECRET,PIGEON,TETRATION_OPTS)

# Debug function used for printing formatted dictionaries
def PrettyPrint(target):
    print json.dumps(target,sort_keys=True,indent=4)

def get_app_scopes():
    result_array = []
    tetration.GetApplicationScopes()
    for scope in tetration.scopes:
        result_array.append({
            'label': scope["name"],
            'value': scope["id"]
        })
    return result_array

def get_extensible_attributes():
    result_array = []
    for attribute in infoblox.GetExtensibleAttributes():
        result_array.append({
            'label': attribute["name"],
            'value': attribute["name"]
        })
    return result_array

def main():
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Starting tasks for infoblox inventory filters',
        'data' : {}
    })
    PIGEON.send()

    fetch_result = {
        'APP_SCOPES': get_app_scopes(),
        'EXT_ATTRS': get_extensible_attributes()
    }[TARGET_ITEM]

    PIGEON.note.update({
        'status_code': 200,
        'message' : 'All tasks completed for infoblox inventory filters',
        'data' : fetch_result[0]
    })
    PIGEON.send()

if __name__ == "__main__":
    main()
