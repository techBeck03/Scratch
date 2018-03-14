import os 
from infoblox_client import connector
import yaml
import json
from helpers import *
import sys
import os
import netaddr
import time
import requests

# ====================================================================================
# GLOBALS
# ------------------------------------------------------------------------------------
# Read in environment variables
QUERY_LIMIT = 200
ANNOTATION_CSV_FILENAME = '/private/user_annotations.csv'
# Tetration
TETRATION_ENDPOINT = os.environ['TETRATION_ENDPOINT']
TETRATION_API_KEY = os.environ['TETRATION_API_KEY']
TETRATION_API_SECRET = os.environ['TETRATION_API_SECRET']
TETRATION_OPTS = {
    'limit': QUERY_LIMIT
}
TETRATION_TENANT_SCOPE_NAME = json.loads(os.environ['ANNOTATION_TENANT_SCOPE_NAME'])[0]["value"]

# Infoblox
INFOBLOX_OPTS = {
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
    'max_results': QUERY_LIMIT,            # change from default
    'log_api_calls_as_info': False,
    'paging': True
}

# Annotation Options

COLUMNS = {
    "annotate_hostname": {
        "enabled": os.environ['ENABLE_HOSTNAME'],
        "annotationName": os.environ['HOSTNAME_ANNOTATION_NAME'],
        "infobloxName": "names"
    },
    "annotate_zone": {
        "enabled": os.environ['ENABLE_ZONE'],
        "annotationName": os.environ['ZONE_ANNOTATION_NAME'],
        "infobloxName": "zone"
    },
    "annotate_view": {
        "enabled": os.environ['ENABLE_NETWORK_VIEW'],
        "annotationName": os.environ['NETWORK_VIEW_ANNOTATION_NAME'],
        "infobloxName": "network_view"
    },
    "annotate_parent": {
        "enabled": os.environ['ENABLE_SUBNET'],
        "annotationName": os.environ['SUBNET_ANNOTATION_NAME'],
        "infobloxName": "network"
    },
    "annotate_extensible_attributes": {
        "enabled": os.environ['ENABLE_EA'],
        "annotationName": os.environ['EA_ANNOTATION_NAME'],
        "infobloxName": "extattrs",
        "overload": "on",
        "attrList" : json.loads(os.getenv('EA_LIST'))
    }
}

# Pigeon Messenger
PIGEON = Pigeon()
# Connect to infoblox
infoblox = Infoblox_Helper(opts=INFOBLOX_OPTS,pigeon=PIGEON)
# Connect to tetration   
tetration = Tetration_Helper(TETRATION_ENDPOINT, api_key=TETRATION_API_KEY, api_secret=TETRATION_API_SECRET,pigeon=PIGEON, options=TETRATION_OPTS, tenant_app_scope=TETRATION_TENANT_SCOPE_NAME)
# Boolean helper
BOOLEAN = Boolean_Helper()

# Debug function used for printing formatted dictionaries
def PrettyPrint(target):
    print json.dumps(target,sort_keys=True,indent=4)

def get_undocumented_inventory(columns):
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Getting undocumented hosts from tetration',
        'data' : {}
    })
    PIGEON.send()
    filters = []
    #for annotation in {k:v for k,v in COLUMNS.iteritems() if v["enabled"] == "on" }:
    for annotation in columns:
        filters.append({
            "type": "eq",
            "field": "user_" + annotation["annotationName"],
            "value": ""
        })
    tetration.GetInventory(filters)

def main():
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Starting tasks for infoblox host annotations',
        'data' : {}
    })
    PIGEON.send()
    columns = [COLUMNS[column] for column in COLUMNS if BOOLEAN.GetBoolean(COLUMNS[column]["enabled"]) ]
    while True:
        if len(columns) > 0:
            PIGEON.note.update({
                'status_code': 100,
                'message' : 'Retrieving next ' + str(QUERY_LIMIT) + ' undocumented hosts from tetration inventory',
                'data' : {}
            })
            PIGEON.send()
            get_undocumented_inventory(columns)
            PIGEON.note.update({
                'status_code': 100,
                'message' : 'Retrieving host information from infoblox',
                'data' : {}
            })
            PIGEON.send()
            host_list = infoblox.GetHost(tetration.inventory.pagedData)
            PIGEON.note.update({
                'status_code': 100,
                'message' : 'Creating tetration annotations for hosts',
                'data' : {}
            })
            PIGEON.send()
            tetration.AnnotateHosts(host_list,columns,ANNOTATION_CSV_FILENAME)
            if(tetration.inventory.hasNext is False):
                break
            time.sleep(2)
        else:
            PIGEON.note.update({
                'status_code': 300,
                'message' : 'No infoblox annotations enabled',
                'data' : {}
            })
            PIGEON.send()
            exit(0)
    PIGEON.note.update({
        'status_code': 200,
        'message' : 'All tasks completed for infoblox host annotations',
        'data' : {}
    })
    PIGEON.send()
if __name__ == "__main__":
    main()
