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
QUERY_LIMIT = 100
CSV_FILENAME = 'ecohub.csv'
# Tetration
TETRATION_ENDPOINT = os.environ['TETRATION_ENDPOINT']
TETRATION_API_KEY = os.environ['TETRATION_API_KEY']
TETRATION_API_SECRET = os.environ['TETRATION_API_SECRET']
TETRATION_OPTS = {
    'limit': QUERY_LIMIT
}

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
    'wapi_version': '2.5',
    'max_results': QUERY_LIMIT,            # change from default
    'log_api_calls_as_info': False,
    'paging': False
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
        "overload": os.environ['OVERLOAD_EA'],
        "attrList" : (os.getenv('EA_LIST')).split(',')
    }
}

# Pigeon Messenger
PIGEON = Pigeon()
# Connect to infoblox
#iblox = Infoblox_Client(INFOBLOX_OPTS,PIGEON)
infoblox = connector.Connector(INFOBLOX_OPTS)
# Connect to tetration   
tetration = Tetration_Helper(TETRATION_ENDPOINT, TETRATION_API_KEY, TETRATION_API_SECRET,PIGEON,TETRATION_OPTS)

# Debug function used for printing formatted dictionaries
def PrettyPrint(target):
    print json.dumps(target,sort_keys=True,indent=4)

def create_network_filters(params):
    # Get Scopes
    logger.info("Creating network filters")
    logger.debug("Getting application scopes from tetration")
    scopes = tetration.GetApplicationScopes(rc)
    # Get defined networks
    networks = []
    if params["type"].lower() == 'all':
        logger.info("Getting all networks from infoblox")
        networks = conn.get_object('network',{'network_view': params["view"]} if params["view"] != '' else None)
        if networks is None:
            logger.warning("No networks were found in network view: " + params["view"])
            return
        # Find networks with a comment defined
        network_list = [network for network in networks if 'comment' in network]
        # Create API Query for creating inventory filters
        logger.info("Creating tetration inventory filters from API")
        inventoryFilters = tetration.CreateInventoryFiltersFromApi(rc,scopes,network_list,params['apiParams'])
    else:
        with open(params["csvParams"]["filename"], "rb") as csvFile:
            reader = csv.DictReader(csvFile)
            for row in reader:
                logger.info("Getting network:" + row["Network"] + " from infoblox")
                networks.extend(conn.get_object('network',{'network': row["Network"], 'network_view': row["Network View"]}))
        network_list = [network for network in networks if 'comment' in network]
        logger.info("Creating inventory filters from networks in csv: " + params["csvParams"]["filename"])
        inventoryFilters = tetration.CreateInventoryFiltersFromApi(rc,scopes,params['apiParams'])
    # Push Filters to Tetration
    logger.info("Pushing filters to tetration")
    tetration.PushInventoryFilters(rc,inventoryFilters)
    logger.info("Filters successfully pushed to tetration")

def annotate_hosts(params):
    logger.info("Creating host annotations")
    hosts = []
    # Read hosts from networks listed in csv
    if params["type"] == 'csv':
        logger.info("Reading network list from csv:" + params["csvParams"]["importFilename"])
        with open(params["csvParams"]["importFilename"], "rb") as csvFile:
            reader = csv.DictReader(csvFile)
            for row in reader:
                # Read all hosts with a name defined
                hosts.extend(conn.get_object('ipv4address',{'network': row["Network"], 'names~': '.*', '_return_fields': 'network,network_view,names,ip_address,extattrs'}))
    else:
        logger.info("Getting all networks from infoblox for view:" + params["view"])
        networks = conn.get_object('network',{'network_view': params["view"]} if params["view"] != '' else None)
        for network in [network["network"] for network in networks]:
            # Read all hosts with a name defined
            host_obj = conn.get_object('ipv4address',{'network': network,'names~': '.*', '_return_fields': 'network,network_view,names,ip_address,extattrs'} if params["view"] == '' else {'network': network, 'names~': '.*', '_return_fields': 'network,network_view,names,ip_address,extattrs','network_view': params["view"]})
            if host_obj is not None:
                hosts.extend(host_obj)
    logger.info("Creating annotations for selected networks")
    tetration.AnnotateHosts(rc,hosts,params)
    logger.info("Host annotation updates complete")

def get_undocumented_inventory():
    PIGEON.letter.update({
        'status_code': 100,
        'message' : 'Getting undocumented hosts from tetration',
        'data' : {}
    })
    PIGEON.send()
    filters = []
    #for annotation in {k:v for k,v in COLUMNS.iteritems() if v["enabled"] == "on" }:
    for annotation in [COLUMNS[column] for column in COLUMNS if COLUMNS[column]["enabled"] == "on" ]:
        filters.append({
            "type": "eq",
            "field": "user_" + annotation["annotationName"],
            "value": ""
        })
    tetration.GetInventory(filters)

def get_infoblox_data():
    host_list = []
    for host in tetration.inventory.pagedData:
        host_list.append(infoblox.get_object('ipv4address',{'ip_address': host["ip"],'_return_fields': 'network,network_view,names,ip_address,extattrs'}))
        
    return [host for host in host_list if host != None]
    

def main():
    while True:
        get_undocumented_inventory()
        host_list = get_infoblox_data()
        tetration.AnnotateHosts(host_list,[COLUMNS[column] for column in COLUMNS if COLUMNS[column]["enabled"] == "on" ],CSV_FILENAME)
        # ibloxData = get_infoblox_data()
        #tetration.GetApplicationScopes()
        #PrettyPrint(tetration.scopes)
        if(tetration.inventory.hasNext == False):
            exit(0)
        time.sleep(2)

if __name__ == "__main__":
    main()
