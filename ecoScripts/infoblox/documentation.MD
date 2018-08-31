## ![alt text](https://raw.githubusercontent.com/techBeck03/Scratch/runner/ecoScripts/infoblox/icon.png "Logo") infoblox Annotations

### Overview
The infoblox integration works with the infoblox API to create annotations and inventory filters for your tetration deployment

*Annotations*

Annotations can be automatically generated for the following:

- Hostname
- DNS Zone
- Network Subnet
- Network View
- Extensible Attributes

Users can additionally select a tenant scope if using multi-tenancy

*Inventory Filters*

Inventory Filters can be pushed to tetration for a given App Scope and selectively set to scope restricted by the user.

### Behavior

#### Annotations

For each scheduled execution, the infoblox integration does the following:

1. Search the tetration inventory for any hosts missing values for selected infoblox fields
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
 
The subnet cache file can be cleared using the `Clear Cache` button in the **Inventory Filters** panel of the configuration screen for the deployment.

![alt text](https://github.com/techBeck03/Scratch/raw/master/ecoScripts/infoblox/clearInventoryCache.png "Clear Cache")

### Configuration

This section desribes how to configure a **deployment** of the Infoblox image. There are three sections of configuration parameters.

#### Connection Parameters

- **Infoblox Hostname or IP** is the hostname or IP address for Infoblox. Do not include HTTP or HTTPS in this field.
- **Infoblox Username** specifies the login ID to be used each time this deployment runs. Use an account in the cloud-api-only group
- **Infoblox Password** is the login password for the username specified above. ecohub uses this password to connect to Infoblox every time, this field must be updated if the user's password changes.

#### Annotation Options

- **Tenant Scope Name** is the tetration scope associated with the generated user annotations.  These value are automatically fetched from the assigned tetration target.
- **Hostname** is a toggle switch that determines if the infoblox hostname is included in annotations pushed to Tetration. When this toggle is on, the name of the annotation used for Hostname can be customized. More details are provided below.
- **DNS Zone** is a toggle switch that determines if the infoblox dns zone is included in annotations pushed to Tetration. When this toggle is on, the name of the annotation used for DNS Zone can be customized. More details are provided below.
- **Network Subnet** s a toggle switch that determines if the infoblox subnet (x.x.x.x/xx) for a given host is included in annotations pushed to Tetration. When this toggle is on, the name of the annotation used for Network Subnet can be customized. More details are provided below.
- **Network View** s a toggle switch that determines if the infoblox network view for a given host is included in annotations pushed to Tetration. When this toggle is on, the name of the annotation used for Network View can be customized. More details are provided below.
- **Extensible Attributes** is a toggle switch that determines if the selected extensible attributes (fetched from infoblox) for each host are included in the annotations pushed to Tetration. When this toggle is on, the name of the annotation used for the Extensible Attributes can be customized. More details are provided below.

#### *Renaming attributes

Each parameter in the configuration screen that can be enabled/disabled can also be renamed. For example, the user might want to push `Hostname` to Tetration but search for it using a different parameter name (like `Infoblox Hostname` or `Infoblox_Hostname`) in the Tetration user interface.

It is recommended to maintain consistent names (labels) for annotations in Tetration as Tetration considers `Infoblox Hostname` and `Infoblox_Hostname` to be completely different and unrelated fields.

#### Inventory Filters
- **Scope Restricted** is a toggle switch indicating whether the generated inventory filters should be restricted to their ownership scope
- **App Scope ID** is a select list fetched from tetration containing all defined application scopes.  Only one application scope is currently supported.