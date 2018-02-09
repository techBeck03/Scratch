## ![alt text](https://github.com/techBeck03/Scratch/raw/master/ecoScripts/splunk/icon.png "Logo") Splunk Monitoring

### Overview
The Splunk integration is bi-directional and requires that the **Cisco Tetration Application** be installed from the ServiceNow store in addition to enabling this feature in ecohub. The benefits of this integration are:

- Tetration detects endpoints using flow analysis and pushes them to the SerivceNow CMDB. 
- Tetration-defined outliers and exceptions trigger trouble-ticket creation in ServiceNow.
- The ServiceNow CMDB can be used to augment the inventory annotations in Tetration.
- Tetration ADM results autment top-down config file based discovery of servicewatch.

The script will query tetration for any observed inventory endpoints and look for matching IPs or hostnames within your Infoblox inventory.