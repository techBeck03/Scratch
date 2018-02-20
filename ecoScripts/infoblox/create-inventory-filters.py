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
# Read in environment variables
QUERY_LIMIT = 20
KNOWN_SUBNETS_CSV = 'known_subnets.csv'
FILTER_CSV_FILENAME ='inventory_filters.csv'
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

# Pigeon Messenger
PIGEON = Pigeon()
# Connect to infoblox
infoblox = Infoblox_Helper(opts=INFOBLOX_OPTS,pigeon=PIGEON)
# Connect to tetration   
tetration = Tetration_Helper(TETRATION_ENDPOINT, TETRATION_API_KEY, TETRATION_API_SECRET,PIGEON,TETRATION_OPTS)

# Debug function used for printing formatted dictionaries
def PrettyPrint(target):
    print json.dumps(target,sort_keys=True,indent=4)

def load_known_subnets():
    known_subnets = []
    with open(KNOWN_SUBNETS_CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            known_subnets.append(row["subnet"])
    infoblox.setSubnets(known_subnets)

def update_subnets():
    with open(KNOWN_SUBNETS_CSV, 'w') as csvfile:
        fieldnames = ['subnet']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for subnet in infoblox.subnets:
            writer.writerow({'subnet': subnet})


def create_network_filters():
    filtered_ips = []
    subnets = []
    #for ip in tetration.inventory.pagedData:
    #    print ip["ip"]
    hosts = infoblox.GetInfobloxHost(tetration.inventory.pagedData)
    for host in hosts:
        subnets.append(host["network"])
    infoblox.setSubnets(list(set(subnets)))
    

'''
def create_network_filters(params):
    # Get Scopes
    scopes = tetration.GetApplicationScopes()
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
'''

def main():
    load_known_subnets()
    filters = [{
        "type": "contains",
        "field": "ip",
        "value": "."
    }]
    dimensions = ['ip']
    while True:
        tetration.GetInventory(filters=filters,dimensions=dimensions)
        #PrettyPrint(tetration.inventory.pagedData)
        create_network_filters()
        if(tetration.inventory.hasNext is False):
           break
        time.sleep(20)
    update_subnets()

if __name__ == "__main__":
    main()
