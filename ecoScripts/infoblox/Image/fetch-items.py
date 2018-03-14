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
QUERY_LIMIT = 200
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
    'wapi_version': '2.2',
    'max_results': QUERY_LIMIT,            # change from default
    'log_api_calls_as_info': False,
    'paging': True
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

def get_app_scope_ids():
    result_array = []
    tetration.GetApplicationScopes()
    for scope in tetration.scopes:
        result_array.append({
            'label': scope["name"],
            'value': scope["id"]
        })
    return sorted(result_array, key=lambda k: k['label'])

def get_tenant_scope_names():
    result_array = []
    tenants = tetration.GetTenantNames()
    for tenant in tenants:
        if tenant["name"] not in ['Default', 'Unknown', 'Tetration']:
            result_array.append({
                'label': tenant["name"],
                'value': tenant["name"]
            })
    return sorted(result_array, key=lambda k: k['label'])

def get_extensible_attributes():
    result_array = []
    for attribute in infoblox.GetExtensibleAttributes():
        result_array.append({
            'label': attribute["name"],
            'value': attribute["name"]
        })
    return sorted(result_array, key=lambda k: k['label'])

def main():
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Starting tasks for fetch items',
        'data' : {}
    })
    PIGEON.send()

    options = {
        'APP_SCOPE_IDS': get_app_scope_ids,
        'TENANT_SCOPE_NAMES': get_tenant_scope_names,
        'EXT_ATTRS': get_extensible_attributes
    }
    fetch_result = options[TARGET_ITEM]()

    PIGEON.note.update({
        'status_code': 200,
        'message' : 'All tasks completed for fetch items',
        'data' : fetch_result
    })
    PIGEON.send()

if __name__ == "__main__":
    main()
