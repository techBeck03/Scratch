from tetpyclient import RestClient
import tetpyclient
import json
import os
import requests.packages.urllib3
import csv
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

class Pigeon(object):
    def __init__(self):
        self.letter = {
            "status_code" : 0,
            "message" : "",
            "data" : {}
        }

    def send(self):
        print json.dumps(self.letter)

      
class Tetration_Helper(object):
    class Inventory(object):
        offset = ''
        pagedData = None
        hasNext = False

    def __init__(self, endpoint, api_key, api_secret,pigeon, options):
        self.rc = RestClient(endpoint, api_key=api_key, api_secret=api_secret, verify=False)
        self.scopes = []
        self.pigeon = pigeon
        self.inventory = self.Inventory()
        self.filters = {}
        self.options = options

    def GetSearchDimensions(self):
        resp = self.rc.get('/inventory/search/dimensions')
        return resp.json()

    def GetApplicationScopes(self):
        resp = self.rc.get('/app_scopes')
        if resp.status_code != 200:
            self.pigeon.status_code = '403'
            self.pigeon.letter.update({
                'status_code': 403,
                'message' : 'Unable to get application scopes from tetration cluster',
                'data' : {}
            })
            self.pigeon.send()
            exit(0)

        else:
            self.scopes = resp.json()

    def GetInventory(self, filters):
        req_payload = {
            "filter": {
                "type": "or",
                "filters": filters
            },
            "limit": self.options["limit"],
            "offset": self.inventory.offset if self.inventory else ""
        }
        resp = self.rc.post('/inventory/search',json_body=json.dumps(req_payload))
        if resp.status_code != 200:
            self.pigeon.letter.update({
                'status_code': 403,
                'message' : 'Unable to get inventory from tetration cluster',
                'data' : {}
            })
            self.pigeon.send()
            exit(0)
        else:
            resp = resp.json()
            self.inventory.pagedData = resp['results']
            self.inventory.offset = resp['offset'] if 'offset' in resp else ''
            self.inventory.hasNext = True if self.inventory.offset else False
            return

    def CreateInventoryFilters(self,network_list):
        inventoryDict = {}
        appScopeName = os.getenv('APP_SCOPE_NAME',default='Default')
        try:
            appScopeId = [scope["id"] for scope in self.scopes if scope["name"] == appScopeName][0]
        except:
            self.pigeon.letter.update({
                'status_code': 403,
                'message' : 'Unable to find app scope id for: ' + appScopeName,
                'data' : {}
            })
            self.pigeon.send()
            exit(0)
        for row in network_list:
            if row['comment'] not in inventoryDict:
                inventoryDict[row['comment']] = {}
                inventoryDict[row['comment']]['app_scope_id'] = appScopeId
                inventoryDict[row['comment']]['name'] = row['comment']
                inventoryDict[row['comment']]['primary'] = os.getenv('SCOPE_RESTRICTED',default=False)
                inventoryDict[row['comment']]['query'] = {
                    "type" : "or",
                    "filters" : []
                }
            inventoryDict[row['comment']]['query']['filters'].append({
                "type": "subnet",
                "field": "ip",
                "value": row['network']
            })
        self.filters = inventoryDict
        return

    def PushInventoryFilters(self):
        for inventoryFilter in self.filters:
            req_payload = self.filters[inventoryFilter]
            resp = self.rc.post('/filters/inventories', json_body=json.dumps(req_payload))
        if resp.status_code != 200:
            self.pigeon.letter.update({
                'status_code': 403,
                'message' : 'Error pushing inventory filters to tetration cluster',
                'data' : {}
            })
            self.pigeon.send()
            exit(0)
        return

    def AnnotateHosts(self,hosts,columns,csvFile):
        with open(csvFile, "wb") as csv_file:
            fieldnames = ['IP','VRF']
            for column in columns:
                if column["infobloxName"] != 'extattrs':
                    fieldnames.extend([column["annotationName"]])
                else:
                    if column["overload"] == "on":
                        fieldnames.extend([column["annotationName"]])
                    else:
                        for attr in column["attrList"]:
                            fieldnames.extend([str(column["annotationName"]) + '-' + str(attr)])
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for host in hosts:
                host = host[0]
                hostDict = {}
                hostDict["IP"] = host["ip_address"]
                hostDict["VRF"] = [ tetHost["vrf_name"] for tetHost in self.inventory.pagedData if tetHost["ip"] == host["ip_address"] ][0]
                for column in columns:
                    if column["infobloxName"] == 'extattrs':
                        for attr in column["attrList"]:
                            if column["overload"] == "on":
                                if attr in host["extattrs"]:
                                    hostDict[column["annotationName"]] = str(attr) + '=' + str(host["extattrs"][attr]["value"]) + ';' if column["annotationName"] not in hostDict.keys() else hostDict[column["annotationName"]] + str(attr) + '=' + str(host["extattrs"][attr]["value"]) + ';'
                                else:
                                    hostDict[column["annotationName"]] = str(attr) + '=;' if column["annotationName"] not in hostDict.keys() else str(hostDict[column["annotationName"]]) + str(attr) + '=;'
                            else:
                                if attr in host["extattrs"]:
                                    hostDict[column["annotationName"] + '-' + attr] = host["extattrs"][attr]["value"]
                                else:
                                    hostDict[column["annotationName"] + '-' + attr] = ''
                    elif column["infobloxName"] == 'zone':
                        hostDict[column["annotationName"]] = '.'.join(",".join(host["names"]).split('.')[1:])
                    elif column["infobloxName"] == 'names':
                        hostDict[column["annotationName"]] = ",".join(host[column["infobloxName"]]).split('.')[0]
                    else:
                        hostDict[column["annotationName"]] = host[column["infobloxName"]]
                writer.writerow(hostDict)
        '''
        keys = ['IP', 'VRF']
        req_payload = [tetpyclient.MultiPartOption(key='X-Tetration-Key', val=keys), tetpyclient.MultiPartOption(key='X-Tetration-Oper', val='add')]
        resp = rc.upload(csvFile, '/assets/cmdb/upload', req_payload)
        if resp.status_code != 200:
            print("Error posting annotations to Tetration cluster")
        else:
            print("Successfully posted annotations to Tetration cluster")
        '''
