## ![alt text](https://github.com/techBeck03/Scratch/raw/master/ecoScripts/infoblox/icon.png "Logo") infoblox Annotations

### Overview
The infoblox integration works with the infoblox API to create annotations and inventory filters for your tetration deployment

***Annotations***

Annotations can be automatically generated for the following:
- Hostname
- DNS Zone
- Network Subnet
- Network View
- Extensible Attributes

Users can additionally select a tenant scope if using multi-tenancy

***Inventory Filters***

Inventory Filters can be pushed to tetration for a given App Scope and selectively set to scope restricted by the user.

### Behavior

#### Annotations

For each scheduled execution, the infoblox integration does the following:

1. Search the tetration inventory for any entries missing infoblox data
2. Query infoblox api for hosts found in step 1
3. Generate annotation csv and upload to the assigned tetration target cluster

#### Inventory Filters

Inventory filters can be generated using the controls within the Inventory Filters panel.  For each manual execution, the integration does the following:

1. Retrieve all hosts from tetration inventory and iterate
2. Check if host is in known cached subnet (if yes skip step 3)
3. Query infoblox api for the subnet each host belongs to:
    * Create inventory filter name based on infoblox 'Comment' field
    * Cache subnet definition to local file
4. Push inventory filters to assigned tetration target
 
The subnet cache file can be cleared using the `Clear Cache` button in the **clearFInventory Filters** panel of the configuration screen for the deployment.

<img src="https://github.com/techBeck03/Scratch/raw/master/ecoScripts/infoblox/clearInventoryCache.png" altText="Clear Cache" />

### Configuration

This section desribes how to configure a **deployment** of the vCenter Annotations image. There are two sections of configuration parameters.

#### Connection Parameters

- **vCenter** is the hostname or IP address for vCenter. Do not include HTTP or HTTPS in this field.
- **VC Username** specifies the login ID to be used each time this deployment runs. Use an account with read access to the vCenter and datacenter that chosen.
- **VC Password** is the login password for the username specified above. ecohub uses this password to connect to vCenter every time, this field must be updated if the user's password changes.
- **VC Datacenter** defines the vCenter Datacenter object from which to pull data. If information from more than one Datacenter is required, simply create multiple deployments of the vCenter image (more details below).

#### Annotation Options

- **VM Name** is a toggle switch that determines if the virtual machine name is included in annotations pushed to Tetration. When this toggle is on, the name of the annotation used for VM Name can be customized. More details are provided below.
- **VM Location** is a toggle switch that determines if the virtual machine location is included in annotations pushed to Tetration. VM location is specified in the format: `"host / cluster`". When this toggle is on, the name of the annotation used for VM Location can be customized. More details are provided below.
- **VM Tags** is a toggle switch that determines if the vSphere tag for a virtual machine is included in the annotations pushed to Tetration. A tag is a label that you can apply to objects in the vSphere inventory. When this toggle is on, the name of the annotation used for VM Location can be customized. More details are provided below.
- **Custom Attributes** is a toggle switch that determines if a virtual machine's custom attributes are included in the annotations pushed to Tetration. Custom attributes are key:value pairs that can be applied to virtual machines and searched upon in Tetration. When this toggle is on, the name of the annotation used for VM Location can be customized. More details are provided below.
- **VM Networks** is a toggle switch that determines if the names of the networks (port groups) for each virtual machine are included in the annotations pushed to Tetration. When this toggle is on, the name of the annotation used for the VM Networks can be customized. More details are provided below.

### Multiple Datacenters

Each deployment of the vCenter integration will only interact with one Datacenter in one vCenter endpoint. If information from multiple Datacenters is desired, the ecohub administrator can create multiple **deployments** from the same vCenter Annotations **image**. 

From the `IMAGES` tab in the ecohub dashboard, locate the vCenter Annotations installed image and click the `Deploy` icon. Repeat this process for each additional Datacenter required. Each deployment can be configured to pull information from a different Datacenter.

### Renaming attributes

Each parameter in the configuration screen that can be enabled/disabled can also be renamed. For example, the user might want to push `VM Name` to Tetration but search for it using a different parameter name (like `vm_name` or `machine name`) in the Tetration user interface.

It is recommended to maintain consistent names (labels) for annotations in Tetration as Tetration considers `VM Name` and `VM_Name` to be completely different and unrelated fields.