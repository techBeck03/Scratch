# ecohub Tetration/vCenter integration

This repository contains the code required to pull rich data about virtual machines from VMware vCenter and push that rich data as annotations to Cisco Tetration. 

**All of the scripts** in this repository rely on **environment variables** to pass arguments to each script.

The files in this repository are intended to build a Docker image for use with the ecohub project but can also be run indepently of Docker by setting temporary environment variables. Details about the Docker build and details about how to set local environment variables are in another document. This README only describes the intended behavior of the scripts in this repository.

## Supported Actions

This bundle of scripts is programmed to respond to **four** *actions* specified by the ecohub portal.

### TEST_CONNECTIVITY
`TEST_CONNECTIVITY` will verify the username, password and URL of the specified vCenter endpoint. It will also verify that the specified vCenter Datacenter exists. It returns pigeon messages with details of any connectivity errors or a success pigeon.

This action is executed by `eco_action.py` very simply:

```python
python test_connectivity.py
```

### RUN_INTEGRATION
 `RUN_INTEGRATION` retrieves rich data for each VM in the specified Datacenter and uploads that data as a CSV to Tetration. This involves several steps and is implemented in two different scripts, the first in PowerShell and the second in Python. 
 
 The PowerShell script interfaces only with vCenter (using PowerCLI) and the Pyton script interfaces only with Tetration. PowerCLI is an easier way to interface with vCenter but there is not a PowerShell SDK for Tetration.

 1. Get-Inventory.ps1 retrieves all *requested* information (the fields to retrieve can be controlled by environment variables) from vCenter and saves that inventory data as a local variable.
 2. Get-Inventory.ps1 looks to see if there is already an inventory CSV file in `/private` (or the local directory if the `/private` directory does not exist). If the inventory file exists, the script performs a diff and saves that diff as an annotations CSV to be uploaded later. If the inventory does not exist, it saves **all** of the requested information as an annotations CSV to be uploaded later.
 3. Get-Inventory.ps1 saves the data collected in step 1 as the new inventory baseline CSV in the `/private` directory to be retrieved next time this script is run.
 4. upload_annotations.py takes the annotations CSV file created by the script above and uploads it to Tetration. This is only done in Python to avoid having to code a Tetration client in PowerShell.

 This action is executed by `eco_action.py` like this:

```linux
pwsh Get-Inventory.ps1
python upload_annotations.py
```

### CLEAR_CACHE
`CLEAR_CACHE` erases any history that the *RUN_INTEGRATION* action has been performed. All `txt` and `csv` files are removed from the `/private` directory.

```python
for file in glob.glob("/private/*.txt"):
    os.remove(file)
for file in glob.glob("/private/*.csv"):
    os.remove(file)
```

### FETCH_ITEMS
To make it easier on the user, this integration can retrieve a list of datacenters that are available to the supplied credentials. This allows ecohub to show VMware Datacenter names as a dropdown list rather than have the user type the name manually.

Fetching items is handled by the script `fetch_items.py`, which looks at an environment variable to determine what should be fetched. Since the script only supports datacenters at this time, any other requested value will return a `400` error pigeon message.

## Environment Variables

All ecohub scripts use environment variables for their arguments. This section desribe those variables used for this integration.

**Required Variables**
- *TETRATION_API_KEY* (string) Tetration API key with the appropriate rights to run this Python script
- *TETRATION_API_SECRET* (string) Tetration API secret for the key with the appropriate rights to run this Python script
- *TETRATION_ENDPOINT* (string) DNS name of the Tetration endpoint such as https://example.com
- *VCENTER_HOST* (string) the DNS name or IP of the vCenter host (without HTTP/HTTPS prefix)
- *VCENTER_USER* (string) vCenter user account to use for the integration
- *VCENTER_PWD* (string) vCenter user password
- *VCENTER_DATACENTER* (string) name of the Datacenter whose VMs should be examined
- *ACTION* (string) the action that the eco script should perform such as `TEST_CONNECTIVITY`
- *ENABLE_VM_NAME* (string) set to either "on" or "off" to define if the user wants to retrieve VM Name. If it is set to "on" then you must also define the *VM_NAME_ANNOTATION_NAME* (string) variable to define the CSV column heading that will be used for VM Name.
- *ENABLE_VM_LOCATION* (string) set to either "on" or "off" to define if the user wants to retrieve VM location (host and cluster). If it is set to "on" then you must also define the *VM_LOCATION_ANNOTATION_NAME* (string) variable to define the CSV column heading that will be used for VM location.
- *ENABLE_VM_TAGS* (string) set to either "on" or "off" to define if the user wants to retrieve VMware VM tags. If it is set to "on" then you must also define the *VM_TAGS_ANNOTATION_NAME* (string) variable to define the CSV column heading that will be used for VM tags.
- *ENABLE_CUSTOM_ATTRIBUTES* (string) set to either "on" or "off" to define if the user wants to retrieve VM custom attributes. If it is set to "on" then you must also define the *CUSTOM_ATTRIBUTES_ANNOTATION_NAME* (string) variable to define the CSV column heading that will be used for VM custom attributes.
- *ENABLE_VM_NETWORK* (string) set to either "on" or "off" to define if the user wants to retrieve the VM network name. If it is set to "on" then you must also define the *VM_NETWORKS_ANNOTATION_NAME* (string) variable to define the CSV column heading that will be used for VM network name.
- *FETCH_TARGET* (string) defines the items(s) that should be retrieved (fetched). At this time, this integration can only fetch Datacenter names, so the only supported value here is `DATACENTERS`. This variable is really only *required* when the `ACTION` environment variable is set to `FETCH_ITEMS`.

**Optional Arguments**
There is only one optional environment variable for this script.
- *DEBUG* (optional boolean) if specified, the output from the container will be formatted JSON with indents to be more human-readable

## Helper Scripts

### Get-DockerCommand.ps1

The most useful helper script in this repository, `Get-DockerCommand.ps1` will read a list of environment variables from `env.json` and:

1. Display all of the commands required to set all of those as temporary environment variables in Linux. It's easy to copy this output and paste it into a Linux console to make development and testing easier.
2. Display the Docker command that is required run this container (assuming the image is built and available on the local machine).
3. Copy the above Docker command to the clipboard.
4. Set all of the environment variables as temporary environment variables in the local PowerShell console. That really helps with local development and debug.

### download_annotations.py

This script just downloads the annotations CSV from Tetration. It helps having a script to do this as its faster than going through the GUI.