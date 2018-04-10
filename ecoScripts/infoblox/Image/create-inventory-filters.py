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
UNKNOWN_SUBNETS = []
# Read in environment variables
KNOWN_SUBNETS_CSV = '/private/known_subnets.csv'
UNKNOWN_SUBNETS_CSV = '/public/unknown_subnets.csv'
FILTER_CSV_FILENAME ='/private/inventory_filters.csv'
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
    'wapi_version': '2.2',
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
    if os.path.isfile(KNOWN_SUBNETS_CSV):
        with open(KNOWN_SUBNETS_CSV) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                known_subnets.append(row["subnet"])
        tetration.AddSubnets(known_subnets)

def update_subnets():
    with open(KNOWN_SUBNETS_CSV, 'w') as csvfile:
        fieldnames = ['subnet']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for subnet in tetration.subnets:
            writer.writerow({'subnet': subnet.__str__()})

    with open(UNKNOWN_SUBNETS_CSV, 'w') as csvfile:
        fieldnames = ['subnet']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for subnet in list(set(UNKNOWN_SUBNETS)):
            writer.writerow({'subnet': subnet.__str__()})

def create_network_filters():
    filtered_hosts = []
    subnets = []
    for host in tetration.inventory.pagedData:
        if(not tetration.HasSubnetFilterForIp(host["ip"])):
            filtered_hosts.append(host)
    hosts = infoblox.GetHost(filtered_hosts)
    for host in hosts:
        subnets.append(host["network"])
    subnets = list(set(subnets))
    iblox_subnets = []
    tet_subnets = []
    for subnet in subnets:
        net = infoblox.GetSubnet(subnet)
        if "comment" in net[0]:
            iblox_subnets.append(net[0])
            tet_subnets.append(net[0]["network"])
        else:
            print "no comment in network"
            print net[0]["network"]
            UNKNOWN_SUBNETS.append(net[0]["network"])
    if len(iblox_subnets) > 0:
        tetration.CreateInventoryFilters(iblox_subnets)
        PIGEON.note.update({
            'status_code': 100,
            'message' : 'Pushing inventory filters to tetration',
            'data' : {}
        })
        PIGEON.send()
        tetration.PushInventoryFilters()
        tetration.AddSubnets(tet_subnets)
    else:
        PIGEON.note.update({
            'status_code': 100,
            'message' : 'No new subnets were found',
            'data' : {}
        })
        PIGEON.send()
    
def main():
    PIGEON.note.update({
        'status_code': 100,
        'message' : 'Starting tasks for infoblox inventory filters',
        'data' : {}
    })
    PIGEON.send()
    load_known_subnets()
    filters = [{
        "type": "contains",
        "field": "ip",
        "value": "."
    }]
    dimensions = ['ip']
    while True:
        PIGEON.note.update({
            'status_code': 100,
            'message' : 'Retrieving next ' + str(QUERY_LIMIT) + ' hosts from tetration inventory',
            'data' : {}
        })
        PIGEON.send()
        tetration.GetInventory(filters=filters,dimensions=dimensions)
        PIGEON.note.update({
            'status_code': 100,
            'message' : 'Creating inventory filters for observed networks',
            'data' : {}
        })
        PIGEON.send()
        create_network_filters()
        if(tetration.inventory.hasNext is False):
           break
    update_subnets()
    PIGEON.note.update({
        'status_code': 200,
        'message' : 'All tasks completed for infoblox inventory filters',
        'data' : {}
    })
    PIGEON.send()

if __name__ == "__main__":
    main()
